import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np


def Test(vis=False, interactive=False, fluka=True, n_slice=10, n_stack=10, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    eax = _gd.Constant("eax", "10", reg, True)
    eby = _gd.Constant("eby", "15", reg, True)
    ecz = _gd.Constant("ecz", "20", reg, True)
    ebc = _gd.Constant("ebc", "-15", reg, True)
    etc = _gd.Constant("etc", "15", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    em = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    es = _g4.solid.Ellipsoid("es", eax, eby, ecz, ebc, etc, reg, nslice=n_slice, nstack=n_stack)

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    el = _g4.LogicalVolume(es, em, "el", reg)
    ep = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], el, "e_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T016_geant4Ellipsoid2Fluka.gdml")

    # fluka conversion
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / "T016_geant4Ellipsoid2Fluka.inp")

    # flair output file
    f = _fluka.Flair("T016_geant4Ellipsoid2Fluka.inp", extentBB)
    f.write(outputPath / "T016_geant4Ellipsoid2Fluka.flair")

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
