""" Collection of classes for representing, viewing and viewing a
Fluka model, and converting it GDML. """

from __future__ import (absolute_import, print_function, division)

import collections
import os.path
import time
import cPickle
import warnings
import textwrap
import uuid
import itertools

import numpy as np
import antlr4
import pyg4ometry

import pyg4ometry.fluka.geometry
import pyg4ometry.fluka.vector
import pyg4ometry.fluka.parser
import pyg4ometry.fluka.materials

from . import FlukaParserVisitor
from . import FlukaParserListener


class Model(object):
    """Class for viewing Fluka geometry and converting to GDML.
    Preprocessing must be done by hand.

    fluka_g4_material_map is the closest thing to a converter for the materials
    there is here.  Provide a map between the material names as usedin the
    ASSIGNMA cards and your externally defined materials for use with your GDML,
    and the volumes will be written out with those materialrefs.

    """
    def __init__(self, filename, fluka_g4_material_map=None):
        self._filename = filename
        # get the syntax tree.
        tree, cards = (
            pyg4ometry.fluka.parser.get_geometry_ast_and_other_cards(filename)
        )
        self.bodies, self._body_freq_map = Model._bodies_from_tree(tree)
        self.regions = self._regions_from_tree(tree)
        materials = pyg4ometry.fluka.materials.get_region_material_strings(
            self.regions.keys(),
            cards
        )

        # Assign the materials if provided with a fluka->G4 material map.
        # Circular dependencies means we can't do this until after the regions
        # are defined: Material assignments depend on the order in which the
        # regions are defined, which we get from the region definitions, which
        # in turn nominally depend on the material assignments.  To get around
        # this we set the material to G4_Galactic at region initialisation and
        # then reassign immediately afterwards here.
        if fluka_g4_material_map:
            # Always set BLCKHOLE to None.  We always omit regions with material
            # BLCKHOLE.
            fluka_g4_material_map["BLCKHOLE"] = None
            for region_name, region in self.regions.iteritems():
                fluka_material = materials[region_name]
                try:
                    g4_material = fluka_g4_material_map[fluka_material]
                    region.material = g4_material
                except KeyError:
                    msg = ("Missing material \"{}\"from"
                           " Fluka->G4 material map!").format(fluka_material)
                    warnings.warn(msg)

        else: # If no material map, we still want to omit BLCKHOLE
            # regions from viewing/conversion.
            msg = '\n'.join(textwrap.wrap(
                "No Fluka->G4 material map provided.  All converted regions"
                " will be \"G4_Galactic\" by default, but BLCKHOLE regions"
                " will still be omitted from both conversion and viewing."))
            print(msg, '\n')

            for region_name, region in self.regions.iteritems():
                fluka_material = materials.get(region_name)
                if fluka_material == "BLCKHOLE":
                    fluka_material = None
                else:
                    fluka_material = "G4_Galactic"
                region.material = fluka_material

        # Initialiser the world volume:
        self._world_volume = pyg4ometry.fluka.geometry._gdml_world_volume(register=True)

    def _regions_from_tree(self, tree):
        """Get the region definitions from the tree.  Called in the
        initialiser and then never called again.

        """
        visitor = FlukaRegionVisitor(self.bodies)
        visitor.visit(tree)
        return visitor.regions

    def write_to_gdml(self, regions=None, out_path=None,
                      make_gmad=True, bounding_subtrahends=None,
                      just_bounding_box=False, survey=None, optimise=True):
        """Convert the region to GDML.  Returns the centre (in mm) of the GDML
                      bounding box in the original Fluka coordinate
                      system, which can be useful for placing the
                      geometry.

        Parameters
        ----------

        - regions: A name or list of names of regions to be
        converted to GDML.  By default, all regions will be converted.

        - out_path: Output path for file to be written to.  By default
        output file name is "./" + basename + ".gdml".

        - make_gmad: Generate a skeleton GMAD file pre-filled with
        references to corresponding the GDML file.

        - bounding_subtrahends: Iterable of Body instances to be
          subtracted from the bounding box, e.g. space for a beampipe.
          The case where the subtraction affects the bounding box
          extent is not tested.  Maybe it will give you what you
          expect, or maybe not.

        - just_bounding_box: Write only the bounding box.  This can be
          useful when trying to place this as external geometry.  If
          true, then write just the bounding box.  If a string, then
          just the bounding box with the single named region placed in
          it.  If an iterable of names, then place all of those named
          regions in the bounding box.

        - survey: Output from Model.survey().  This is used to place regions
          consisting of disconnected zones as individual volumes.
          This is desirable as G4 doesn't support unions of
          disconnected solids.  If True then it will be generated on
          the fly, which maybe fine for small geometries, but it's likely
          preferable to compute the survey separately once using the
          survey method, for the sake of speed.

        """
        # Make the mesh for the given regions.
        self._generate_mesh(regions, setclip=True,
                            optimise=optimise,
                            bounding_subtrahends=bounding_subtrahends,
                            just_bounding_box=just_bounding_box,
                            survey=survey, register=True)
        # If no path to write to provided, then generate one
        # automatically based on input file name.
        if out_path is None:
            out_path = ("./"
                        + os.path.basename(os.path.splitext(self._filename)[0])
                        + ".gdml")
        elif os.path.splitext(out_path)[1] != "gdml":
            out_path = os.path.splitext(out_path)[0] + ".gdml"
        out = pyg4ometry.gdml.Writer()

        pyg4ometry.geant4.registry.setWorld(self._world_volume.name)
        out.addDetector(pyg4ometry.geant4.registry)
        out.write(out_path)
        self._print_bounding_extent()
        print("Written GDML file: {}".format(out_path))

        if make_gmad is True:
            self._write_test_gmad(out_path)

        # world solid is perhaps a subtraction from a box, or a simple
        # box.  Either way, get that box, as it determines the extent
        # of our world.
        base_bounding_box = _get_world_volume_box(self._world_volume)
        info_out = {"origin": self._world_volume.centre,
                    "extent":
                    pyg4ometry.fluka.geometry.Extent.from_gdml_box(base_bounding_box)}
        return info_out

    def _print_bounding_extent(self):
        # When writing, print the extent, because this is useful
        # information when wanting to place it, which has to be done manually.
        lengths = _get_world_volume_dimensions(self._world_volume)
        msg = ("Bounding box has dimensions (in metres): "
               "({:.9f}, {:.9f}, {:.9f})\n").format(lengths.x / 1000,
                                                    lengths.y / 1000,
                                                    lengths.z / 1000)
        print(msg)

    def view(self, regions=None, setclip=True, optimise=False,
             bounding_subtrahends=None, just_bounding_box=False):
        """View the mesh for this model.

        Parameters
        ----------

        - regions: A name or list of names of regions to be viewed.
        By default, all regions will be viewed.

        - setclip: If True, will clip the bounding box to the extent
        of the geometry.  Setting it to False is useful for checking
        placements and as an optimisation--the mesh will only be
        generated once.  By default, the bounding box will be clipped.

        - bounding_subtrahends: iterable of Body instances to be
          subtracted from the bounding box, e.g. space for a beampipe.
          The case where the subtraction affects the bounding box
          extent is not tested.  Maybe it will give you what you
          expect, or maybe not.

        """
        world_mesh = self._generate_mesh(
            regions, setclip=setclip, optimise=optimise,
            bounding_subtrahends=bounding_subtrahends,
            just_bounding_box=just_bounding_box, register=False)
        viewer = pyg4ometry.vtk.Viewer()
        viewer.addPycsgMeshList(world_mesh)
        viewer.view()

    def _generate_mesh(self, region_names, setclip,
                       optimise, bounding_subtrahends,
                       register, just_bounding_box=False, survey=None):
        """This function has the side effect of recreating the world volume if
        the region_names requested are different to the ones already
        assigned to it and returns the relevant mesh.

        just_bounding_box is by default False, because it has no real
        purpose unless the returned mesh is used, which is only for
        visualisation.

        """
        self._add_regions_to_world_volume(regions=region_names,
                                          optimise=optimise,
                                          survey=survey,
                                          register=register)
        # If we are subtracting from the world box
        if bounding_subtrahends:
            self._subtract_from_world_volume(bounding_subtrahends)
        elif setclip:
            self._clip_world_volume()

        # Do we want to construct it with the full geometry within or
        # should be leave some volumes out?
        if just_bounding_box is False:
            return self._world_volume.pycsgmesh()
        # If it's true then we remove all daughterVolumes within.
        elif just_bounding_box is True:
            # 1st element of list return by pycsgmesh, I believe, is
            # always the bounding box.  Hopefully always.  I assume
            # so, anyway.
            world_mesh = self._world_volume.pycsgmesh()
            self._world_volume.daughterVolumes = []
            return [world_mesh[0]]
        # Else if just_bounding_box is the name of a region, then
        # remove all daughterVolumes that don't have that name.
        elif isinstance(just_bounding_box, basestring):
            self._world_volume.daughterVolumes = (
                [element for element in
                 self._world_volume.daughterVolumes
                 if element.name == just_bounding_box])
            return self._world_volume.pycsgmesh()
        # Else if we have a sequence of region names to keep in the
        # otherwise empty bounding box.
        else:
            try:
                self._world_volume.daughterVolumes = (
                    [region for region in
                     self._world_volume.daughterVolumes
                     if region.name in just_bounding_box])
                return self._world_volume.pycsgmesh()
            except TypeError:
                msg = ("unusable argument for just_bounding_box!")
                raise TypeError(msg)

    def _subtract_from_world_volume(self, subtrahends):
        """Nice pyfluka interface for subtracting from bounding boxes
        in pygdml.  We create an RPP out of the clipped bounding box
        and then subtract from it the subtrahends, which is defined in
        the unclipped geometry's coordinate system.

        This works by first getting the "true" centre of
        the geometry, from the unclipped extent.  As the clipped
        extent is always centred on zero, and the subtractee is always
        centred on zero, this gives us the required
        offset for the subtraction from the bounding RPP."""
        # Get the "true" unclipped extent of the solids in the world volume
        unclipped_extent = pyg4ometry.fluka.geometry.Extent.from_world_volume(
            self._world_volume)
        # The offset is -1 * the unclipped extent's centre.
        unclipped_centre = unclipped_extent.centre
        other_offset = -1 * unclipped_centre
        self._clip_world_volume()
        # Make an RPP out of the clipped bounding box.
        world_name = self._world_volume.solid.name
        # solids magically start having material attributes at the top-level so
        # we must pass the material correctly to the new subtraction solid.
        world_material = self._world_volume.material
        world_solid = self._world_volume.solid

        # Deal with the trailing floating points introduced somewhere
        # in pygdml that cause the box to be marginally too big:
        decimal_places = int((-1 * np.log10(pyg4ometry.fluka.geometry.LENGTH_SAFETY)))
        box_parameters = [-1 * world_solid.pX, world_solid.pX,
                          -1 * world_solid.pY, world_solid.pY,
                          -1 * world_solid.pZ, world_solid.pZ]
        box_parameters = [round(i, decimal_places) for i in box_parameters]
        world = pyg4ometry.fluka.geometry.RPP(world_name, box_parameters)
        # We make the subtraction a bit smaller just to be sure we
        # don't subract from a placed solid within, so safety='trim'.
        for subtrahend in subtrahends:
            if isinstance(subtrahend,
                          (pyg4ometry.fluka.geometry.InfiniteCylinder,
                           pyg4ometry.fluka.geometry.InfiniteHalfSpace,
                           pyg4ometry.fluka.geometry.InfiniteEllipticalCylinder)):
                raise TypeError("Subtrahends must be finite!")

            world = world.subtraction(subtrahend, safety="trim",
                                      other_offset=other_offset)
        self._world_volume.currentVolume = world.gdml_solid()
        self._world_volume.currentVolume.material = world_material

    def _clip_world_volume(self):
        self._world_volume.setClip()

    def _add_regions_to_world_volume(self, regions, optimise, register, survey):
        """Add the region or regions in region_names to the current
        world volume (self._world_volume).

        If regions is None:  do all regions
        If regions is a string:  do just that one region
        If regions is a list of strings:  do those
        If regions is a map of region names with zone numbers:  Do
        those regions but only the zones in the list.
        if a survey (of the form output by Model.survey()) is
        provided, then it will be used to place disjoint zones within
        regions as separate volumes, to ensure well-formed G4 geometry.

        """
        pyg4ometry.geant4.registry.clear()
        self._world_volume = pyg4ometry.fluka.geometry._gdml_world_volume(
            register=register)
        if regions is None: # add all regions by default.
            regions = self.regions.keys()
        # Else if regions is the name of a single region
        elif isinstance(regions, basestring):
            regions = [regions]
        # Else if we have a map of region names with lists of zone numbers
        elif isinstance(regions, dict):
            for region_name, zone_nos in regions.iteritems():
                region = self.regions[region_name]
                print("Adding region: \"{}\"  ...".format(region_name))
                if region.material is None: # omit BLCKHOLE
                    print("Omitting BLCKHOLE region \"{}\".".format(
                        region_name))
                    continue
                if survey is None:
                    region.add_to_volume(self._world_volume,
                                         optimise=optimise,
                                         zones=zone_nos,
                                         register=register)
                else:
                    # If true then we should generate connected_zones
                    # on the fly for each region, otherwise we should
                    # use the provided survey.
                    sets = (region.connected_zones
                            if survey is True
                            else survey[region_name]["connected_zones"])
                    for connected_set in sets:
                        # Place them as individual regions, but only
                        # those zones which have also been selected in
                        # the dictionary
                        common_sets = connected_set.intersection(zone_nos)
                        # If the intersection is empty, then we
                        # should not place anything,
                        if not common_sets:
                            continue
                        region.add_to_volume(self._world_volume,
                                             optimise=optimise,
                                             zones=common_sets,
                                             register=register)

            return
        # Add said regions
        for region_name in regions:
            region = self.regions[region_name]
            if region.material is None: # omit BLCKHOLE
                print("Omitting BLCKHOLE region \"{}\".".format(region_name))
                continue
            print("Adding region: \"{}\"  ...".format(region_name))

            if survey is None:
                region.add_to_volume(self._world_volume,
                                     optimise=optimise,
                                     register=register)
            else:
                # If true then we should generate connected_zones
                # on the fly for each region, otherwise we should
                # use the provided survey.
                sets = (region.connected_zones
                        if survey is True
                        else survey[region_name]["connected_zones"])
                for connected_set in sets:
                    region.add_to_volume(self._world_volume,
                                         optimise=optimise,
                                         zones=connected_set,
                                         register=register)

    def report_body_count(self):
        """Prints a count of all unique bodies by type which are used in
        region defintions.

        """
        body_and_count = self._body_freq_map.items()
        body_and_count.sort(key=lambda i: i[1], reverse=True)
        # Print result, with alignment.
        print("Bodies used in region definitions:")

        body_code_definitions = {
            "ARB": "Abitrary Convex Polyhedron",
            "BOX": "General Rectangular Parallelepiped",
            "ELL": "Elippsoid of Revolution",
            "PLA": "Generic Infinite Half-space",
            "QUA": "Generic Quadric",
            "RAW": "Right Angle Wedge",
            "RCC": "Right Circular Cylinder",
            "REC": "Right Ellitpical Cylinder",
            "RPP": "Rectangular Parallelepiped",
            "SPH": "Sphere",
            "TRC": "Truncated Right Angle Cone",
            "WED": "Right Angle Wedge",
            "XCC": "Infinite Circular Cylinder parallel to the x-axis",
            "XEC": "Infinite Elliptical Cylinder parallel to the x-axis",
            "XYP": "Infinite Half-space perpendicular to the z-axis",
            "XZP": "Infinite Half-space perpendicular to the y-axis",
            "YCC": "Infinite Circular Cylinder parallel to the y-axis",
            "YEC": "Infinite Elliptical Cylinder parallel to the y-axis",
            "YZP": "Infinite Half-space perpendicular to the x-axis",
            "ZCC": "Infinite Circular Cylinder parallel to the z-axis",
            "ZEC": "Infinite Elliptical Cylinder parallel to the z-axis"
        }

        for body, count in body_and_count:
            body_description = (
                body
                + " - "
                + body_code_definitions[body]).ljust(60, '.')
            print(body_description + str(count))

    @staticmethod
    def _bodies_from_tree(tree):
        """Return a tuple of bodies, region scale, and a count of bodies by
        type.

        """
        body_listener = FlukaBodyListener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(body_listener, tree)
        body_freq_map = body_listener.body_freq_map
        bodies = body_listener.bodies
        return bodies, body_freq_map

    def _write_test_gmad(self, gdml_path):
        """Write a simple gmad file corresponding corresponding to the input
        file's geometry with the correct GDML component length.

        """
        gmad_path = os.path.splitext(gdml_path)[0] + ".gmad"
        gdml_name = os.path.basename(gdml_path)

        with open(gmad_path, 'w') as gmad:
            lengths = _get_world_volume_dimensions(self._world_volume)
            diameter = max(lengths.x, lengths.y)

            # divide by 1000.0 to convert mm to metres.
            gmad.write("test_component: element, l={!r}*m,"
                       " geometryFile=\"gdml:./{}\","
                       " outerDiameter={}*m;\n".format(lengths.z / 1000.0,
                                                       gdml_name,
                                                       diameter / 1000.0))
            gmad.write('\n')
            gmad.write("component : line = (test_component);\n")
            gmad.write('\n')
            gmad.write("beam,  particle=\"e-\",\n"
                       "energy=1.5 * GeV,\n"
                       "X0=0.1*um;\n")
            gmad.write('\n')
            gmad.write("use, period=component;\n")
            gmad.write('\n')
            gmad.write("option, physicsList=\"em FTFP_BERT muon\",\n"
                       "checkOverlaps=1;\n")
            print("Written GMAD file: {}".format(gmad_path))

    def test_regions(self, pickle=None, regions=None, optimise=True):
        """Individually mesh each region and return dictionary of lists of
        good regions, bad regions, bad intersections, and bad
        subtractions.

        If a string is supplied for pickle, then the resulting dictionary will
        be written to file.

        """
        if regions is None:
            regions = self.regions
        elif isinstance(regions, basestring):
            regions = collections.OrderedDict(regions, self.regions[regions])
        # good regions, bad regions, bad subtractions, bad intersections
        output = {key:[] for key in ["good", "bad", "subs", "ints"]}
        number_of_regions = len(regions)
        start = time.time()
        for index, region_name in enumerate(regions):
            print("... Testing Region: %s" % region_name)
            try:
                self._generate_mesh(region_name,
                                    setclip=False,
                                    optimise=optimise,
                                    bounding_subtrahends=None,
                                    register=False)
                output["good"].append(region_name)
            except pyg4ometry.exceptions.NullMeshError as error:
                output["bad"].append(region_name)
                if isinstance(error.solid, pyg4ometry.geant4.solid.Subtraction):
                    output["subs"].append(region_name)
                elif isinstance(error.solid,
                                pyg4ometry.geant4.solid.Intersection):
                    output["ints"].append(region_name)
            print("Tested {0}/{1}.".format(index + 1, number_of_regions))
            print("Succeded: {}.  Failed: {} ({:.2%}).".format(
                len(output["good"]),
                len(output["bad"]),
                (len(output["good"])
                 / (len(output["good"]) + len(output["bad"])))))

        duration = (time.time() - start) / 60.0
        print(duration, "minutes since test begun.")
        output['time'] = duration

        if pickle:
            pickle_name = "./{}_diag.pickle".format(self._filename)
            with open(pickle_name, 'w') as pickle_file:
                cPickle.dump(output, pickle_file)
        return output

    def view_debug(self, region_name=None, do_all=False):
        """If region_name  is specified then view that in debug mode, else
        attempt to mesh each region in turn and view the first null
        mesh in debug mode, and then exit.  If do_all is not False
        then will not exit after the first null mesh, and will instead
        try to view all regions in turn.

        """
        if region_name is not None:
            self.regions[region_name].view_debug()
            return

        for region in self.regions.itervalues():
            try:
                region.gdml_solid.pycsgmesh()
            except pyg4ometry.exceptions.NullMeshError:
                print("Failed mesh @ region: {}.".format(region.name))
                print("Viewing region in debug mode ...")
                region.view_debug()
                if do_all is False:
                    break

    def survey(self, outpath=None, extents=True, connected_zones=True,
               optimised_extents=True):
        """Extents of every zone and the connected_zones of every region."""
        regions = {region_name: {"extents": {},
                                 "connected_zones": None}
                   for region_name in self.regions}
        for region_name, region in self.regions.iteritems():
            if connected_zones:
                regions[region_name]["connected_zones"] = list(
                    region.connected_zones(verbose=True))
            if extents:
                for zone_no, zone in enumerate(region.zones):
                    print("Meshing Region: {}, Zone: {} ...".format(region_name,
                                                                    zone_no))
                    regions[region_name]["extents"][zone_no] = zone.extent(
                        optimised_extents)
        regions["survey_options"] = {"connected_zones": connected_zones,
                                     "outpath": outpath,
                                     "extents": extents,
                                     "optimised_extents": optimised_extents}

        if outpath is None:
            outpath = "./{}_survey.pickle".format(
                os.path.basename(os.path.splitext(self._filename)[0]))
        with open(outpath, 'w') as pickle_file:
            cPickle.dump(regions, pickle_file)
        return regions

    def check_overlaps(self):
        """Checks for overlaps between regions.  Returned is a
        dictionary with region names and keys, and a dictionary of
        overlapping regions and the extent of the overlaps.

        """
        # a dictionary of dictionaries describing the overlaps between regions
        output = {region.name: {} for region in self}

        # Build up a cache of optimised booleans with corresponding extents.
        # {name: (boolean, extent)}
        booleans_and_extents = self._get_region_booleans_and_extents(True)
        # every combination of names
        name_pairs = itertools.product(self.regions, self.regions)
        for first, second in name_pairs:
            print("Checking for an overlap: {}, {}".format(first, second))
            # don't check for overlaps with self, this is a given.
            if first == second:
                continue
            # if x does (doesn't) overlap with y then y does
            # (doesn't) overlap with x.
            if first in output[second]:
                output[first][second] = output[second][first]
                continue

            # Check if the bounding boxes are overlapping, if they aren't, then
            # the solids can't be either.
            if not pyg4ometry.fluka.geometry.are_extents_overlapping(
                    booleans_and_extents[first][1],
                    booleans_and_extents[second][1]):
                output[first][second] = None
                continue

            # If we made it this far then we must do the intersection.
            print("Intersecting.")
            overlap = pyg4ometry.fluka.geometry.get_overlap(
                booleans_and_extents[first][0],
                booleans_and_extents[second][0])
            output[first][second] = overlap

        # Sanitise the output.  keep track of everything whilst doing
        # the overlap check because it allows for optimisations, but
        # I want to return the  meaningful output.  use .keys() because I'm
        # editing the dictionary as I go.  if x overlaps with y, then
        # an overlap is reported for x with y and y with x.  oh well.
        for region_name in output.keys():
            # delete those regions which overlap with nothing
            if not any(output[region_name].itervalues()):
                del output[region_name]
                continue
            # For regions that do overlap with something, delete
            # references to regions with which the region does not
            # overlap.
            for other_name in output[region_name].keys():
                overlap = output[region_name][other_name]
                if overlap is None:
                    del output[region_name][other_name]

        return output

    def __repr__(self):
        return "<Model: \"{}\">".format(self._filename)

    def __iter__(self):
        return self.regions.itervalues()

    def _get_region_booleans_and_extents(self, optimise):
        """Return the meshes and extents of all regions of this model."""
        out = {}
        for name, region in self.regions.iteritems():
            print("Evaluating region {}".format(name))
            boolean, extent = region.evaluate_with_extent(optimise)
            out[name] = (boolean, extent)
        return out


