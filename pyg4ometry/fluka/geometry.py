""" A collection of classes for representing Fluka regions, zones, and bodies.

Note:  All units are in millimetres, c.f. centimetres in Fluka.

"""

from __future__ import (absolute_import, print_function, division)
import math
import uuid
import collections
import numpy as np
import networkx as nx
import itertools
import logging

import pyg4ometry
import pyg4ometry.transformation as trf
from pyg4ometry.fluka import vector

# Fractional tolerance when minimising solids.  Here have chosen this
# to be 5% for no particular reason.
SCALING_TOLERANCE = 0.05

# Minimum length safety between volumes to ensure no overlaps
LENGTH_SAFETY = 1e-6 # 1 nanometre

# Intersection/Union/Subtraction identity.
# Intersecting/unioning/subtracting with this will simply return the
# other body.  Used for accumulating.
_IDENTITY_TYPE = collections.namedtuple("_IDENTITY_TYPE", [])
_IDENTITY = _IDENTITY_TYPE()
del _IDENTITY_TYPE

_FLUKA_BOILERPLATE = (
"""TITLE
{}
GLOBAL        5000.0       0.0       0.0       0.0       1.0
DEFAULTS                                                              PRECISIO
BEAM         10000.0                                                  PROTON
GEOBEGIN                                                              COMBNAME
    0    0                   MC-CAD
"""
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Where does the meshing actually happen?  This matters because it is
# the source of all slowdown!
# 1. Visualisation.
# 2. Calculating extents, which are used for a multitude of things:
#   1. Solid minimisation for infinite or or very, very large bodies.
#      See _apply_extent methods.
#   2. Overlap checking.  Either via directly meshing the intersection
#      and checking for a null mesh, or checking whether or not the
#      bounding boxes overlap (not yet implemented).
#   3. Surveying.  Different parts of the model can be excluded based
#      on dimensional cuts in x, y and z.  The extents of the
#      constituents zones and regions must be found.
# For this reason it is necessary to cache the mesh.

class Body(object):
    """A class representing a body as defined in Fluka.
    get_body_as_gdml_solid() returns the body as a pyg4ometry.geant4.solid

    """

    def __init__(self, name, parameters, translation=None, transformation=None):
        self.name = name
        self.translation = translation
        self.transformation = transformation
        self._set_parameters(parameters)
        self._set_rotation_matrix(transformation)
        # The _is_omittable flag is set internally for a body if the body
        # is found to be omittable.  An ommittable body is one which can
        # be omitted without impacting the resulting boolean in any way.
        # This is True in two scenarios:
        # - Subtracting a body which doesn't overlap with what it is being
        # subtracted from.
        # - Intersecting a solid which completely overlaps with what it is
        # intersecting.
        # This flag should only be set when checking overlaps with the
        # /known/ resulting mesh for a given zone, either at _get_overlap,
        # when a redundant subtraction will be flagged via the
        # NullMeshError exception, or at _apply_extent, when any redundant
        # intersections can flagged up (in principle so could redundant
        # subtractions, but they will surely have already been caught when
        # _get_overlap is called).
        self._is_omittable = False

    def to_fluka_string(self):
        body_type = type(self).__name__
        return "{} {} {}".format(
            body_type,
            self.name, # / 10 because converting mm to cm.
            " ".join(str(value / 10) for value in self.parameters))

    def view(self, setclip=True):
        world_box = pyg4ometry.geant4.solid.Box("world_box",
                                                10000, 10000, 10000)
        world_volume = pygdml.Volume([0, 0, 0], [0, 0, 0], world_box,
                                     "world-volume", None,
                                     1, False, "G4_NITROUS_OXIDE")

        self.add_to_volume(world_volume)
        if setclip is True:
            world_volume.setClip()
        mesh = world_volume.pycsgmesh()
        viewer = pygdml.VtkViewer()
        viewer.addSource(mesh)
        viewer.view()

    def _apply_crude_scale(self, scale):
        self._is_omittable = False
        self._scale = scale

    def _apply_extent(self, extent):
        # Here handle any scaling/offset caclulation when given an
        # extent instance.  In some cases, an intersection will contribute
        # nothing to the resulting mesh.  If so, it is necessary to
        # set the _is_omittable flag to guarantee the correct
        # resultant solid.  Note: subtractions which
        # contribute nothing will be caught at _resize upon calling
        # _get_overlap.  This is because a redundant subtraction will
        # result in a null mesh, which is not the case with a
        # redundant intersection.
        pass

    def add_to_volume(self, mother_volume, register):
        """Add this body's solid to a volume."""
        # Convert the matrix to TB xyz:
        rotation_angles = trf.matrix2tbxyz(self.rotation)
        # Up to this point all rotations are active, which is OK
        # because so are boolean rotations.  However, volume rotations
        # are passive, so reverse the rotation:
        rotation_angles = trf.reverse(rotation_angles)
        body_lv = pyg4ometry.geant4.LogicalVolume(self.gdml_solid(),
                                                  "G4_Galactic",
                                                  "{}_lv".format(self.name),
                                                  register=register)
        body_pv = pyg4ometry.geant4.PhysicalVolume(rotation_angles,
                                                   self.centre(),
                                                   body_lv,
                                                   "{}_pv".format(self.name),
                                                   mother_volume,
                                                   register=register)

    def _resize(self, scale):
        """Return this instance bounded or extented according to the
        parameter "scale".

        """
        if isinstance(scale, (float, int)):
            self._apply_crude_scale(scale)
        elif isinstance(scale, Body):
            # In the try/except after this one, there are two possible
            # sources of NullMeshError.  We want to catch any possible
            # problem with meshing the scaling body first, as we
            # interpret NullMeshErrors in the second try/except as
            # redundant subtractions.  Mustn't confuse the two.
            # Assuming that the "crude" version is meshable, this
            # first try/except should never actually do anything, if
            # it does, then there's something wrong in this module.
            try:
                scale.gdml_solid().pycsgmesh()
            except pyg4ometry.exceptions.NullMeshError:
                msg = "Scaling body \"{}\" is not meshable!".format(scale.name)
                raise pyg4ometry.exceptions.NullMeshError(msg)
            try:
                extent = self._get_overlap(scale)
                self._apply_extent(extent)
            except pyg4ometry.exceptions.NullMeshError:
                # In this event, the subtraction is redundant one, so
                # we can omit it.
                # Redundant intersections naturally will not raise
                # NullMeshErrors, and are dealt with in the
                # _apply_extent methods.
                logger.debug("Omitting redundant subtraction of %s \"%s\"",
                             type(self).__name__, self.name)
                self._is_omittable = True
        else:
            raise TypeError("Unknown scale type: {}".format(type(scale)))
        return self

    def _extent(self):
        # Construct a world volume to place the solid in to be meshed.
        world_lv = _gdml_world_volume(register=False)
        self.add_to_volume(world_lv, register=False)
        return Extent.from_world_volume(world_lv)

    def _get_overlap(self, other):
        """
        Get the overlap of this solid with another, calculate the
        extent of the mesh, and return this.

        """
        intersection = self.intersection(other, safety="trim")
        extent = intersection._extent()
        return extent

    def intersection(self, other, safety=None, other_offset=None,
                     register=False):
        # Safety is the same for an intersection, either we seek to
        # shrink both solids or to extend both solids, usually the
        # desire is to shrink both.
        return self._do_boolean_op(other, pyg4ometry.geant4.solid.Intersection,
                                   safety, safety, other_offset, register)

    def subtraction(self, other, safety=None, other_offset=None,
                    register=False):
        # Safety is inverted for the first w.r.t the second.  When we
        # seek to extend the subtrahend, we want to trim the minuend,
        # and vice versa.t
        opposite_safety = {None: None,
                           "extend": "trim",
                           "trim": "extend"}[safety]
        return self._do_boolean_op(other, pyg4ometry.geant4.solid.Subtraction,
                                   opposite_safety, safety, other_offset,
                                   register)

    def union(self, other, safety=None, other_offset=None, register=False):
        return self._do_boolean_op(other, pyg4ometry.geant4.solid.Union,
                                   safety, safety, other_offset, register)

    def _do_boolean_op(self, other, op, safety1, safety2, offset, register):
        """ Do the boolean operation of self with other.  op is the boolean
        operation of choice.  safety1 is the safety of self (either
        None, "trim", or "extend"), and offset is ???
        """
        if other == _IDENTITY:
            return self
        if offset is None:
            offset = vector.Three(0, 0, 0)
        else: # Coerce an iterable to a vector
            offset = vector.Three(offset)
        relative_angles = self._get_relative_rotation(other)
        relative_translation = self._get_relative_translation(other) + offset
        relative_transformation = [relative_angles, relative_translation]

        out_name = _unique_name("boolean")
        out_solid = op(
            out_name, self.gdml_solid(safety1, register),
            other.gdml_solid(safety2, register), relative_transformation
        )
        out_centre = self.centre()
        out_rotation = self.rotation
        return Boolean(out_name, out_solid, out_centre, out_rotation)

    def _get_relative_rot_matrix(self, other):
        return self.rotation.T.dot(other.rotation)

    def _get_relative_translation(self, other):
        # In a boolean rotation, the first solid is centred on zero,
        # so to get the correct offset, subtract from the second the
        # first, and then rotate this offset with the rotation matrix.
        offset_vector = vector.Three((other.centre().x - self.centre().x),
                                     (other.centre().y - self.centre().y),
                                     (other.centre().z - self.centre().z))
        mat = self.rotation.T
        offset_vector = mat.dot(offset_vector).view(vector.Three)
        try:
            x = offset_vector[0][0]
            y = offset_vector[0][1]
            z = offset_vector[0][2]
        except IndexError:
            x = offset_vector.x
            y = offset_vector.y
            z = offset_vector.z
        return vector.Three(x, y, z)

    def _get_relative_rotation(self, other):
        # The first solid is unrotated in a boolean operation, so it
        # is in effect rotated by its inverse.  We apply this same
        # rotation to the second solid to get the correct relative
        # rotation.
        return trf.matrix2tbxyz(self._get_relative_rot_matrix(other))

    def _unique_boolean_name(self, other):
        """wrapper for uuid.  Solid names must begin with a letter in
        Geant4, so we simply prepend with an 'a'."""
        return "a" + str(uuid.uuid4())

    @staticmethod
    def _get_safety_addend(choice):
        # choice is either a string or None.
        if choice is None:
            return 0.0
        elif choice.lower() == "trim":
            return -LENGTH_SAFETY
        elif choice.lower() == "extend":
            return LENGTH_SAFETY
        else:
            raise ValueError("Unrecognised safety choice: {}".format(choice))

    def __repr__(self):
        return "<{}: \"{}\">".format(type(self).__name__, self.name)


class InfiniteCylinder(Body):
    def _apply_crude_scale(self, scale):
        self._offset = vector.Three(0, 0, 0)
        self._scale = scale

    def crude_extent(self):
        return max(map(abs, self.parameters))

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Tubs(_unique_name(self.name),
                                 0.0, self._radius + safety_addend,
                                 self._scale * 0.5,
                                 0.0, 2*math.pi)

class InfiniteEllipticalCylinder(Body):
    """Currently just for type checking XEC, YEC, and ZEC.  No functionality."""
    pass

class InfiniteHalfSpace(Body):
    def __init__(self, name, parameters, translation=None, transformation=None):
        self.name = name
        self.translation = translation
        self.transformation = transformation
        self._set_parameters(parameters)
        self._set_rotation_matrix(transformation)

    def _apply_crude_scale(self, scale):
        self._is_omittable = False
        self._offset = vector.Three(0, 0, 0)
        self._scale_x = scale
        self._scale_y = scale
        self._scale_z = scale

    def _set_rotation_matrix(self, transformation):
        self.rotation = np.matrix(np.identity(3))

    def crude_extent(self):
        return abs(max(self.parameters))

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Box(_unique_name(self.name),
                                0.5 * self._scale_x + safety_addend,
                                0.5 * self._scale_y + safety_addend,
                                0.5 * self._scale_z + safety_addend)

class RPP(Body):
    """An RPP is a rectangular parallelpiped (a cuboid). """
    def _set_parameters(self, parameters):
        parameter_names = ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']
        self.parameters = Parameters(zip(parameter_names, parameters))
        # Hidden versions of these parameters which can be reassigned
        self._x_min = self.parameters.x_min
        self._x_max = self.parameters.x_max
        self._y_min = self.parameters.y_min
        self._y_max = self.parameters.y_max
        self._z_min = self.parameters.z_min
        self._z_max = self.parameters.z_max

        if (self.parameters.x_min > self.parameters.x_max
                or self.parameters.y_min > self.parameters.y_max
                or self.parameters.z_min > self.parameters.z_max):
            raise Warning("This RPP \"" + self.name + "\" has mins larger than "
                          "its maxes.\n It is ignored in Fluka but "
                          "won't be ignored here!")

    @classmethod
    def from_extent(cls, name, extent):
        return cls(name, [extent.lower.x, extent.upper.x,
                          extent.lower.y, extent.upper.y,
                          extent.lower.z, extent.upper.z])

    def _apply_crude_scale(self, scale):
        self._is_omittable = False
        self._x_min = self.parameters.x_min
        self._x_max = self.parameters.x_max
        self._y_min = self.parameters.y_min
        self._y_max = self.parameters.y_max
        self._z_min = self.parameters.z_min
        self._z_max = self.parameters.z_max

    def _check_omittable(self, extent):
        # Tests to check whether this RPP completely envelops the
        # extent.  If it does, then we can safely omit it.
        is_gt_in_x = (self.parameters.x_max + 2 * LENGTH_SAFETY > extent.upper.x
                      and not np.isclose(self.parameters.x_max,
                                         extent.upper.x))
        is_lt_in_x = (self.parameters.x_min - 2 * LENGTH_SAFETY < extent.lower.x
                      and not np.isclose(self.parameters.x_min,
                                         extent.lower.x))
        is_gt_in_y = (self.parameters.y_max + 2 * LENGTH_SAFETY > extent.upper.y
                      and not np.isclose(self.parameters.y_max,
                                         extent.upper.y))
        is_lt_in_y = (self.parameters.y_min - 2 * LENGTH_SAFETY < extent.lower.y
                      and not np.isclose(self.parameters.y_min,
                                         extent.lower.y))
        is_gt_in_z = (self.parameters.z_max + 2 * LENGTH_SAFETY > extent.upper.z
                      and not np.isclose(self.parameters.z_max,
                                         extent.upper.z))
        is_lt_in_z = (self.parameters.z_min - 2 * LENGTH_SAFETY < extent.lower.z
                      and not np.isclose(self.parameters.z_min,
                                         extent.lower.z))
        return (is_gt_in_x and is_lt_in_x
                and is_gt_in_y and is_lt_in_y
                and is_gt_in_z and is_lt_in_z)


    def _apply_extent(self, extent):
        self._is_omittable = self._check_omittable(extent)
        if self._is_omittable:
            return

        # Then we can't omit it, but maybe we can shrink it:

        # Calculate the tolerances for lower bounds:
        x_bound_lower = extent.lower.x - abs(SCALING_TOLERANCE * extent.lower.x)
        y_bound_lower = extent.lower.y - abs(SCALING_TOLERANCE * extent.lower.y)
        z_bound_lower = extent.lower.z - abs(SCALING_TOLERANCE * extent.lower.z)
        # and for the upper bounds:
        x_bound_upper = extent.upper.x + abs(SCALING_TOLERANCE * extent.upper.x)
        y_bound_upper = extent.upper.y + abs(SCALING_TOLERANCE * extent.upper.y)
        z_bound_upper = extent.upper.z + abs(SCALING_TOLERANCE * extent.upper.z)

        # If outside of tolerances, then assign to those tolerances.
        # Lower bounds:
        if self.parameters.x_min < x_bound_lower:
            self._x_min = x_bound_lower
        if self.parameters.y_min < y_bound_lower:
            self._y_min = y_bound_lower
        if self.parameters.z_min < z_bound_lower:
            self._z_min = z_bound_lower
        # Upper bounds::
        if self.parameters.x_max > x_bound_upper:
            self._x_max = x_bound_upper
        if self.parameters.y_max > y_bound_upper:
            self._y_max = y_bound_upper
        if self.parameters.z_max > z_bound_upper:
            self._z_max = z_bound_upper

    def centre(self):
        """Centre of the equivalent GDML solid."""
        return 0.5 * vector.Three(self._x_min + self._x_max,
                                  self._y_min + self._y_max,
                                  self._z_min + self._z_max)

    def _set_rotation_matrix(self, transformation):
        self.rotation = np.matrix(np.identity(3))

    def crude_extent(self):
        return max([abs(self.parameters.x_min), abs(self.parameters.x_max),
                    abs(self.parameters.y_min), abs(self.parameters.y_max),
                    abs(self.parameters.z_min), abs(self.parameters.z_max),
                    self.parameters.x_max - self.parameters.x_min,
                    self.parameters.y_max - self.parameters.y_min,
                    self.parameters.z_max - self.parameters.z_min])


    def gdml_solid(self, length_safety=None, register=False):
        """Construct the equivalent pygdml Box from this body."""
        safety_addend = Body._get_safety_addend(length_safety)
        x_half_length = 0.5 * (self._x_max - self._x_min)
        y_half_length = 0.5 * (self._y_max - self._y_min)
        z_half_length = 0.5 * (self._z_max - self._z_min)
        return pyg4ometry.geant4.solid.Box(_unique_name(self.name),
                                x_half_length + safety_addend,
                                y_half_length + safety_addend,
                                z_half_length + safety_addend)


class SPH(Body):
    def _set_parameters(self, parameters):
        parameter_names = ['v_x', 'v_y', 'v_z', 'radius']
        self.parameters = Parameters(zip(parameter_names, parameters))

    def centre(self):
        return vector.Three(self.parameters.v_x,
                            self.parameters.v_y,
                            self.parameters.v_z)

    def _set_rotation_matrix(self, transformation):
        self.rotation = np.matrix(np.identity(3))

    def crude_extent(self):
        # Maximum possible extent won't be any more than 2 times the
        # largest parameter.
        return 2 * max(map(abs, self.parameters))

    def gdml_solid(self, length_safety=None, register=False):
        """Construct a solid, whole, GDML sphere from this."""
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Orb(_unique_name(self.name),
                                self.parameters.radius + safety_addend)


class RCC(Body):
    """Right-angled Circular Cylinder

    Parameters:
    v_(x,y,z) = coordinates of the centre of one of the circular planes
    faces
    h_(x,y,z) = components of vector pointing in the direction of the
    other plane face, with magnitude equal to the cylinder length.
    radius    = cylinder radius

    """
    def _set_parameters(self, parameters):
        parameter_names = ['v_x', 'v_y', 'v_z', 'h_x', 'h_y', 'h_z', 'radius']
        self.parameters = Parameters(zip(parameter_names, parameters))

        self.face_centre = vector.Three(self.parameters.v_x,
                                        self.parameters.v_y,
                                        self.parameters.v_z)
        self.direction = vector.Three(self.parameters.h_x,
                                      self.parameters.h_y,
                                      self.parameters.h_z)
        self.length = self.direction.length()
        self.radius = self.parameters.radius
        self._offset = vector.Three(0, 0, 0)

    def _apply_crude_scale(self, scale):
        self._offset = vector.Three(0, 0, 0)
        self._scale = self.length

    def centre(self):
        return (self._offset
                + self.face_centre
                + (0.5 * self.direction))

    def _set_rotation_matrix(self, transformation):
        initial = [0, 0, 1]
        final = -self.direction
        self.rotation = trf.matrix_from(initial, final)

    def crude_extent(self):
        centre_max = max(abs(vector.Three(self.parameters.v_x,
                                          self.parameters.v_y,
                                          self.parameters.v_z)))
        return centre_max + self.length

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Tubs(_unique_name(self.name),
                                 0.0,
                                 self.radius + safety_addend,
                                 self.length * 0.5 + safety_addend,
                                 0.0,
                                 2*math.pi)


class REC(Body):
    """
    NOT IMPLEMENTED

    Class representing the Right Elliptical Cylinder of Fluka.

    Parameters:
    face_centre_x : x-coordinate of the centre of one of the faces.
    face_centre_y : y-coordinate of the centre of one of the faces.
    face_centre_z : z-coordinate of the centre of one of the faces.

    to_other_face_x : x-component of the vector pointing from
                      face_centre to the other face.
    to_other_face_y : y-component of the vector pointing from
                      face_centre to the other face.
    to_other_face_z : z-component of the vector pointing from
                      face_centre to the other face.
    The length of the vector to_other_face is the length of the
    elliptical cylinder.

    semi_minor_x : x-component of the semi-minor axis.
    semi_minor_y : y-component of the semi-minor axis.
    semi_minor_z : z-component of the semi-minor axis.
    The length of the vector semi_minor is the length of the
    semi-minor axis.

    semi_major_x : x-component of the semi-major axis.
    semi_major_y : y-component of the semi-major axis.
    semi_major_z : z-component of the semi-major axis.
    The length of the vector semi_major is the length of the
    semi-major axis.
    """
    def __init__(self, name,
                 parameters,
                 translation=None,
                 transformation=None):
        raise NotImplementedError

    def _set_parameters(self, parameters):
        parameter_names = [
            "face_centre_x", "face_centre_y", "face_centre_z",
            "to_other_face_x", "to_other_face_y", "to_other_face_z",
            "semi_minor_x", "semi_minor_y", "semi_minor_z",
            "semi_major_x", "semi_major_y", "semi_major_z"]
        self.parameters = Parameters(zip(parameter_names, parameters))

    def centre(self):
        centre_x = (self.parameters.face_centre_x
                    + self.parameters.to_other_face_x * 0.5)
        centre_y = (self.parameters.face_centre_y
                    + self.parameters.to_other_face_y * 0.5)
        centre_z = (self.parameters.face_centre_z
                    + self.parameters.to_other_face_z * 0.5)

        return vector.Three(centre_x, centre_y, centre_z)

    def _set_rotation_matrix(self, transformation):
        pass

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        # EllipticalTube is defined in terms of half-lengths in x, y,
        # and z.  Choose semi_major to start in the positive y direction.
        semi_minor = np.linalg.norm([self.parameters.semi_minor_x,
                                     self.parameters.semi_minor_y,
                                     self.parameters.semi_minor_z])

        semi_major = np.linalg.norm([self.parameters.semi_major_x,
                                     self.parameters.semi_major_y,
                                     self.parameters.semi_major_z])

        length = np.linalg.norm([self.parameters.to_other_face_x,
                                 self.parameters.to_other_face_y,
                                 self.parameters.to_other_face_z])

        return pyg4ometry.geant4.solid.EllipticalTube(_unique_name(self.name),
                                           semi_minor + safety_addend,
                                           semi_major + safety_addend,
                                           length * 0.5 + safety_addend)


class TRC(Body):
    """Truncated Right-angled Cone.

    Parameters
    ----------

    centre_major_x: x-coordinate of the centre of the larger face.
    centre_major_y: y-coordinate of the centre of the larger face.
    centre_major_z: z-coordinate of the centre of the larger face.

    major_to_minor_x : x_coordinat of the vector pointing from the major
                       to minor face.
    major_to_minor_y : y_coordinator of the vector pointing from the major
                       to minor face.
    major_to_minor_z : z_coordinator of the vector pointing from the major
                       to minor face.
    The length of the major_to_minor vector is the length of the resulting
    cone.

    major_radius : radius of the larger face.
    minor_radius : radius of the smaller face.
    """
    def _set_parameters(self, parameters):
        parameter_names = [
            'centre_major_x', 'centre_major_y', 'centre_major_z',
            'major_to_minor_x', 'major_to_minor_y', 'major_to_minor_z',
            'major_radius', 'minor_radius'
        ]
        self.parameters = Parameters(zip(parameter_names, parameters))
        self.major_centre = vector.Three([self.parameters.centre_major_x,
                                          self.parameters.centre_major_y,
                                          self.parameters.centre_major_z])
        self.major_to_minor = vector.Three([self.parameters.major_to_minor_x,
                                            self.parameters.major_to_minor_y,
                                            self.parameters.major_to_minor_z])
        self.length = self.major_to_minor.length()
        self.major_radius = self.parameters.major_radius
        self.minor_radius = self.parameters.minor_radius

    def centre(self):
        return self.major_centre + 0.5 * self.major_to_minor

    def _set_rotation_matrix(self, transformation):
        # We choose in the as_gdml_solid method to place the major at
        # -z, and the major at +z, hence this choice of initial and
        # final vectors:
        initial = [0, 0, 1]
        final = self.major_to_minor
        self.rotation = trf.matrix_from(initial, final)

    def crude_extent(self):
        return max(abs(self.parameters.centre_major_x) + self.length,
                   abs(self.parameters.centre_major_y) + self.length,
                   abs(self.parameters.centre_major_z) + self.length,
                   self.parameters.minor_radius,
                   self.parameters.major_radius)

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        # The first face of pygdml.Cons is located at -z, and the
        # second at +z.  Here choose to put the major face at -z.
        return pyg4ometry.geant4.solid.Cons(_unique_name(self.name),
                                 0.0, self.major_radius + safety_addend,
                                 0.0, self.minor_radius + safety_addend,
                                 0.5 * self.length + safety_addend,
                                 0.0, 2*math.pi)


class XYP(InfiniteHalfSpace):
    """Infinite half space perpendicular to the z-axis."""
    def _set_parameters(self, parameters):
        parameter_names = ['v_z']
        self.parameters = Parameters(zip(parameter_names, parameters))

    def _apply_extent(self, extent):
        if (self.parameters.v_z - 2 * LENGTH_SAFETY > extent.upper.z
                and not np.isclose(self.parameters.v_z, extent.upper.z)):
            self._is_omittable = True
            logger.debug("Setting XYP \"{}\" omittable.".format(self.name))
            return
        self._offset = vector.Three(extent.centre.x,
                                    extent.centre.y,
                                    0.0)
        self._scale_x = extent.size.x * (SCALING_TOLERANCE + 1)
        self._scale_y = extent.size.y * (SCALING_TOLERANCE + 1)
        self._scale_z = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        # Choose the face at
        centre_x = 0.0
        centre_y = 0.0
        centre_z = self.parameters.v_z - (self._scale_z * 0.5)
        return self._offset + vector.Three(centre_x, centre_y, centre_z)


class XZP(InfiniteHalfSpace):
    """Infinite half space perpendicular to the y-axis."""
    def _set_parameters(self, parameters):
        parameter_names = ['v_y']
        self.parameters = Parameters(zip(parameter_names, parameters))

    def _apply_extent(self, extent):
        if (self.parameters.v_y - 2 * LENGTH_SAFETY > extent.upper.y
                and not np.isclose(self.parameters.v_y, extent.upper.y)):
            self._is_omittable = True
            logger.debug("Setting XZP \"{}\" omittable.".format(self.name))
            return
        self._offset = vector.Three(extent.centre.x,
                                    0.0,
                                    extent.centre.z)
        self._scale_x = extent.size.x * (SCALING_TOLERANCE + 1)
        self._scale_y = extent.size.y * (SCALING_TOLERANCE + 1)
        self._scale_z = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        centre_x = 0.0
        centre_y = self.parameters.v_y - (self._scale_y * 0.5)
        centre_z = 0.0
        return self._offset + vector.Three(centre_x, centre_y, centre_z)


class YZP(InfiniteHalfSpace):
    """Infinite half space perpendicular to the x-axis."""
    def _set_parameters(self, parameters):
        parameter_names = ['v_x']
        self.parameters = Parameters(zip(parameter_names, parameters))

    def _apply_extent(self, extent):
        if (self.parameters.v_x - 2 * LENGTH_SAFETY > extent.upper.x
                and not np.isclose(self.parameters.v_x, extent.upper.x)):
            self._is_omittable = True
            logger.debug("Setting YZP \"{}\" omittable.".format(self.name))
            return
        self._offset = vector.Three(0.0,
                                    extent.centre.y,
                                    extent.centre.z)
        self._scale_x = extent.size.x * (SCALING_TOLERANCE + 1)
        self._scale_y = extent.size.y * (SCALING_TOLERANCE + 1)
        self._scale_z = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        centre_x = self.parameters.v_x - (self._scale_x * 0.5)
        centre_y = 0.0
        centre_z = 0.0
        return self._offset + vector.Three(centre_x, centre_y, centre_z)


class PLA(Body):
    """Generic infinite half-space.

    Parameters:
    x_direction (Hx) :: x-component of a vector of arbitrary length
                        perpendicular to the plane.  Pointing outside
                        of the space.
    y_direction (Hy) :: y-component of a vector of arbitrary length
                        perpendicular to the plane.  Pointing outside
                        of the space.
    z_direction (Hz) :: z-component of a vector of arbitrary length
                        perpendicular to the plane.  Pointing outside
                        of the space.
    x_position  (Vx) :: x-component of a point anywhere on the plane.
    y_position  (Vy) :: y-component of a point anywhere on the plane.
    z_position  (Vz) :: z-component of a point anywhere on the plane.
    """
    def _set_parameters(self, parameters):
        parameter_names = ["x_direction", "y_direction", "z_direction",
                           "x_position", "y_position", "z_position"]
        self.parameters = Parameters(zip(parameter_names, parameters))


        # Normalise the perpendicular vector:
        perpendicular = vector.Three([self.parameters.x_direction,
                                      self.parameters.y_direction,
                                      self.parameters.z_direction])
        self.perpendicular = (perpendicular
                              / np.linalg.norm(perpendicular))
        self.surface_point = vector.Three([self.parameters.x_position,
                                           self.parameters.y_position,
                                           self.parameters.z_position])
        self.surface_point = self._closest_point([0, 0, 0])

    def centre(self):
        # This is the centre of the underlying gdml solid (i.e. won't
        # be on the surface, but set backwards by half length scale's amount.
        centre = (self.surface_point
                  - (0.5 * self._scale * self.perpendicular.unit()))
        return centre

    def _apply_extent(self, extent):
        self.surface_point = self._closest_point(extent.centre)
        root3 = math.sqrt(3) # root3 to ensure that the box is big enough to
        # effectively act as a plane regardless of any rotations
        # present.  This is necessary because an extent is a box
        # without any rotation, but the PLA may in fact have rotation,
        # so to ensure the PLA is definitely big enough, make it have
        # the same dimensions as a sphere which completely contains
        # any rotation of the extent.
        self._scale = max(extent.size.x * (SCALING_TOLERANCE + 1) * root3,
                          extent.size.y * (SCALING_TOLERANCE + 1) * root3,
                          extent.size.z * (SCALING_TOLERANCE + 1) * root3)

    def _set_rotation_matrix(self, transformation):
        # Choose the face pointing in the direction of the positive
        # z-axis to make the face of the plane.
        initial = [0, 0, 1]
        final = self.perpendicular
        self.rotation = trf.matrix_from(initial, final)

    def crude_extent(self):
        return max(abs(self.surface_point.x),
                   abs(self.surface_point.y),
                   abs(self.surface_point.z))

    def _closest_point(self, point):
        """
        Return the point on the plane closest to the point provided.

        """
        # perpendicular distance from the point to the plane
        distance = np.dot((self.surface_point - point),
                          self.perpendicular)
        closest_point = point + distance * self.perpendicular
        assert (abs(np.dot(self.perpendicular,
                           closest_point - self.surface_point)) < 1e-6), (
                               "Point isn't on the plane!")
        return closest_point

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Box(_unique_name(self.name),
                                0.5 * self._scale + safety_addend,
                                0.5 * self._scale + safety_addend,
                                0.5 * self._scale + safety_addend)


class XCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to x-axis

    parameters:

    centre_y    -- y-coordinate of the centre of the cylinder
    centre_z    -- z-coordinate of the centre of the cylinder
    radius -- radius of the cylinder
    """
    def _set_parameters(self, parameters):
        parameter_names = ["centre_y", "centre_z", "radius"]
        self.parameters = Parameters(zip(parameter_names, parameters))
        self._radius = self.parameters.radius

    def _apply_extent(self, extent):
        self._offset = vector.Three(extent.centre.x,
                                    0.0,
                                    0.0)
        self._scale = extent.size.x * (SCALING_TOLERANCE + 1)

    def centre(self):
        return (self._offset
                + vector.Three(0.0,
                               self.parameters.centre_y,
                               self.parameters.centre_z))

    def _set_rotation_matrix(self, transformation):
        # Rotate pi/2 about the y-axis.
        self.rotation = np.matrix([[0, 0, -1],
                                   [0, 1, 0],
                                   [1, 0, 0]])


class YCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to y-axis

    parameters:

    centre_z    -- z-coordinate of the centre of the cylinder
    centre_x    -- x-coordinate of the centre of the cylinder
    radius -- radius of the cylinder
    """
    def _set_parameters(self, parameters):
        parameter_names = ["centre_z", "centre_x", "radius"]
        self.parameters = Parameters(zip(parameter_names, parameters))
        self._radius = self.parameters.radius

    def _apply_extent(self, extent):
        self._offset = vector.Three(0.0, extent.centre.y, 0.0)
        self._scale = extent.size.y * (SCALING_TOLERANCE + 1)

    def centre(self):
        return (self._offset
                + vector.Three(self.parameters.centre_x,
                               0.0,
                               self.parameters.centre_z))

    def _set_rotation_matrix(self, transformation):
        # Rotate by pi/2 about the x-axis.
        self.rotation = np.matrix([[1, 0, 0],
                                   [0, 0, 1],
                                   [0, -1, 0]])


class ZCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to z-axis

    parameters:

    centre_x    -- x-coordinate of the centre of the cylinder
    centre_y    -- y-coordinate of the centre of the cylinder
    radius -- radius of the cylinder
    """
    def _set_parameters(self, parameters):
        parameter_names = ["centre_x", "centre_y", "radius"]
        self.parameters = Parameters(zip(parameter_names, parameters))
        self._radius = self.parameters.radius

    def _apply_extent(self, extent):
        self._offset = vector.Three(0.0,
                                    0.0,
                                    extent.centre.z)
        self._scale = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        return (self._offset
                + vector.Three(self.parameters.centre_x,
                               self.parameters.centre_y,
                               0.0))

    def _set_rotation_matrix(self, transformation):
        self.rotation = np.matrix(np.identity(3))


class XEC(InfiniteEllipticalCylinder):
    """An infinite elliptical cylinder parallel to the x-axis.

    Parameters:

    centre_y (Ay) - y-coordinate of the centre of the ellipse face.
    centre_z (Az) - z-coordinate of the centre of the ellipse face.
    semi_axis_y (Ly) - semi-axis in the y-direction of the ellipse
    face.
    semi_axis_z (Lz) - semi-axis in the z-direction of the ellipse
    face.

    """
    def _set_parameters(self, parameters):
        parameter_names = ["centre_y", "centre_z", "semi_axis_y", "semi_axis_z"]
        self.parameters = Parameters(zip(parameter_names, parameters))

    def centre(self):
        return vector.Three(0.0,
                            self.parameters.centre_y,
                            self.parameters.centre_z)

    def _set_rotation_matrix(self, transformation):
        # Rotate pi/2 about the y-axis.
        self.rotation = np.matrix([[0, 0, -1],
                                   [0, 1, 0],
                                   [1, 0, 0]])

    def crude_extent(self):
        return max(map(abs, self.parameters))

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.EllipticalTube(
            _unique_name(self.name),
            self.parameters.semi_axis_z + safety_addend,
            self.parameters.semi_axis_y + safety_addend,
            0.5 * self._scale
        )


class YEC(InfiniteEllipticalCylinder):
    """An infinite elliptical cylinder parallel to the y-axis.

    Parameters:

    centre_z (Az) - z-coordinate of the centre of the ellipse face.
    centre_x (Ax) - x-coordinate of the centre of the ellipse face.
    semi_axis_z (Lz) - semi-axis in the z-direction of the ellipse face.
    semi_axis_x (Lx) - semi-axis in the x-direction of the ellipse face.

    """
    def _set_parameters(self, parameters):
        parameter_names = ["centre_z", "centre_x", "semi_axis_z", "semi_axis_x"]
        self.parameters = Parameters(zip(parameter_names, parameters))

    def centre(self):
        return vector.Three(self.parameters.centre_x,
                            0.0,
                            self.parameters.centre_z)

    def _set_rotation_matrix(self, transformation):
        # Rotate by pi/2 about the x-axis.
        self.rotation = np.matrix([[1, 0, 0],
                                   [0, 0, 1],
                                   [0, -1, 0]])

    def crude_extent(self):
        return max(map(abs, self.parameters))

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.EllipticalTube(
            _unique_name(self.name),
            self.parameters.semi_axis_x + safety_addend,
            self.parameters.semi_axis_z + safety_addend,
            0.5 * self._scale
        )


class ZEC(InfiniteEllipticalCylinder):
    """An infinite elliptical cylinder parallel to the z-axis.

    Parameters:

    centre_x (Ax) - x-coordinate of the centre of the ellipse face.
    centre_y (Ay) - y-coordinate of the centre of the ellipse face.
    semi_axis_x (Lx) - semi-axis in the x-direction of the ellipse face.
    semi_axis_y (Ly) - semi-axis in the y-direction of the ellipse face.
    """
    def _set_parameters(self, parameters):
        parameter_names = ["centre_x", "centre_y", "semi_axis_x", "semi_axis_y"]
        self.parameters = Parameters(zip(parameter_names, parameters))

    def centre(self):
        return vector.Three(self.parameters.centre_x,
                            self.parameters.centre_y,
                            0.0)

    def _set_rotation_matrix(self, transformation):
        self.rotation = np.matrix(np.identity(3))

    def crude_extent(self):
        return max(map(abs, self.parameters))

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.EllipticalTube(
            _unique_name(self.name),
            self.parameters.semi_axis_x + safety_addend,
            self.parameters.semi_axis_y + safety_addend,
            0.5 * self._scale
        )


class Region(object):
    """Class used for interfacing a Fluka region with a GDML volume.
    This class has the underlying pygdml volume payload, alongside its
    placement and rotation in the world volume, and a material.

    """
    def __init__(self, name, zones, material="G4_Galactic"):
        self.name = name
        self.material = material
        self.zones = zones

    @property
    def material(self):
        return self._material.name

    @material.setter
    def material(self, material):
        self._material = (
            pyg4ometry.geant4.Material.from_arbitrary_name(material))

    def view(self, zones=None, setclip=True, optimise=False):
        """
        View this single region.  If a null mesh is encountered, try
        the view_debug method to see the problematic boolean operation.

        """
        world_box = pyg4ometry.geant4.solid.Box("world_box",
                                                10000, 10000, 10000)
        world_volume = pygdml.Volume(
            [0, 0, 0], [0, 0, 0], world_box, "world-volume",
            None, 1, False, "G4_NITROUS_OXIDE"
        )
        solid = self.evaluate(zones, optimise=optimise)
        solid.add_to_volume(world_volume)
        if setclip is True:
            world_volume.setClip()
        mesh = world_volume.pycsgmesh()
        viewer = pygdml.VtkViewer()
        viewer.addSource(mesh)
        viewer.view()

    def add_to_volume(self, mother_volume, zones=None,
                      optimise=True,
                      register=False):
        """
        Basically for adding to a world volume.

        """
        boolean = self.evaluate(zones, optimise=optimise)
        # Convert the matrix to TB xyz:
        rotation_angles = trf.matrix2tbxyz(boolean.rotation)
        # Up to this point all rotations are active, which is OK
        # because so are boolean rotations.  However, volume rotations
        # are passive, so reverse the rotation:
        rotation_angles = trf.reverse(rotation_angles)
        # Give a more informative name when a subset of the zones are
        # selected to be placed.
        name = (self.name
                if zones is None
                else "{}_Zones_{}".format(self.name,
                                          "_".join([str(index) for
                                                    index in zones])))
        region_lv = pyg4ometry.geant4.LogicalVolume(
            boolean.gdml_solid(length_safety="trim", register=register),
            self._material, "{}_lv".format(name), register=register)
        region_pv = pyg4ometry.geant4.PhysicalVolume(rotation_angles,
                                                     boolean.centre(),
                                                     region_lv,
                                                     "{}_pv".format(name),
                                                     mother_volume,
                                                     register=register)

    def evaluate(self, zones=None, optimise=False):
        logger.debug("Evaluating Region \"%s\", optimisation=%s, zones=%s",
                     self.name, optimise, zones)
        zones = self._select_zones(zones)
        # Get the boolean solids from the zones:
        booleans = [zone.evaluate(optimise=optimise) for zone in zones]

        def accumulate_unions(first, second):
            # only add automatic length safety if the whole geometry
            # is optimised.  This is the (hopefully) consistent rule.
            safety = "trim" if optimise is True else None
            return first.union(second, safety=safety)
        out_boolean = reduce(accumulate_unions, booleans)
        return out_boolean

    def evaluate_with_extent(self, optimise):
        boolean = self.evaluate(optimise=optimise)
        extent = boolean._extent()
        return boolean, extent

    def _select_zones(self, zones):
        if zones is None:
            return self.zones
        try:
            return [self.zones[key] for key in zones]
        except TypeError:
            pass
        try:
            # if no __getitem__, or __iter__, then try using it as a
            # key directly:
            return [self.zones[zones]]
        except TypeError:
            msg = ("Unknown selection "
                   "provided for zones {}").format(type(zones))
            raise TypeError(msg)

    def extent(self, zones=None):
        boolean = self.evaluate(zones)
        return boolean._extent()

    def __repr__(self):
        return "<Region: \"{}\">".format(self.name)

    def __iter__(self):
        return iter(self.zones)

    def connected_zones(self, verbose=False):
        """Returns a generator of sets of connected zones.  If the solid A
        is connected to B, and B is connected to C, then A is
        connected to C.  This is useful because Geant4 does not
        strictly support disjoint unions.

        """
        n_zones = len(self.zones)
        tried = []
        # Build undirected graph, and add nodes corresponding to each zone.
        g = nx.Graph()
        g.add_nodes_from(range(n_zones))
        if n_zones == 1: # return here if there's only one zone.
            return nx.connected_components(g)
        # Build up a cache of booleans and extents for each zone.
        # format: {zone_index: (boolean, extent)}
        booleans_and_extents = self._get_zone_booleans_and_extents(True)

        # Loop over all combinations of zone numbers within this region
        for i, j in itertools.product(range(n_zones), range(n_zones)):
            # Trivially connected to self or tried this combination.
            if i == j or {i, j} in tried:
                continue
            tried.append({i, j})
            # Check if the bounding boxes overlap.  Cheaper than intersecting.
            if not are_extents_overlapping(booleans_and_extents[i][1],
                                           booleans_and_extents[j][1]):
                continue

            # Check if a path already exists.  Not sure how often this
            # arises but should at least occasionally save some time.
            if nx.has_path(g, i, j):
                continue

            # Finally: we must do the intersection op.
            if verbose:
                print("Intersecting zone {} with {}".format(i, j))
            if get_overlap(booleans_and_extents[i][0],
                           booleans_and_extents[j][0]) is not None:
                g.add_edge(i, j)
        return nx.connected_components(g)

    def _get_zone_booleans_and_extents(self, optimise):
        """Return the meshes and extents of all regions of this model."""
        out = {}
        for index, zone in enumerate(self.zones):
            print("Evaluating zone {}".format(index))
            boolean, extent = zone.evaluate_with_extent(optimise)
            out[index] = (boolean, extent)
        return out

    def bodies(self):
        """Get all the unique bodies instances that make up this Region."""
        unique_bodies = set()
        for zone in self.zones:
            zone_bodies = set(zone.bodies())
            unique_bodies = unique_bodies.union(zone_bodies)
        return unique_bodies

    def to_fluka_string(self):
        name_and_mystery_number = "{:13}5".format(self.name)
        zone_strings = [zone.to_fluka_string() for zone in self.zones]
        if len(zone_strings) == 1:
            return name_and_mystery_number + " {}".format(zone_strings[0])
        lines = []
        for i, string in enumerate(zone_strings):
            if i == 0:
                lines.append((name_and_mystery_number
                              + " | {}".format(zone_strings[0])))
                continue
            lines.append("               | {}".format(string))
        return "\n".join(lines)

    def to_fluka_inp(self, filename=None):
        filename = "{}.inp".format(self.name) if filename is None else filename
        with open(filename, 'w') as f:
            f.write(_FLUKA_BOILERPLATE.format(self.name))
            for body in self.bodies():
                f.write(body.to_fluka_string() + "\n")
            f.write("END\n")
            f.write(self.to_fluka_string() + "\n")
            f.write("END\n")
            f.write("GEOEND\n")

    def compare_extents(self):
        _, optimised_extent = self.evaluate_with_extent(True)
        _, unoptimised_extent = self.evaluate_with_extent(False)
        return optimised_extent, unoptimised_extent


class Zone(object):
    """Class representing a Zone (subregion delimited by '|'), i.e. a
    tract of space to be unioned with zero or more other zones.  A
    Zone may also have sub-zones, which in this implementation are
    simply nested Zone instances.

    Parameters
    ----------

    pairs: list of tuplestuples of the form (operator, Body) or
           (operator, SubZone), where operator is a string of the form
           '+' or '-'.

    """

    def __init__(self, pairs):
        self.contains = []
        self.excludes = []
        if isinstance(pairs, tuple):
            self._add_space(pairs[0], pairs[1])
        elif isinstance(pairs, list):
            for operator, body in pairs:
                self._add_space(operator, body)
        else:
            raise TypeError("Unknown pairs type: {}".format(type(pairs)))

        if not self.contains:
            raise TypeError(
                "Zone must always contain at least one body or subzone!!!")

    def _add_space(self, operator, body):
        """
        Add a body or SubZone to this region.

        """
        if not isinstance(body, (Body, Zone)):
            raise TypeError("Unknown body type: {}".format(type(body)))

        if operator == '+':
            self.contains.append(body)
        elif operator == '-':
            self.excludes.append(body)
        else:
            raise TypeError("Unknown operator: {}".format(operator))

    def __repr__(self):
        contains_bodies = ' '.join([('+{}[{}]').format(space.name,
                                                       type(space).__name__)
                                    for space in self.contains if
                                    isinstance(space, Body)])
        excludes_bodies = ' '.join([('-{}[{}]').format(space.name,
                                                       type(space).__name__)
                                    for space in self.excludes if
                                    isinstance(space, Body)])
        contains_zones = ' '.join(['\n+({})'.format(repr(space))
                                   for space in self.contains if
                                   isinstance(space, Zone)])
        excludes_zones = ' '.join(['\n-({})'.format(repr(space))
                                   for space in self.excludes if
                                   isinstance(space, Zone)])
        return "<Zone: {}{}{}{}>".format(contains_bodies,
                                         excludes_bodies,
                                         contains_zones,
                                         excludes_zones)

    def crude_extent(self):
        extent = 0.0
        for body in self.contains + self.excludes:
            extent = max(extent, body.crude_extent())
        return extent

    def view(self, setclip=True, optimise=False):
        self.evaluate(optimise=optimise).view(setclip=setclip)

    def view_compare_optimisation(self, setclip=True):
        world_box = pyg4ometry.geant4.solid.Box("world_box",
                                                10000, 10000, 10000)
        world_volume = pygdml.Volume(
            [0, 0, 0], [0, 0, 0], world_box, "world-volume",
            None, 1, False, "G4_NITROUS_OXIDE"
        )
        optimised = self.evaluate(optimise=True)
        unoptimised = self.evaluate(optimise=False)
        optimised.add_to_volume(world_volume)
        unoptimised.add_to_volume(world_volume)

        if setclip is True:
            world_volume.setClip()

        mesh = world_volume.pycsgmesh()
        viewer = pygdml.VtkViewer()
        viewer.addSource(mesh)
        viewer.view()

    def evaluate_with_extent(self, optimise):
        boolean = self.evaluate(optimise=optimise)
        extent = boolean._extent()
        return boolean, extent

    def evaluate(self, optimise=False):
        """
        Evaluate the zone, returning a Boolean instance with the
        appropriate optimisations, if any.

        """
        if optimise:
            return self._optimised_boolean()
        else:
            return self._crude_boolean()

    def _crude_boolean(self):
        scale = self.crude_extent() * 10.
        # Map the crude extents to the solids:
        self._map_extent_2_bodies(self.contains, scale)
        self._map_extent_2_bodies(self.excludes, scale)

        return self._accumulate(None) # Don't trim/extend.  Get the true mesh.

    def _optimised_boolean(self):
        out = self._crude_boolean()
        # Rescale the bodies and zones with the resulting mesh:
        self._map_extent_2_bodies(self.contains, out)

        def accumulate_intersections(first, second):
            return first.intersection(second, safety="trim")
        boolean_from_ints = reduce(accumulate_intersections, self.contains)

        self._map_extent_2_bodies(self.excludes, boolean_from_ints)

        return self._accumulate(0) # Top level zone so subzone_order = 0

    def _map_extent_2_bodies(self, bodies, extent):
        for body in bodies:
            if isinstance(body, Body):
                body._is_omittable = False
                body._resize(extent)
            elif isinstance(body, Zone):
                body._map_extent_2_bodies(body.contains, extent)
                body._map_extent_2_bodies(body.excludes, extent)

    def _accumulate(self, subzone_order):
        # Intersections on the top level should be trimmed, but
        # intersections nested with subtracted zones should be
        # extended.  These two maps and the subzone_order parameter
        # reflect this fact.
        if subzone_order is None: # don't do any trimming/extending
            safety_map = {"intersection": None, "subtraction": None}
        elif subzone_order % 2 == 0:
            safety_map = {"intersection": "trim", "subtraction": "extend"}
        elif subzone_order % 2 == 1:
            safety_map = {"intersection": "extend", "subtraction": "trim"}

        accumulated = _IDENTITY # An intersection with _IDENTITY is just self..

        # Remove all bodies which are omittable:
        filtered_contains = [body for body in self.contains
                             if (isinstance(body, Zone)
                                 or not body._is_omittable)]
        filtered_excludes = [body for body in self.excludes
                             if (isinstance(body, Zone)
                                 or not body._is_omittable)]

        for body in filtered_contains:
            if isinstance(body, Body):
                accumulated = body.intersection(
                    accumulated, safety_map['intersection'])
            elif isinstance(body, Zone):
                evaluated_zone = body._accumulate(subzone_order=subzone_order)
                accumulated = evaluated_zone.intersection(
                   accumulated, safety=safety_map['intersection'])

        for body in filtered_excludes:
            if isinstance(body, Body):
                accumulated = accumulated.subtraction(
                    body, safety_map['subtraction'])
            elif isinstance(body, Zone):
                # If we are doing a subtraction of a subzone, then we
                # would like to move to the next subzone order by
                # incrementing the current subzone order.  This in
                # effect flips the trimming and the extending.  This
                # is because we  wish to make subtractions solids
                # larger.  To do this we must extend any intersections
                # within, where we typically (for "flat" (i.e., no
                # subzones) geomtries) would instead slightly shrink
                # an intersection.
                next_subzone_order = (None if subzone_order is None
                                      else subzone_order + 1)
                # subtract from accumulated the accumulation of the
                # Zone instance.
                accumulated = accumulated.subtraction(
                    body._accumulate(subzone_order=next_subzone_order),
                    safety=safety_map['subtraction'])

        assert accumulated is not _IDENTITY
        return accumulated

    def extent(self, optimise=False):
        boolean = self.evaluate(optimise=optimise)
        return boolean._extent()

    def _flatten(self):
        out = []
        def _flatten_iter():
            for element in self:
                if isinstance(element, Zone):
                    out.extend(element._flatten())
                else:
                    out.append(element)
        _flatten_iter()
        return out

    def remove(self, body_name):
        """Recursively remove a body (by name) from this Zone instance."""
        # remove from contains:
        for index, element in enumerate(self.contains):
            if isinstance(element, Zone):
                element.remove(body_name)
            elif element.name == body_name:
                self.contains.pop(index)
        # remove from excludes:
        for index, element in enumerate(self.excludes):
            if isinstance(element, Zone):
                element.remove(body_name)
            elif element.name == body_name:
                self.excludes.pop(index)

    def __contains__(self, value):
        # A name of a body:
        flattened = self._flatten()
        return (value in [body.name for body in flattened]
                or value in flattened)

    def __iter__(self):
        return iter(self.contains + self.excludes)

    def bodies(self):
        """Return all the unique body instances associated with this zone"""
        return list(set(self._flatten()))

    def to_fluka_string(self):
        """Returns this Zone as a fluka input string."""
        bodies = []
        zones = []
        for part in self.contains:
            if isinstance(part, Body):
                bodies.append("+{}".format(part.name))
            if isinstance(part, Zone):
                 zones.append("+({}) ".format(part.to_fluka_string()))
        for part in self.excludes:
            if isinstance(part, Body):
                bodies.append("-{}".format(part.name))
            if isinstance(part, Zone):
                zones.append("-({})".format(part.to_fluka_string()))
        return " ".join(bodies + zones)
class Boolean(Body):
    """A Body is a solid with a centre, a rotation and a name.  This
    is used to represent combinations of bodies, e.g. as a result of
    evaluating a Region or Zone.  This is a Body which has no real
    FLUKA analogue, but is useful to form as an intermediary between
    FLUKA regions/zones and GDML volumes (a solid, plus a
    position, and a rotation)."""
    def __init__(self, name, solid, centre, rotation):
        self.name = name
        self._solid = solid
        self._centre = centre
        self.rotation = rotation

    def gdml_solid(self, *args, **kwargs):
        # args, kwargs are here purely to preserve interface with "true" bodies.
        return self._solid

    def centre(self):
        return self._centre

    def view_debug(self, first=None, second=None):
        world_box = pyg4ometry.geant4.solid.Box("world_box",
                                                10000, 10000, 10000)
        world_volume = pygdml.Volume([0, 0, 0], [0, 0, 0], world_box,
                                     "world-volume", None,
                                     1, False, "G4_NITROUS_OXIDE")
        self.add_to_volume(world_volume)
        try:
            world_volume.pycsgmesh()
            print("Mesh was successful.")
        except pyg4ometry.exceptions.NullMeshError as error:
            print(error.message)
            print("Debug:  Viewing consituent solids.")
            self._view_null_mesh(error, first, second, setclip=False)

    def _view_null_mesh(self, error, first, second, setclip=False):
        solid1 = error.solid.obj1
        solid2 = error.solid.obj2
        tra2 = error.solid.tra2

        world_box = pyg4ometry.geant4.solid.Box("world_box",
                                                10000, 10000, 10000)
        world_volume = pygdml.Volume(
            [0, 0, 0], [0, 0, 0], world_box, "world-volume",
            None, 1, False, "G4_NITROUS_OXIDE"
        )
        if (first is None and second is None
                or first is True and second is True):
            pygdml.Volume(
                [0, 0, 0], [0, 0, 0], solid1, solid1.name,
                world_volume, 1, False, "G4_NITROUS_OXIDE"
            )
            pygdml.Volume(
                trf.reverse(tra2[0]), tra2[1], solid2, solid2.name,
                world_volume, 1, False, "G4_NITROUS_OXIDE"
            )
        elif first is True and second is not True:
            pygdml.Volume(
                [0, 0, 0], [0, 0, 0], solid1, solid1.name,
                world_volume, 1, False, "G4_NITROUS_OXIDE"
            )
        elif second is True and first is not True:
            pygdml.Volume(
                trf.reverse(tra2[0]), tra2[1], solid2, solid2.name,
                world_volume, 1, False, "G4_NITROUS_OXIDE"
            )
        elif first is False and second is False:
            raise RuntimeError("Must select at least one"
                               " of the two solids to view")
        if setclip is True:
            world_volume.setClip()
        mesh = world_volume.pycsgmesh()
        viewer = pygdml.VtkViewer()
        viewer.addSource(mesh)
        viewer.view()

    def gdml_primitives(self):
        # quick and dirty..  revisit this at a later date.
        primitives = []
        def primitive_iter(solid):
            if isinstance(solid, (pyg4ometry.geant4.solid.Intersection,
                                  pyg4ometry.geant4.solid.Subtraction,
                                  pyg4ometry.geant4.solid.Union)):
                primitives.append(primitive_iter(solid.obj1))
                primitives.append(primitive_iter(solid.obj2))
            else:
                primitives.append(solid)
        primitive_iter(self.gdml_solid())
        return [primitive for primitive in primitives
                if primitive is not None]

class Parameters(object):
    # Kind of rubbishy class but sufficient for what it's used for (a
    # very rudimentary mutable record-type class)
    def __init__(self, parameters):
        self._fields = []
        for parameter, value in parameters:
            setattr(self, parameter, value)
            self._fields.append(parameter)

    def __repr__(self):
        out_string = ', '.join(['{}={}'.format(parameter,
                                               getattr(self, parameter))
                                for parameter in self._fields])
        return "<Parameters: ({})>".format(out_string)

    def __iter__(self):
        for field_name in self._fields:
            yield getattr(self, field_name)


class Extent(object):
    def __init__(self, lower, upper):
         # Decimal places for rounding
        decimal_places = int((-1 * np.log10(LENGTH_SAFETY)))
        lower = [round(i, decimal_places) for i in lower]
        upper = [round(i, decimal_places) for i in upper]
        self.lower = vector.Three(lower)
        self.upper = vector.Three(upper)
        self.size = self.upper - self.lower
        self.centre = self.upper - 0.5 * self.size

    @classmethod
    def from_gdml_box(cls, box):
        upper = vector.Three(box.pX, box.pY, box.pZ)
        lower = -1 * upper
        return cls(lower, upper)

    @classmethod
    def from_world_volume(cls, world_volume):
        """Construct an Extent object from a pygdml (world) volume instance. """
        mesh = world_volume.pycsgmesh()
        extent = pyg4ometry.geant4.mesh_extent(mesh)
        lower = vector.Three(extent[0].x, extent[0].y, extent[0].z)
        upper = vector.Three(extent[1].x, extent[1].y, extent[1].z)
        return cls(lower, upper)

    def is_close_to(self, other):
        return bool((np.isclose(self.lower, other.lower).all()
                     and np.isclose(self.upper, other.upper).all()))

    def within_length_safety_of(self, other):
        """Check if this extent differs from the other within a factor
        of 10 times LENGTH_SAFETY."""
        diff = self - other
        lower_is_lt_safety = [x <= 10 * LENGTH_SAFETY for x in abs(diff.lower)]
        upper_is_lt_safety = [x <= 10 * LENGTH_SAFETY for x in abs(diff.upper)]
        return all(lower_is_lt_safety) and all(upper_is_lt_safety)

    def __repr__(self):
        return ("<Extent: Lower({lower.x}, {lower.y}, {lower.z}),"
                " Upper({upper.x}, {upper.y}, {upper.z})>".format(
                    upper=self.upper, lower=self.lower))

    def __eq__(self, other):
        return self.lower == other.lower and self.upper == other.upper

    def __sub__(self, other):
        return Extent(self.lower - other.lower, self.upper - other.upper)
def are_extents_overlapping(first, second):
    """Check if two Extent instances are overlapping."""
    return not (first.upper.x < second.lower.x
                or first.lower.x > second.upper.x
                or first.upper.y < second.lower.y
                or first.lower.y > second.upper.y
                or first.upper.z < second.lower.z
                or first.lower.z > second.upper.z)

def get_overlap(first, second):
    """Return the extent of any overlapping region between the first
    and the second Region or Zone instance.  If there are no overlaps,
    then None is returned.

    Regions and Zones will be optimised before checking for overlaps.
    This is slow.  May change in the future as the parity between the
    meshes of optimised and unoptimised booleans becomes more assured.

    """
    # If the bounding boxes do not overlap, then the constituent solids
    # definitely do not overlap.
    # If the bounding boxes do overlap then the constituent solids
    # might overlap.

    # If we are dealing with any regions or zones, then get their
    # evaluated boolean forms.  otherwise assume they are just Body
    # instances (in general:  Boolean instances).
    if isinstance(first, (Region, Zone)):
        first = first.evaluate(optimise=True)
    if isinstance(second, (Region, Zone)):
        second = second.evaluate(optimise=True)
    try:
        return first.intersection(second, safety="trim")._extent()
    except pyg4ometry.exceptions.NullMeshError:
        return None

def _gdml_world_volume(register):
    """This method returns a world logical volume."""
    world_box = pyg4ometry.geant4.solid.Box(
        _unique_name("world_box"), 1, 1, 1,
        register=register)
    name = "the_world_lv_{}".format(uuid.uuid4())
    world_lv = pyg4ometry.geant4.LogicalVolume(
        world_box, "G4_Galactic", name, register=register)
    return world_lv

def _unique_name(name):
    "Mangle the name by appending it with a UUID."
    return "{}_{}".format(name, uuid.uuid4()).replace('-', '_')
