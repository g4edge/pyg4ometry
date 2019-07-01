from __future__ import (absolute_import, print_function, division)

import pygdml.transformation as trf
import pyfluka.vector

def get_bdsim_placement_string(output_name,
                               gdml_path,
                               bdsim_point,
                               fluka_point,
                               fluka_bounding_box_origin,
                               bdsim_rotation_axis,
                               bdsim_rotation_angle,
                               fluka_direction):
    """
    output_name -- the name of the output geometry placement.
    gdml_path -- the path of the GDML file.
    bdsim_point -- the point in BDSIM-world to coincide with
                         `fluka_point` in BDSIM-world.
    fluka_point -- the point in FLUKA-world to coincide with
                         `bdsim_point` in BDSIM-world
    fluka_bounding_box_origin -- the centre of the bounding box in
                         FLUKA-world.  This coordinate is in the
                         dictionary returned by
                         pyfluka.Model.write_to_gdml.
    bdsim_rotation_axis -- The axis component of the axis-angle
                         rotation denoting the desired rotation in
                         BDSIM world.
    bdsim_rotation_angle -- The angle component of the axis-angle
                         rotation denoting the desired rotation in
                         BDSIM world.
    fluka_direction -- the unit vector denoting the direction in the
                         FLUKA world that is to be orientated to the
                         rotation in bdsim_rotation.

    """
    axis, angle = _get_bdsim_rotation(fluka_direction,
                                      bdsim_rotation_axis,
                                      bdsim_rotation_angle)
    placement = _get_bdsim_placement(bdsim_point, fluka_point,
                                     fluka_bounding_box_origin,
                                     axis, angle)
    return _build_placement_string(output_name, gdml_path, placement,
                                   axis, angle)



def _get_bdsim_rotation(fluka_direction,
                        bdsim_rotation_axis,
                        bdsim_rotation_angle):
    """Get the rotation for placing the external FLUKA geometry with
    respect to the BDSIM beamline.  The fluka_direction vector is
    aligned to the orientation denoted by bdsim_rotation

    fluka_direction --  a vector in the FLUKA coordinate system.
    bdsim_rotation -- an axis-angle rotation in the bdsim coordinate system.

    """
    # The reason why the fluka_direction should be a unit vector and
    # the bdsim_rotation instead an axis-angle rotation is that FLUKA
    # uses unit vectors to denote orientation and BDSIM output stores
    # rotations as axis-angle rotations.
    # Vector pointing in the direction sig
    bdsim_unit_vector = trf.axisangle2matrix(bdsim_rotation_axis,
                                             bdsim_rotation_angle).dot(
                                                 [0, 0, 1])
    net_rotation_matrix = trf.matrix_from(fluka_direction, bdsim_unit_vector)

    axis_angle = trf.matrix2axisangle(net_rotation_matrix)
    return axis_angle

def _get_bdsim_placement(bdsim_point, fluka_point,
                         fluka_bounding_box_origin,
                         axis, angle):
    """Return the placement that aligns fluka_point with bdsim_point in
    the BDSIM global coordinate system.  Units in mm

    Arguments:
    bdsim_point -- a point in the BDSIM world.
    fluka_point -- a coordinate in the FLUKA coordinate system.
    fluka_bounding_box_origin -- the centre of the bounding box in FLUKA-world.
    axis -- the axis part of the axis-angle rotation for the bounding
    box.  Get this from get_bdsim_rotation.
    angle -- the angle part of the axis-angle rotation for the bounding
    box.  Get this from get_bdsim_rotation.

    """
    # Convert the axis/angle back to a rotation matrix.
    rotation_matrix = trf.axisangle2matrix(axis, angle)
    # converts a point in the fluka coordinate system to its point in
    # the bdsim global coordinate system.
    fluka_point_in_bdsim = fluka_point - fluka_bounding_box_origin
    rotated_point = rotation_matrix.dot(fluka_point_in_bdsim)
    offset = bdsim_point - rotated_point
    return offset

def _build_placement_string(name, filepath, offset, axis, angle):
    """All units should be in millimetres."""
    # cast iterables to vectors.
    offset = pyfluka.vector.Three(offset)
    axis = pyfluka.vector.Three(axis)
    out = """{name}: placement,
geometryFile="gdml:{filepath}", axisAngle=1,
x={offset.x}*mm, y={offset.y}*mm, z={offset.z}*mm,
axisX={axis.x}, axisY={axis.y}, axisZ={axis.z},
angle={angle};
""".format(name=name, filepath=filepath,
           offset=offset, axis=axis, angle=angle)
    return out