class FlukaBodyListener(FlukaParserListener.FlukaParserListener):
    """
    This class is for getting simple, declarative  information about
    the geometry model.  In no particular order:

    - Body definitions, including surrounding geometry directives
    - Stats like names and frequencies for body types and regions.

    """
    def __init__(self):
        self.bodies = dict()

        self.body_freq_map = dict()
        self.unique_body_names = set()
        self.used_bodies_by_type = list()

        self.transform_stack = []
        self.current_translat = None
        self.current_expansion = None

    def enterBodyDefSpaceDelim(self, ctx):
        # This is where we get the body definitions and instantiate
        # them with the relevant pyfuka.bodies classes.
        body_name = ctx.ID().getText()
        body_type = ctx.BodyCode().getText()
        body_parameters = FlukaBodyListener._get_floats(ctx)
        # Apply any expansions:
        body_parameters = self.apply_expansions(body_parameters)

        # Try and construct the body, if it's not implemented then warn
        try:
            body_constructor = getattr(pyg4ometry.fluka.geometry, body_type)
            body = body_constructor(body_name,
                                    body_parameters,
                                    self.transform_stack,
                                    self.current_translat)
            self.bodies[body_name] = body
        except (AttributeError, NotImplementedError):
            warnings.simplefilter('once', UserWarning)
            msg = ("\nBody type \"{}\" not supported.  All bodies"
                   " of this type will be omitted.  If bodies"
                   " of this type are used in regions, the"
                   " conversion will fail.").format(body_type)
            warnings.warn(msg)

    def enterUnaryExpression(self, ctx):
        body_name = ctx.ID().getText()
        # used, then record its name and type.
        if body_name not in self.unique_body_names:
            self.unique_body_names.add(body_name)
            body_type = type(self.bodies[body_name]).__name__
            self.used_bodies_by_type.append(body_type)

    def enterTranslat(self, ctx):
        translation = FlukaBodyListener._get_floats(ctx)
        self.current_translat = pyg4ometry.fluka.vector.Three(translation)

    def exitTranslat(self, ctx):
        self.current_translat = None

    def enterExpansion(self, ctx):
        self.current_expansion = float(ctx.Float().getText())

    def exitExpansion(self, ctx):
        self.current_expansion = None

    def apply_expansions(self, parameters):
        """
        Method for applying the current expansion to the parameters.

        """
        factor = self.current_expansion
        if factor is not None:
            return [factor * x for x in parameters]
        return parameters

    @staticmethod
    def _get_floats(ctx):
        '''
        Gets the Float tokens associated with the rule and returns
        them as an array of python floats.
        '''
        float_strings = [i.getText() for i in ctx.Float()]
        floats = map(float, float_strings)
        # Converting centimetres to millimetres!!!
        floats = [10 * x for x in floats]
        return floats

    def exitGeocards(self, ctx):
        # When we've finished walking the geometry, count the bodies.
        self.body_freq_map = collections.Counter(self.used_bodies_by_type)
        del self.used_bodies_by_type


