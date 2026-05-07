import pyg4ometry as _pyg
import numpy as _np
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gdml
import pyg4ometry.visualisation as _vis
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka

from os import path as _path


def Test(vis=False, interactive=False, gdml=True, fluka=False):

    reg = _g4.Registry()

    safety = _gdml.Defines.Constant("length_safety", 1e-8, reg)

    bp_radius = _gdml.Defines.Constant("beam_pipe_radius", 7.5, reg)
    bp_thickness = _gdml.Defines.Constant("beam_pipe_thickness", 2, reg)
    bp_length = _gdml.Defines.Constant("beam_pipe_length", 50, reg)

    wg_innerr = _gdml.Defines.Constant("wg_innerrb", bp_radius, reg)
    wg_outerd = _gdml.Defines.Constant("wg_outerd", 91.2, reg)
    wg_outerr = _gdml.Defines.Constant("wg_outerr", wg_outerd / 2.0, reg)
    wg_length = _gdml.Defines.Constant("wg_length", 50.0, reg)

    # wg_length    = 50.0
    wg_width = 8.0
    wg_height = _gdml.Defines.Constant("wg_height", 27.5, reg)
    wg_offset = _gdml.Defines.Constant("wg_offset", 12.0, reg)
    wg_centre = _gdml.Defines.Constant("wg_centre", wg_offset + wg_height / 2, reg)

    ec_innerr = _gdml.Defines.Constant("ec_innerr", bp_radius, reg)
    ec_outerr = _gdml.Defines.Constant("ec_outerr", wg_outerr, reg)
    ec_length = _gdml.Defines.Constant("ec_length", 5, reg)
    ec_centre = _gdml.Defines.Constant("ec_center", wg_length + ec_length / 2, reg)

    ca_length = _gdml.Defines.Constant("ca_length", 13, reg)
    ca_outerr = _gdml.Defines.Constant("ca_outerr", wg_outerd / 2.0, reg)
    ca_centre = _gdml.Defines.Constant("ca_centre", ca_length / 2.0, reg)
    ca_innerr = _gdml.Defines.Constant("ca_innerr", 52.778 / 2.0, reg)

    ce_outerr = _gdml.Defines.Constant("ce_outerr", ca_innerr + 5, reg)
    ce_length = _gdml.Defines.Constant("ce_length", 5, reg)

    ################################
    # World solid
    ################################
    world_solid = _g4.solid.Box("world_solid", 500, 500, 500, reg)
    world_logical = _g4.LogicalVolume(world_solid, "G4_Galactic", "world_logical", reg)

    ################################
    # Wave guide
    ################################
    wg_body_solid = _g4.solid.Tubs(
        "wg_body_solid", wg_innerr, wg_outerr, wg_length, 0, 2 * _np.pi, reg
    )
    wg_cut_solid = _g4.solid.Box("wg_cut_solid", wg_height, wg_width, wg_length, reg)
    wg_cut2_solid = _g4.solid.Box("wg_cut2_solid", 100.0, 100.0, wg_length, reg)

    wg_sub1 = _g4.solid.Subtraction(
        "wg_sub1", wg_body_solid, wg_cut_solid, [[0, 0, 0], [wg_centre, 0, 0]], reg
    )
    wg_sub2 = _g4.solid.Subtraction(
        "wg_sub2", wg_sub1, wg_cut_solid, [[0, 0, _np.pi / 2.0], [0, wg_centre, 0]], reg
    )
    wg_sub3 = _g4.solid.Subtraction(
        "wg_sub3", wg_sub2, wg_cut_solid, [[0, 0, _np.pi], [-wg_centre, 0, 0]], reg
    )
    wg_sub4 = _g4.solid.Subtraction(
        "wg_sub4",
        wg_sub3,
        wg_cut_solid,
        [[0, 0, 3.0 / 2.0 * _np.pi], [0, -wg_centre, 0]],
        reg,
    )

    wg_sub5 = _g4.solid.Subtraction(
        "sg_sub5", wg_sub4, wg_cut2_solid, [[0, 0, 0], [50 + 10, 50 + 10, -10]], reg
    )
    wg_sub6 = _g4.solid.Subtraction(
        "sg_sub6", wg_sub5, wg_cut2_solid, [[0, 0, 0], [-50 - 10, 50 + 10, -10]], reg
    )
    wg_sub7 = _g4.solid.Subtraction(
        "sg_sub7", wg_sub6, wg_cut2_solid, [[0, 0, 0], [-50 - 10, -50 - 10, -10]], reg
    )
    wg_sub8 = _g4.solid.Subtraction(
        "sg_sub8", wg_sub7, wg_cut2_solid, [[0, 0, 0], [50 + 10, -50 - 10, -10]], reg
    )

    wg_logical = _g4.LogicalVolume(wg_sub8, "G4_Cu", "wg_logical", reg)
    wg_physical = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, -wg_length / 2.0],
        wg_logical,
        "wg_physical",
        world_logical,
        reg,
    )

    ################################
    # Wave guide end cap
    ################################
    ec_solid = _g4.solid.Tubs("ec_solid", ec_innerr, ec_outerr, ec_length, 0, 2 * _np.pi, reg)
    ec_sub1 = _g4.solid.Subtraction(
        "ec_sub1", ec_solid, wg_cut2_solid, [[0, 0, 0], [50 + 10, 50 + 10, 0]], reg
    )
    ec_sub2 = _g4.solid.Subtraction(
        "ec_sub2", ec_sub1, wg_cut2_solid, [[0, 0, 0], [-50 - 10, 50 + 10, 0]], reg
    )
    ec_sub3 = _g4.solid.Subtraction(
        "ec_sub3", ec_sub2, wg_cut2_solid, [[0, 0, 0], [-50 - 10, -50 - 10, 0]], reg
    )
    ec_sub4 = _g4.solid.Subtraction(
        "ec_sub4", ec_sub3, wg_cut2_solid, [[0, 0, 0], [50 + 10, -50 - 10, 0]], reg
    )
    ec_logical = _g4.LogicalVolume(ec_sub4, "G4_Cu", "ec_logical", reg)
    ec_physical = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, -wg_length - ec_length / 2.0 - safety],
        ec_logical,
        "ec_physical",
        world_logical,
        reg,
    )

    ################################
    # Cavity
    ################################
    ca_solid = _g4.solid.Tubs("ca_solid", ca_innerr, wg_outerr, ca_length, 0, 2 * _np.pi, reg)
    ca_logical = _g4.LogicalVolume(ca_solid, "G4_Cu", "ca_logical", reg)
    ca_physical = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, ca_length / 2.0 + safety],
        ca_logical,
        "ca_physical",
        world_logical,
        reg,
    )

    ################################
    # Cavity end cap
    ################################
    ce_solid = _g4.solid.Tubs("ce_solid", bp_radius, ce_outerr, ce_length, 0, 2 * _np.pi, reg)
    ce_logical = _g4.LogicalVolume(ce_solid, "G4_Cu", "ce_logical", reg)
    ce_physical = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, ca_length + ce_length / 2 + 2 * safety],
        ce_logical,
        "ce_physical",
        world_logical,
        reg,
    )

    ################################
    # beam pipe 1 and 2
    ################################
    bp_solid = _g4.solid.Tubs(
        "bp_solid", bp_radius, bp_radius + bp_thickness, bp_length, 0, 2 * _np.pi, reg
    )
    bp_logical = _g4.LogicalVolume(bp_solid, "G4_Cu", "bp_logical", reg)
    bp_physical1 = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, ca_length + ce_length + bp_length / 2.0 + 2 * safety],
        bp_logical,
        "bp_physical1",
        world_logical,
        reg,
    )
    bp_physical2 = _g4.PhysicalVolume(
        [0, 0, 0],
        [0, 0, -wg_length - ec_length - bp_length / 2.0 - 2 * safety],
        bp_logical,
        "bp_physical2",
        world_logical,
        reg,
    )

    # register the world volume
    reg.setWorld("world_logical")

    # test extent of physical volume
    extentBB = world_logical.extent(includeBoundingSolid=True)

    ################################
    # visualisation
    ################################
    v = None
    if vis:
        v = _vis.VtkViewer()
        v.addLogicalVolume(world_logical)
        v.addAxes(100)
        v.setOpacity(0.25)
        v.view(interactive=interactive)

    ################################
    # write gdml
    ################################
    if gdml:
        w = _gdml.Writer()
        w.addDetector(reg)
        w.write(_path.join(_path.dirname(_path.abspath(__file__)), "DipoleCbpm.gdml"))

    ################################
    # write fluka
    ################################
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(world_logical)

        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(_path.join(_path.dirname(_path.abspath(__file__)), "DipoleCbpm.inp"))

        # flair output file
        f = _fluka.Flair("DipoleCbpm.inp", extentBB)
        f.write(_path.join(_path.dirname(_path.abspath(__file__)), "DipoleCbpm.flair"))

    return {"logicalVolume": world_logical, "vtkViewer": v}


if __name__ == "__main__":
    Test()
