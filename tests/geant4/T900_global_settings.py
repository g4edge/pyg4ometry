import os as _os

import pyg4ometry.config as _config
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi


def Test(vis=False, interactive=False, n_slice=16, n_stack=16):
    reg = _g4.Registry()

    # Set the default mesh density (both nstack and nslice) to the same value
    # for all curved solids. The global default value must be set before any of the
    # solid constructors are called.
    _config.setGlobalMeshSliceAndStack(n_slice)

    # nstack and nslice can be set individually for one solid via:
    _config.SolidDefaults.Orb.nslice = 40

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    ormax = _gd.Constant("rmax", "10", reg, True)

    wm = _g4.MaterialPredefined("G4_Galactic")
    om = _g4.MaterialPredefined("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    os = _g4.solid.Orb("os", ormax, reg, "mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    ol = _g4.LogicalVolume(os, om, "ol", reg)
    op = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], ol, "o_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(_os.path.join(_os.path.dirname(__file__), "T009_Orb.gdml"))
    w.writeGmadTester(_os.path.join(_os.path.dirname(__file__), "T009_Orb.gmad"), "T009_Orb.gdml")

    # test __repr__
    str(os)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": wl, "vtkViewer": v}


if __name__ == "__main__":
    Test()