class FlukaRegionVisitor(FlukaParserVisitor.FlukaParserVisitor):
    """
    A visitor class for accumulating the region definitions.  The body
    instances are provided at instatiation, and then these are used
    when traversing the tree to build up a dictionary of region name
    and pyg4ometry.fluka.geometry.Region instances.

    """
    def __init__(self, bodies):
        self.bodies = bodies
        self.regions = collections.OrderedDict()

    def visitSimpleRegion(self, ctx):
        # Simple in the sense that it consists of no unions of Zones.
        region_defn = self.visitChildren(ctx)
        # Build a zone from the list of bodies or single body:
        zone = [pyg4ometry.fluka.geometry.Zone(region_defn)]
        region_name = ctx.RegionName().getText()
        self.regions[region_name] = pyg4ometry.fluka.geometry.Region(region_name, zone)

    def visitComplexRegion(self, ctx):
        # Complex in the sense that it consists of the union of
        # multiple zones.

        # Get the list of tuples of operators and bodies/zones
        region_defn = self.visitChildren(ctx)
        # Construct zones out of these:
        zones = [pyg4ometry.fluka.geometry.Zone(defn) for defn in region_defn]
        region_name = ctx.RegionName().getText()
        region = pyg4ometry.fluka.geometry.Region(region_name, zones)
        self.regions[region_name] = region

    def visitUnaryAndBoolean(self, ctx):
        left_solid = self.visit(ctx.unaryExpression())
        right_solid = self.visit(ctx.expr())

        # If both are tuples (i.e. operator, body/zone pairs):
        if (isinstance(left_solid, tuple)
                and isinstance(right_solid, tuple)):
            return [left_solid, right_solid]
        elif (isinstance(left_solid, tuple)
              and isinstance(right_solid, list)):
            right_solid.append(left_solid)
            return right_solid
        else:
            raise RuntimeError("dunno what's going on here")

    def visitUnaryExpression(self, ctx):
        body_name = ctx.ID().getText()
        body = self.bodies[body_name]
        if ctx.Plus():
            return  ('+', body)
        elif ctx.Minus():
            return ('-', body)
        return None

    def visitUnaryAndSubZone(self, ctx):
        sub_zone = self.visit(ctx.subZone())
        expr = self.visit(ctx.expr())
        # If expr is already a list, append to it rather than building
        # up a series of nested lists.  This is to keep it flat, with
        # the only nesting occuring in Zones.
        if isinstance(expr, list):
            return [sub_zone] + expr
        return [sub_zone, expr]

    def visitSingleUnion(self, ctx):
        zone = [(self.visit(ctx.zone()))]
        return zone

    def visitMultipleUnion(self, ctx):
        # Get the zones:
        zones = [self.visit(zone) for zone in ctx.zone()]
        return zones

    def visitMultipleUnion2(self, ctx):
        # This rule exists because of the three ways of expressing a
        # union:
        # - | +x +y (union with nothing)
        # -   +x | +y (infix union operator)
        # - | +x | +y (infix union operator with leading union op)
        # The latter two are identical, hence this method simply calling
        # the other.
        return self.visitMultipleUnion(ctx)

    def visitSubZone(self, ctx):
        if ctx.Plus():
            operator = '+'
        elif ctx.Minus():
            operator = '-'
        solids = self.visit(ctx.expr())
        zone = pyg4ometry.fluka.geometry.Zone(solids)
        return (operator, zone)

def load_pickle(path):
    """
    Convenience function for loading pickle files.

    """
    with open(path, 'r') as file_object:
        unpickled = cPickle.load(file_object)
    return unpickled

def _get_world_volume_box(world_volume):
    bound = world_volume.solid # bounding box
    if isinstance(bound, pyg4ometry.geant4.solid.Subtraction):
        # get left most solid of tree, which is the Box from which all
        # else is subtracted.
        while isinstance(bound, pyg4ometry.geant4.solid.Subtraction):
            bound = bound.obj1
        return bound
    elif isinstance(bound, pyg4ometry.geant4.solid.Box):
        return bound
    raise ValueError("Malformed bounding box!")

def _get_world_volume_dimensions(world_volume):
    """Given a world volume, get the extents in x, y, and z.  This
    works for either a solid which is just a box, or has had an
    arbitrary number of subtractions from it."""
    box = _get_world_volume_box(world_volume)
    # Double because pX, pY, pZ are half-lengths for a pygdml.solid.Box.
    return pyg4ometry.fluka.vector.Three(2 * box.pX, 2 * box.pY, 2 * box.pZ)
