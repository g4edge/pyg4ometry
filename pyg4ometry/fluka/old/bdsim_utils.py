"""Useful functions and classes to ease the use of pyfluka with BDSIM."""

from __future__ import (absolute_import, print_function, division)
import collections
import warnings
import textwrap


import pyg4ometry.transformation as trf
import pyfluka.vector

def get_placement_string(output_name,
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
                                                 [0, 0, 1]).A1
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
    rotated_point = rotation_matrix.dot(fluka_point_in_bdsim).A1
    offset = bdsim_point - rotated_point
    return offset

def _build_placement_string(name, filepath, offset, axis, angle):
    """All units should be in millimetres."""
    # cast iterables to vectors.
    offset = pyfluka.vector.Three(offset)
    axis = pyfluka.vector.Three(axis)
    out = ("{name}: placement,"
           " x = {offset.x}*mm, y = {offset.y}*mm, z = {offset.z}*mm,"
           " geometryFile=\"gdml:{filepath}\", axisAngle=1,"
           " axisX = {axis.x}, axisY = {axis.y}, axisZ = {axis.z},"
           " angle = {angle};")
    out = '\n'.join(textwrap.wrap(out))
    return out.format(name=name, filepath=filepath,
                      offset=offset, axis=axis, angle=angle)

_G4_EXCEPTION_START = (
    "-------- WWWW ------- G4Exception-START -------- WWWW -------\n")
_G4_EXCEPTION_END = (
    "-------- WWWW -------- G4Exception-END --------- WWWW -------\n")

class G4ExceptionMessage(object):
    """Given an exception message (list of lines) from G4Exception-START to
    G4-Exception-END."""


    def __init__(self, msg):
        self.exception = ""
        self.issuer = ""
        self.message = ""

        self._set_exception(msg)
        self._set_issuer(msg)
        self._set_message(msg)

    def _set_exception(self, msg):
        for line in msg:
            if line.startswith("*** G4Exception"):
                self.exception = line.split(": ")[1].strip()

        G4ExceptionMessage._only_one(msg, "*** G4Exception")

    def _set_issuer(self, msg):
        for line in msg:
            if "issued by :" in line:
                self.issuer = line.split(": ")[1].strip()
        G4ExceptionMessage._only_one(msg, "issued by :")

    def _set_message(self, msg):
        start_index = next((i
                            for i, line in enumerate(msg)
                            if "issued by :" in line)) + 1
        message = []
        for line in msg[start_index:]:
            if line == _G4_EXCEPTION_END:
                break
            message.append(line)
        else:
            raise ValueError("No G4Exception-END line found!")
        self.message = message

    @staticmethod
    def _only_one(msg, substring):
        n = len([1 for line in msg if substring in line])
        if n != 1:
            raise ValueError("Too many occurences of {}".format(substring))


def process_geometry_test(file_in, file_out=None):
    # Skip until we get to the geometry test
    with open(file_in) as f:
        for i, line in enumerate(f):
            # If test was called from the vis.mac
            if line.startswith("/geometry/test/run"):
                start_overlaps_line_no = i
            # If test was called from the opengl visualiser prompt
            elif line.startswith("Running geometry overlaps"):
                start_overlaps_line_no = i
            elif line.startswith("Geometry overlaps check completed"):
                end_overlaps_line_no = i

    # Read in the geometry test exceptions and append
    # G4ExceptionMessage instances to all_exceptions
    with open(file_in) as f:
        all_exceptions = []
        this_exception = []
        in_exception = False
        for line in f.readlines()[start_overlaps_line_no:end_overlaps_line_no]:
            # Look for an exception message
            if line != _G4_EXCEPTION_START and in_exception is False:
                continue
            in_exception = True
            this_exception.append(line)
            if line == _G4_EXCEPTION_END and in_exception is True:
                all_exceptions.append(G4ExceptionMessage(this_exception))
                in_exception = False
                this_exception = []

    # Split into a dictionary of lists of instances based on issuer
    issuers = _splitter(all_exceptions, "issuer")

    return [_process_overlap_g4message(message)
            for message in issuers["G4PVPlacement::CheckOverlaps()"]]


def _splitter(iterable, attribute):
    out = dict()
    for item in iterable:
        value = getattr(item, attribute)
        if value not in out:
            out[value] = []
        out[value].append(item)

    return out

def _process_overlap_g4message(msg):
    if msg.issuer != "G4PVPlacement::CheckOverlaps()":
        raise ValueError("This exception message is not for an overlap!")
    first_vol = msg.message[1].split()[-1]
    amount = float(msg.message[3].split()[-2])
    unit = msg.message[3].split()[-1]

    if "mother volume" in msg.message[0]:
        second_vol = "mother"
        point = list(eval(msg.message[3].split()[4][:-1]))
        with_mother = True
    else:
        second_vol = msg.message[2].split()[1]
        point = list(eval(msg.message[3].split()[2][:-1]))
        with_mother = False

    OverlapInfo = collections.namedtuple(
        "OverlapInfo", ["first", "second", "point",
                        "amount", "unit", "with_mother"])
    return OverlapInfo(first_vol, second_vol, point, amount, unit, with_mother)
