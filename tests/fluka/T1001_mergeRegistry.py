import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np


def Test(vis=False, interactive=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    def geometry1(fileName="geometry1.inp"):
        reg1 = _g4.Registry()
        b1 = _g4.solid.Box("wb", 75, 75, 75, reg1)
        t1 = _g4.solid.CutTubs("ct", 0, 20, 25, 0, _np.pi * 2, [0, -0.1, -1], [0, -0.1, 1], reg1)

        b1l = _g4.LogicalVolume(b1, "G4_Galactic", "b1l", reg1)
        t1l = _g4.LogicalVolume(t1, "G4_Fe", "t1l", reg1)

        t1p = _g4.PhysicalVolume([5, 10, 15], [0.1, 0.2, 0.3], t1l, "t1p", b1l, reg1)

        # set world volume
        reg1.setWorld(b1l.name)

        if vis:
            v = _vi.VtkViewer()
            v.addLogicalVolume(b1l)
            v.view(interactive=interactive)

        freg = _convert.geant4Reg2FlukaReg(reg1)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / fileName)

    def geometry2(fileName="geometry1.inp"):
        reg1 = _g4.Registry()
        b1 = _g4.solid.Box("wb", 75, 75, 75, reg1)
        o1 = _g4.solid.Orb("ct", 20, reg1)

        b1l = _g4.LogicalVolume(b1, "G4_Galactic", "b1l", reg1)
        o1l = _g4.LogicalVolume(o1, "G4_Fe", "o1l", reg1)

        o1p = _g4.PhysicalVolume([5, 10, 15], [0.1, 0.2, 0.3], o1l, "t1p", b1l, reg1)

        # set world volume
        reg1.setWorld(b1l.name)

        if vis:
            v = _vi.VtkViewer()
            v.addLogicalVolume(b1l)
            v.view(interactive=interactive)

        freg = _convert.geant4Reg2FlukaReg(reg1)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / fileName)

    geometry1("T1001_file1.inp")
    geometry2("T1002_file2.inp")

    freg1 = _fluka.Reader("T1001_file1.inp").getRegistry()
    freg2 = _fluka.Reader("T1002_file2.inp").getRegistry()

    return [freg1, freg2]
