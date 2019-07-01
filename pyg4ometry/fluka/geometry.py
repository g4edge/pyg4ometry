""" A collection of classes for representing FLUKA regions, zones, and bodies.

Note:  All units are in millimetres, c.f. centimetres in FLUKA.

Note:  It's up to you to ensure your input consists of no null zones.

"""

from __future__ import (absolute_import, print_function, division)
import math
import uuid
import itertools
import logging

import numpy as np
import networkx as nx
import pygdml
import pygdml.transformation as trf

from pyfluka import vector

# Fractional tolerance when minimising solids.  Here have chosen this
# to be 50% for no reason other than that it works!  Smaller values
# introduce overlaps, and I don't know why...  Revisit this at some
# point to understand.
SCALING_TOLERANCE = 0.5

# Minimum length safety between volumes to ensure no overlaps
LENGTH_SAFETY = 1e-6 # 1 nanometre

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


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
    """A class representing a body as defined in FLUKA. gdml_solid()
    returns the body as a pygdml.solid.

    """

    def to_fluka_string(self):
        body_type = type(self).__name__
        return "{} {} {}".format(
            body_type,
            self.name, # / 10 because converting mm to cm.
            " ".join(str(value / 10) for value in self.parameters))

    def view(self, setclip=True):
        world_volume = make_world_volume("world", "G4_AIR")
        self.add_to_volume(world_volume)
        _mesh_and_view_world_volume(world_volume, setclip)

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
        pygdml.volume.Volume(rotation_angles, self.centre(), self.gdml_solid(),
                             self.name, volume, 1, False, "G4_Galactic")

    def _resize(self, scale):
        """Modify this instance bounded or extented according to the
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
                raise pygdml.solid.NullMeshError(msg)
            extent = get_overlap(self, scale)
            if extent is None:
                # In this event, the subtraction is redundant one, so
                # we can omit it.
                # Redundant intersections naturally will not raise
                # NullMeshErrors, and are dealt with in the
                # _apply_extent methods.
                logger.info("Omitting redundant subtraction of %s \"%s\"",
                            type(self).__name__, self.name)
                self._is_omittable = True
            else:
                # _is_omittable may also be set inside:
                self._apply_extent(extent)
        else:
            raise TypeError("Unknown scale type: {}".format(type(scale)))

    def _extent(self):
        # Construct a world volume to place the solid in to be meshed.
        world_volume = make_world_volume("world", "G4_AIR")
        self.add_to_volume(world_volume)
        return Extent.from_world_volume(world_volume)

    def intersection(self, other, safety=None, other_offset=None):
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
        if offset is None:
            offset = vector.Three(0, 0, 0)
        else: # Coerce an iterable to a vector
            offset = vector.Three(offset)
        relative_angles = self._get_relative_rotation(other)
        relative_translation = self._get_relative_translation(other) + offset
        relative_transformation = [relative_angles, relative_translation]
        out_name = self._unique_boolean_name()
        out_solid = op(out_name, self.gdml_solid(safety1),
                       other.gdml_solid(safety2), relative_transformation)
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

    def _unique_boolean_name(self):
        """wrapper for uuid.  Solid names must begin with a letter in
        Geant4, so we simply prepend with an 'a'."""
        return "a" + str(uuid.uuid4())

    def _unique_body_name(self):
        """Generate a name for a given body.  As a single FLUKA body
        may ultimately map to an arbitrary number of GDML solids, it
        is necessary that each name is unique.  We try here to
        maintain the reference to the original name slightly by
        appending to the original human-readable name.

        """
        return "{}_{}".format(self.name, uuid.uuid4())

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
        self._is_omittable = False
        self._offset = vector.Three(0, 0, 0)
        self._scale = scale

    def gdml_solid(self, length_safety=None):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Tubs(_unique_name(self.name),
                                 0.0, self._radius + safety_addend,
                                 self._scale * 0.5,
                                 0.0, 2*math.pi)


class InfiniteEllipticalCylinder(Body):
    """Currently just for type checking XEC, YEC, and ZEC.  No functionality."""
    pass


class InfiniteHalfSpace(Body):
    def _apply_crude_scale(self, scale):
        self._is_omittable = False
        self._offset = vector.Three(0, 0, 0)
        self._scale_x = scale
        self._scale_y = scale
        self._scale_z = scale

    def gdml_solid(self, length_safety=None):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Box(_unique_name(self.name),
                                0.5 * self._scale_x + safety_addend,
                                0.5 * self._scale_y + safety_addend,
                                0.5 * self._scale_z + safety_addend)

class RPP(Body):
    """An RPP is a rectangular parallelpiped (a cuboid). """
    def __init__(self, name, lower, upper, translation=None):
        self.name = name
        self.lower = vector.Three(lower)
        self.upper = vector.Three(upper)
        if translation is not None:
            self.lower += vector.Three(translation)
            self.upper += vector.Three(translation)
        # Hidden versions of these parameters which can be reassigned
        self._x_min = self.lower.x
        self._x_max = self.upper.x
        self._y_min = self.lower.y
        self._y_max = self.upper.y
        self._z_min = self.lower.z
        self._z_max = self.upper.z

        if (self.lower > self.upper).any():
            raise Warning("This RPP \"" + self.name + "\" has mins larger than "
                          "its maxes.\n It is ignored in FLUKA but "
                          "won't be ignored here!")

        self.rotation = np.identity(3)

    @classmethod
    def from_extent(cls, name, extent):
        return cls(name, extent.lower, extent.upper)

    def _apply_crude_scale(self, scale):
        # Reset the RPP.
        self._is_omittable = False
        self._x_min = self.lower.x
        self._x_max = self.upper.x
        self._y_min = self.lower.y
        self._y_max = self.upper.y
        self._z_min = self.lower.z
        self._z_max = self.upper.z

    def _check_omittable(self, extent):
        # Tests to check whether this RPP completely envelops the
        # extent.  If it does, then we can safely omit it.
        is_gt_in_x = (self.upper.x + 2 * LENGTH_SAFETY > extent.upper.x
                      and not np.isclose(self.upper.x, extent.upper.x))
        is_lt_in_x = (self.lower.x - 2 * LENGTH_SAFETY < extent.lower.x
                      and not np.isclose(self.lower.x, extent.lower.x))
        is_gt_in_y = (self.upper.y + 2 * LENGTH_SAFETY > extent.upper.y
                      and not np.isclose(self.upper.y, extent.upper.y))
        is_lt_in_y = (self.lower.y - 2 * LENGTH_SAFETY < extent.lower.y
                      and not np.isclose(self.lower.y, extent.lower.y))
        is_gt_in_z = (self.upper.z + 2 * LENGTH_SAFETY > extent.upper.z
                      and not np.isclose(self.upper.z, extent.upper.z))
        is_lt_in_z = (self.lower.z - 2 * LENGTH_SAFETY < extent.lower.z
                      and not np.isclose(self.lower.z, extent.lower.z))
        return (is_gt_in_x and is_lt_in_x
                and is_gt_in_y and is_lt_in_y
                and is_gt_in_z and is_lt_in_z)


    def _apply_extent(self, extent):
        self._is_omittable = self._check_omittable(extent)
        if self._is_omittable:
            logger.info("Setting RPP \"%s\" omittable.", self.name)
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
        if self.lower.x < x_bound_lower:
            self._x_min = x_bound_lower
        if self.lower.y < y_bound_lower:
            self._y_min = y_bound_lower
        if self.lower.z < z_bound_lower:
            self._z_min = z_bound_lower
        # Upper bounds::
        if self.upper.x > x_bound_upper:
            self._x_max = x_bound_upper
        if self.upper.y > y_bound_upper:
            self._y_max = y_bound_upper
        if self.upper.z > z_bound_upper:
            self._z_max = z_bound_upper

    def centre(self):
        """Centre of the equivalent GDML solid."""
        return 0.5 * vector.Three(self._x_min + self._x_max,
                                  self._y_min + self._y_max,
                                  self._z_min + self._z_max)

    def crude_extent(self):
        return max([abs(self.lower.x), abs(self.upper.x),
                    abs(self.lower.y), abs(self.upper.y),
                    abs(self.lower.z), abs(self.upper.z),
                    self.upper.x - self.lower.x,
                    self.upper.y - self.lower.y,
                    self.upper.z - self.lower.z])


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
    """A sphere"""
    def __init__(self, name, point, radius, translation=None):
        self.name = name
        self.point = vector.Three(point)
        if translation is not None:
            self.point += vector.Three(translation)
        self.radius = radius
        self.rotation = np.identity(3)

    def centre(self):
        return self.point

    def crude_extent(self):
        max_abs_centre = max([abs(c) for c in self.centre()])
        return max_abs_centre + self.radius

    def gdml_solid(self, length_safety=None, register=False):
        """Construct a solid, whole, GDML sphere from this."""
        safety_addend = Body._get_safety_addend(length_safety)
        return pygdml.solid.Orb(self._unique_body_name(),
                                self.radius + safety_addend)


class RCC(Body):
    """Right-angled Circular Cylinder

    Parameters:
    face_centre: centre of one of the faces
    direction: direction of cylinder from face_centre.  magnitude of
    this vector is the length of the cylidner.
    radius    = cylinder radius

    """
    def __init__(self, name, face_centre, direction, radius, translation=None):
        self.name = name
        self.face_centre = vector.Three(face_centre)
        if translation is not None:
            self.face_centre += vector.Three(translation)
        self.direction = vector.Three(direction)
        self.radius = radius
        initial = [0, 0, 1]
        final = -1 * self.direction
        self.rotation = trf.matrix_from(initial, final)

    def centre(self):
        return self.face_centre +0.5 * self.direction

    def crude_extent(self):
        centre_max = max(abs(self.face_centre))
        return centre_max + self.direction.length()

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Tubs(_unique_name(self.name),
                                 0.0,
                                 self.radius + safety_addend,
                                 self.direction.length() * 0.5 + safety_addend,
                                 0.0,
                                 2*math.pi)


class TRC(Body):
    """Truncated Right-angled Cone.

    centre: coordinates of the centre of the larger face.
    direction: coordinates of the vector pointing from major to minor.
    radius_major: radius of the larger face.
    radius_minor: radius of the smaller face.
    """
    def __init__(self, name, major_centre, direction, major_radius,
                 minor_radius, translation=None):
        self.name = name
        self.major_centre = vector.Three(major_centre)
        if translation is not None:
            self.major_centre += vector.Three(translation)
        self.direction = vector.Three(direction)
        self.major_radius = major_radius
        self.minor_radius = minor_radius

        # We choose in the as_gdml_solid method to place the major at
        # -z, and the major at +z:
        self.rotation = trf.matrix_from([0, 0, 1], self.direction)

    def centre(self):
        return self.major_centre + 0.5 * self.direction

    def crude_extent(self):
        return max(abs(self.major_centre.x) + self.direction.length(),
                   abs(self.major_centre.y) + self.direction.length(),
                   abs(self.major_centre.z) + self.direction.length(),
                   self.minor_radius,
                   self.major_radius)

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        # The first face of pygdml.Cons is located at -z, and the
        # second at +z.  Here choose to put the major face at -z.
        return pyg4ometry.geant4.solid.Cons(_unique_name(self.name),
                                 0.0, self.major_radius + safety_addend,
                                 0.0, self.minor_radius + safety_addend,
                                 0.5 * self.direction.length() + safety_addend,
                                 0.0, 2*math.pi)


class XYP(InfiniteHalfSpace):
    """Infinite half space perpendicular to the z-axis."""
    def __init__(self, name, z, translation=None):
        self.name = name
        self.z = z
        if translation is not None:
            self.z += translation[2]
        self.rotation = np.identity(3)

    def crude_extent(self):
        return abs(self.z)

    def _apply_extent(self, extent):
        if (self.z - 2 * LENGTH_SAFETY > extent.upper.z
                and not np.isclose(self.z, extent.upper.z)):
            self._is_omittable = True
            logger.info("Setting XYP \"%s\" omittable.", self.name)
            return
        self._offset = vector.Three(extent.centre.x,
                                    extent.centre.y,
                                    0.0)
        self._scale_x = extent.size.x * (SCALING_TOLERANCE + 1)
        self._scale_y = extent.size.y * (SCALING_TOLERANCE + 1)
        self._scale_z = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        return self._offset + vector.Three(0, 0, self.z - (self._scale_z * 0.5))


class XZP(InfiniteHalfSpace):
    """Infinite half space perpendicular to the y-axis."""
    def __init__(self, name, y, translation=None):
        self.name = name
        self.y = y
        if translation is not None:
            self.y += translation[1]
        self.rotation = np.identity(3)

    def crude_extent(self):
        return abs(self.y)

    def _apply_extent(self, extent):
        if (self.y - 2 * LENGTH_SAFETY > extent.upper.y
                and not np.isclose(self.y, extent.upper.y)):
            self._is_omittable = True
            logger.info("Setting XZP \"%s\" omittable.", self.name)
            return
        self._offset = vector.Three(extent.centre.x, 0.0, extent.centre.z)
        self._scale_x = extent.size.x * (SCALING_TOLERANCE + 1)
        self._scale_y = extent.size.y * (SCALING_TOLERANCE + 1)
        self._scale_z = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        return self._offset + vector.Three(0, self.y - (self._scale_y * 0.5), 0)


class YZP(InfiniteHalfSpace):
    """Infinite half space perpendicular to the x-axis."""
    def __init__(self, name, x, translation=None):
        self.name = name
        self.x = x
        if translation is not None:
            self.x += translation[0]
        self.rotation = np.identity(3)

    def crude_extent(self):
        return abs(self.x)

    def _apply_extent(self, extent):
        if (self.x - 2 * LENGTH_SAFETY > extent.upper.x
                and not np.isclose(self.x, extent.upper.x)):
            self._is_omittable = True
            logger.info("Setting YZP \"%s\" omittable.", self.name)
            return
        self._offset = vector.Three(0.0, extent.centre.y, extent.centre.z)
        self._scale_x = extent.size.x * (SCALING_TOLERANCE + 1)
        self._scale_y = extent.size.y * (SCALING_TOLERANCE + 1)
        self._scale_z = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        return self._offset + vector.Three(self.x - (self._scale_x * 0.5), 0, 0)


class PLA(Body):
    """Generic infinite half-space.

    Parameters:
    point = point on surface of halfspace
    normal = vector normal to the surface (pointing outwards)

    """
    def __init__(self, name, normal, point, translation=None):
        self.name = name
        self.normal = vector.Three(normal)
        self.point = vector.Three(point)
        if translation is not None:
            self.point += vector.Three(translation)
        # Choose the face pointing in the direction of the positive
        # z-axis to make the surface of the half space.
        self.rotation = trf.matrix_from([0, 0, 1], self.normal)

        # Start by putting the point as close to the origin as can,
        # and the normalising the norm vector.  these are the versions
        # we actually "use.. in all methods within" this is a horrible
        # wart and really i should do this more sensibly.  oh well for now.
        self._normal = self.normal / np.linalg.norm(self.normal)
        self._point = self.point
        self._point = self._closest_point([0, 0, 0])

    def centre(self):
        # This is the centre of the underlying gdml solid (i.e. won't
        # be on the surface, but set backwards by half length scale's amount.
        centre = self._point - 0.5 * self._scale * self._normal.unit()
        return centre

    def _apply_extent(self, extent):
        self._point = self._closest_point(extent.centre)
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

    def crude_extent(self):
        return max(abs(self._point.x), abs(self._point.y), abs(self._point.z))

    def _closest_point(self, point):
        """
        Return the point on the plane closest to the point provided.

        """
        # perpendicular distance from the point to the plane
        distance = np.dot((self._point - point), self._normal)
        closest_point = point + distance * self._normal

        assert (abs(np.dot(self._normal, closest_point - self._point)) <
                1e-6), "Point isn't on the plane!"

        return closest_point

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pyg4ometry.geant4.solid.Box(_unique_name(self.name),
                                0.5 * self._scale + safety_addend,
                                0.5 * self._scale + safety_addend,
                                0.5 * self._scale + safety_addend)


class XCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to x-axis

    y = y-coordinate of the centre of the cylinder
    z = z-coordinate of the centre of the cylinder
    radius = radius of the cylinder

    """
    def __init__(self, name, y, z, radius, translation=None):
        self.name = name
        self.y = y
        self.z = z
        if translation is not None:
            self.y += translation[1]
            self.z += translation[2]
        self.radius = radius
        # Stuff for infinite scaling..
        self._radius = radius
        # Rotate pi/2 about the y-axis.
        self.rotation = np.array([[0, 0, -1],
                                  [0, 1, 0],
                                  [1, 0, 0]])

    def _apply_extent(self, extent):
        self._offset = vector.Three(extent.centre.x, 0.0, 0.0)
        self._scale = extent.size.x * (SCALING_TOLERANCE + 1)

    def centre(self):
        return self._offset + vector.Three(0.0, self.y, self.z)

    def crude_extent(self):
        return max([abs(self.y), abs(self.z), self.radius])


class YCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to y-axis

    z = z-coordinate of the centre of the cylinder
    x = x-coordinate of the centre of the cylinder
    radius = radius of the cylinder

    """
    def __init__(self, name, z, x, radius, translation=None):
        self.name = name
        self.x = x
        self.z = z
        if translation is not None:
            self.x += translation[0]
            self.z += translation[2]
        self.radius = radius
        self._radius = radius
        # Rotate by pi/2 about the x-axis.
        self.rotation = np.array([[1, 0, 0],
                                  [0, 0, 1],
                                  [0, -1, 0]])

    def _apply_extent(self, extent):
        self._offset = vector.Three(0.0, extent.centre.y, 0.0)
        self._scale = extent.size.y * (SCALING_TOLERANCE + 1)

    def centre(self):
        return self._offset + vector.Three(self.x, 0.0, self.z)

    def crude_extent(self):
        return max([abs(self.x), abs(self.z), self.radius])


class ZCC(InfiniteCylinder):
    """Infinite circular cylinder parallel to z-axis

    x = x-coordinate of the centre of the cylinder
    y = y-coordinate of the centre of the cylinder
    radius = radius of the cylinder

    """
    def __init__(self, name, x, y, radius, translation=None):
        self.name = name
        self.x = x
        self.y = y
        if translation is not None:
            self.y += translation[1]
            self.z += translation[2]
        self.radius = radius
        self._radius = radius
        self.rotation = np.identity(3)

    def _apply_extent(self, extent):
        self._offset = vector.Three(0.0, 0.0, extent.centre.z)
        self._scale = extent.size.z * (SCALING_TOLERANCE + 1)

    def centre(self):
        return self._offset + vector.Three(self.x, self.y, 0.0)

    def crude_extent(self):
        return max([abs(self.x), abs(self.y), self.radius])


class XEC(InfiniteEllipticalCylinder):
    """An infinite elliptical cylinder parallel to the x-axis.

    y = y-coordinate of the centre of the ellipse face.
    z = z-coordinate of the centre of the ellipse face.
    semi_y = semi-axis in the y-direction of the ellipse face.
    semi_z = semi-axis in the z-direction of the ellipse face.

    """
    def __init__(self, name, y, z, semi_y, semi_z, translation=None):
        self.name = name
        self.y = y
        self.z = z
        if translation is not None:
            self.y += translation[1]
            self.z += translation[2]
        self.semi_y = semi_y
        self.semi_z = semi_z
        # Rotate pi/2 about the y-axis.
        self.rotation = np.array([[0, 0, -1],
                                  [0, 1, 0],
                                  [1, 0, 0]])

    def centre(self):
        return vector.Three(0.0, self.y, self.z)

    def crude_extent(self):
        return max([abs(self.y), abs(self.z),
                    abs(self.semi_y), abs(self.semi_z)])

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pygdml.solid.EllipticalTube(self._unique_body_name(),
                                           self.semi_z + safety_addend,
                                           self.semi_y + safety_addend,
                                           0.5 * self._scale)


class YEC(InfiniteEllipticalCylinder):
    """An infinite elliptical cylinder parallel to the y-axis.

    z - z-coordinate of the centre of the ellipse face.
    x - x-coordinate of the centre of the ellipse face.
    semi_z - semi-axis in the z-direction of the ellipse face.
    semi_x - semi-axis in the x-direction of the ellipse face.

    """
    def __init__(self, name, z, x, semi_z, semi_x, translation=None):
        self.name = name
        self.x = x
        self.z = z
        if translation is not None:
            self.x += translation[0]
            self.z += translation[2]
        self.semi_x = semi_x
        self.semi_z = semi_z
        # Rotate by pi/2 about the x-axis.
        self.rotation = np.array([[1, 0, 0],
                                  [0, 0, 1],
                                  [0, -1, 0]])

    def centre(self):
        return vector.Three(self.x, 0.0, self.z)

    def crude_extent(self):
        return max([abs(self.x), abs(self.z),
                    abs(self.semi_x), abs(self.semi_z)])

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pygdml.solid.EllipticalTube(self._unique_body_name(),
                                           self.semi_x + safety_addend,
                                           self.semi_z + safety_addend,
                                           0.5 * self._scale)


class ZEC(InfiniteEllipticalCylinder):
    """An infinite elliptical cylinder parallel to the z-axis.

    x - x-coordinate of the centre of the ellipse face.
    y - y-coordinate of the centre of the ellipse face.
    semi_x - semi-axis in the x-direction of the ellipse face.
    semi_y - semi-axis in the y-direction of the ellipse face.

    """
    def __init__(self, name, x, y, semi_x, semi_y, translation=None):
        self.name = name
        self.x = x
        self.y = y
        if translation is not None:
            self.x += translation[0]
            self.y += translation[1]
        self.semi_x = semi_x
        self.semi_y = semi_y
        # Rotate by pi/2 about the x-axis.
        self.rotation = np.identity(3)

    def centre(self):
        return vector.Three(self.x, self.y, 0.0)

    def crude_extent(self):
        return max([abs(self.x), abs(self.y),
                    abs(self.semi_x), abs(self.semi_y)])

    def gdml_solid(self, length_safety=None, register=False):
        safety_addend = Body._get_safety_addend(length_safety)
        return pygdml.solid.EllipticalTube(self._unique_body_name(),
                                           self.semi_x + safety_addend,
                                           self.semi_y + safety_addend,
                                           0.5 * self._scale)


class Region(object):
    """Class used for interfacing a FLUKA region with a GDML volume.
    This class has the underlying pygdml volume payload, alongside its
    placement and rotation in the world volume, and a material.

    """
    def __init__(self, name, zones, material):
        self.name = name
        self.material = material
        if isinstance(zones, Zone):
            raise TypeError("zones must be an iterable of Zone instances.")
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
        world_volume = make_world_volume("world", "G4_AIR")
        solid = self.evaluate(zones, optimise=optimise)
        solid.add_to_volume(world_volume)
        _mesh_and_view_world_volume(world_volume, setclip)

    def add_to_volume(self, mother_volume, zones=None,
                      optimise=True,
                      register=False):
        """
        Basically for adding to a world volume.

        """
        name = (self.name
                if zones is None
                else "{}-Zones-{}".format(self.name,
                                          "-".join([str(index) for
                                                    index in zones])))


        # if name in (["UJPLUGR4-Zones-1",
        # Note the overlaps in the UPS stuff below seem to get worse
        # with larger scaling tolerance..
        if name in (["UPS16H1A-Zones-1",
                     "UPS16H1C-Zones-1",
                     "UPS16H1S-Zones-1",
                     "UPS16H2A-Zones-1",
                     "UPS16H2S-Zones-1",
                     "UPS16H2C-Zones-1",
                     "UJ16AIR1-Zones-0", # Highest priority to fix.
                     "UJPLUGR0-Zones-1", #zones
                     "UJPLUGR4-Zones-1"]): # second priority
            print("Skipping bad tunnel region, oops...")
            return


        boolean = self.evaluate(zones, optimise=optimise)
        # Convert the matrix to TB xyz:
        rotation_angles = trf.matrix2tbxyz(boolean.rotation)
        # Up to this point all rotations are active, which is OK
        # because so are boolean rotations.  However, volume rotations
        # are passive, so reverse the rotation:
        rotation_angles = trf.reverse(rotation_angles)
        # Give a more informative name when a subset of the zones are
        # selected to be placed.

        pygdml.volume.Volume(
            rotation_angles, boolean.centre(),
            boolean.gdml_solid(length_safety="trim"), name, volume,
            1, False, self.material)

    def evaluate(self, zones=None, optimise=False):
        logger.info("Evaluating Region \"%s\", optimisation=%s, zones=%s",
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
        graph = nx.Graph()
        graph.add_nodes_from(range(n_zones))
        if n_zones == 1: # return here if there's only one zone.
            return nx.connected_components(graph)
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
            if nx.has_path(graph, i, j):
                continue

            # Finally: we must do the intersection op.  add 1 because
            # we conform to convention that
            logger.debug("Intersecting zone %d with %d", i, j)
            if get_overlap(booleans_and_extents[i][0],
                           booleans_and_extents[j][0]) is not None:
                graph.add_edge(i, j)
        return nx.connected_components(graph)

    def _get_zone_booleans_and_extents(self, optimise):
        """Return the meshes and extents of all regions of this model."""
        out = {}
        for index, zone in enumerate(self.zones):
            logger.debug("Evaluating zone %d", index)
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
            boilerplate = """TITLE
{}
GLOBAL        5000.0       0.0       0.0       0.0       1.0
DEFAULTS                                                              PRECISIO
BEAM         10000.0                                                  PROTON
GEOBEGIN                                                              COMBNAME
0        0                  PYFLUKA
"""
            f.write(boilerplate.format(self.name))
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
            body_crude_extent = body.crude_extent()
            logger.debug("Extent for body %s = %s", body, body_crude_extent)
            extent = max(extent, body_crude_extent)
        logger.debug("Crude extent for zone %s = %s", self, extent)
        return extent

    def view(self, setclip=True, optimise=False):
        self.evaluate(optimise=optimise).view(setclip=setclip)

    def view_compare_optimisation(self, setclip=True):
        world_volume = make_world_volume("world", "G4_AIR")
        optimised = self.evaluate(optimise=True)
        unoptimised = self.evaluate(optimise=False)
        optimised.add_to_volume(world_volume)
        unoptimised.add_to_volume(world_volume)

        _mesh_and_view_world_volume(world_volume, setclip)

    def evaluate_with_extent(self, optimise):
        boolean = self.evaluate(optimise=optimise)
        extent = boolean._extent()
        return boolean, extent

    def evaluate(self, optimise=False):
        """
        Evaluate the zone, returning a Boolean instance with the
        appropriate optimisations, if any.

        """
        logger.debug("%s: optimise=%s", self, optimise)
        if optimise:
            return self._optimised_boolean()
        return self._crude_boolean()

    def _crude_boolean(self):
        logger.debug("%s", self)
        scale = self.crude_extent() * 10.
        # Map the crude extents to the solids:
        self._map_extent_2_bodies(self.contains, scale)
        self._map_extent_2_bodies(self.excludes, scale)

        return self._accumulate(None) # Don't trim/extend.  Get the true mesh.

    def _optimised_boolean(self):
        logger.debug("%s", self)
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


        # Remove all bodies which are omittable:
        filtered_contains = [body for body in self.contains
                             if (isinstance(body, Zone)
                                 or not body._is_omittable)]
        filtered_excludes = [body for body in self.excludes
                             if (isinstance(body, Zone)
                                 or not body._is_omittable)]

        accumulated = None
        for body in filtered_contains:
            if isinstance(body, Body):
                if accumulated is None: # If nothing to intersect with yet.
                    accumulated = body
                accumulated = body.intersection(
                    accumulated, safety_map['intersection'])
            elif isinstance(body, Zone): # If nothing to intersect with yet.
                if accumulated is None:
                    evaluated_zone = body._accumulate(subzone_order=subzone_order)
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

        assert accumulated is not None
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

    def bodies(self):
        """Return all the unique body instances associated with this zone"""
        return list(set(self._flatten()))

    def to_fluka_string(self):
        """Returns this Zone as a FLUKA input string."""
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
        world_volume = make_world_volume("world", "G4_AIR")
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

        world_volume = make_world_volume("world", "G4_AIR")
        if (first is None and second is None
                or first is True and second is True):
            pygdml.Volume([0, 0, 0], [0, 0, 0], solid1, solid1.name,
                          world_volume, 1, False, "G4_AIR")
            pygdml.Volume(trf.reverse(tra2[0]), tra2[1], solid2, solid2.name,
                          world_volume, 1, False, "G4_AIR")
        elif first is True and second is not True:
            pygdml.Volume([0, 0, 0], [0, 0, 0], solid1, solid1.name,
                          world_volume, 1, False, "G4_AIR")
        elif second is True and first is not True:
            pygdml.Volume(trf.reverse(tra2[0]), tra2[1], solid2, solid2.name,
                          world_volume, 1, False, "G4_AIR")
        elif first is False and second is False:
            raise RuntimeError("Must select at least one"
                               " of the two solids to view")

        _mesh_and_view_world_volume(world_volume, setclip)

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
    """Return the extent of any overlapping or solid region between the first
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

