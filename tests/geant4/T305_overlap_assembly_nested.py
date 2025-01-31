import os as _os
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import numpy as _np

import ECamelAssembly


def Test(vis=False, interactive=False):
    reg = _g4.Registry()

    vacuum = _g4.MaterialPredefined("G4_Galactic")

    assembly = ECamelAssembly.MakeECamelAssembly(reg, separation=5)
    worldSolid = _g4.solid.Box("world_solid", 200, 200, 200, reg)
    worldLV = _g4.LogicalVolume(worldSolid, vacuum, "world_lv", reg)

    masterAssembly = _g4.AssemblyVolume("assembly2", reg)
    asPV1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], assembly, "part_pv1", masterAssembly, reg)
    asPV2 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 12], assembly, "part_pv2", masterAssembly, reg)
    asPV3 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 24], assembly, "part_pv3", masterAssembly, reg)

    _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], masterAssembly, "ma_pv1", worldLV, reg)
    _g4.PhysicalVolume(
        [-_np.pi / 12, _np.pi / 24, 0],
        [30, 0, 7],
        masterAssembly,
        "ma_pv2",
        worldLV,
        reg,
    )

    # check for overlaps
    worldLV.checkOverlaps(recursive=True, coplanar=True)

    # set world volume
    reg.setWorld(worldLV)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T305_overlap_assembly_nested.gdml"))

    # test __repr__
    str(worldSolid)

    # test extent of physical volume
    extentBB = worldLV.extent(includeBoundingSolid=True)
    extent = worldLV.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": worldLV, "vtkViewer": v}


if __name__ == "__main__":
    Test()