def clip_world_volume_with_safety(world_volume, safety_addend):
    world_volume.setClip()
    world_volume.currentVolume.pX += safety_addend
    world_volume.currentVolume.pY += safety_addend
    world_volume.currentVolume.pZ += safety_addend

def subtract_from_world_volume(world_volume, subtrahends, bb_addend=0.0):
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
    unclipped_extent = Extent.from_world_volume(world_volume)
    # The offset is -1 * the unclipped extent's centre.
    unclipped_centre = unclipped_extent.centre
    other_offset = -1 * unclipped_centre
    clip_world_volume_with_safety(world_volume, bb_addend)
    # Make an RPP out of the clipped bounding box.
    world_name = world_volume.currentVolume.name
    # solids magically start having material attributes at the top-level so
    # we must pass the material correctly to the new subtraction solid.
    world_material = world_volume.currentVolume.material
    world_solid = world_volume.currentVolume

    # Deal with the trailing floating points introduced somewhere
    # in pygdml that cause the box to be marginally too big:
    decimal_places = int((-1 * np.log10(LENGTH_SAFETY)))
    box_parameters = [-1 * world_solid.pX,
                      -1 * world_solid.pY,
                      -1 * world_solid.pZ,
                      world_solid.pX,
                      world_solid.pY,
                      world_solid.pZ]


    box_parameters = [round(i, decimal_places) for i in
                      box_parameters]

    world = RPP(world_name, box_parameters[:3], box_parameters[3:])
    # We make the subtraction a bit smaller just to be sure we
    # don't subract from a placed solid within, so safety='trim'.
    for subtrahend in subtrahends:
        if isinstance(subtrahend,
                      (InfiniteCylinder,
                       InfiniteHalfSpace,
                       InfiniteEllipticalCylinder)):
            raise TypeError("Subtrahends must be finite!")

        world = world.subtraction(subtrahend, safety="trim",
                                  other_offset=other_offset)
    world_volume.currentVolume = world.gdml_solid()
    world_volume.currentVolume.material = world_material

def make_world_volume(name, material):
    """This method returns a pygdml world volume with a correctly
    mangled name and a material"""
    unique_id = uuid.uuid4()
    world_box = pygdml.solid.Box("world_box_{}".format(unique_id), 1, 1, 1)
    name = "{}_world_volume_{}".format(name, unique_id)
    return pygdml.Volume([0, 0, 0], [0, 0, 0], world_box,
                         name, None, 1, False, material)

def _mesh_and_view_world_volume(world_volume, setclip):
    if setclip:
        world_volume.setClip()
    mesh = world_volume.pycsgmesh()
    viewer = pygdml.VtkViewer()
    viewer.addSource(mesh)
    viewer.view()
