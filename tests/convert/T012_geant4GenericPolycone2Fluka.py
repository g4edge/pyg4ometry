import os as _os
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi

normal = 1
two_planes = 2


def Test(vis=False, interactive=False, fluka=True, type=normal):
    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    # pi     = _gd.Constant("pi","3.1415926",reg,True)
    psphi = _gd.Constant("sphi", "1", reg, True)
    pdphi = _gd.Constant("dphi", "4", reg, True)

    pr1 = _gd.Constant("pr1", "5", reg, True)
    pz1 = _gd.Constant("z1", "-10", reg, True)

    pr2 = _gd.Constant("pr2", "7.5", reg, True)
    pz2 = _gd.Constant("z2", "-10", reg, True)

    pr3 = _gd.Constant("pr3", "10", reg, True)
    pz3 = _gd.Constant("z3", "0", reg, True)

    pr4 = _gd.Constant("pr4", "20", reg, True)
    pz4 = _gd.Constant("z4", "-5", reg, True)

    pr5 = _gd.Constant("pr5", "7.5", reg, True)
    pz5 = _gd.Constant("z5", "10", reg, True)

    pr6 = _gd.Constant("pr6", "5", reg, True)
    pz6 = _gd.Constant("z6", "10", reg, True)

    pr7 = _gd.Constant("pr7", "2", reg, True)
    pz7 = _gd.Constant("z7", "5", reg, True)

    pr = [pr1, pr2, pr3, pr4, pr5, pr6, pr7]
    pz = [pz1, pz2, pz3, pz4, pz5, pz6, pz7]

    if type == two_planes:
        pr = [pr1, pr2]
        pz = [pz1, pz2]

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    pm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ps = _g4.solid.GenericPolycone("ps", psphi, pdphi, pr, pz, reg, "mm", "rad")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    pl = _g4.LogicalVolume(ps, pm, "pl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], pl, "p_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(
        _os.path.join(
            _os.path.dirname(__file__), "T012_geant4GenericPolycone2Fluka.gdml"
        )
    )

    # fluka conversion
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(
            _os.path.join(
                _os.path.dirname(__file__), "T012_geant4GenericPolycone2Fluka.inp"
            )
        )

    # flair output file
    f = _fluka.Flair("T012_geant4GenericPolycone2Fluka.inp", extentBB)
    f.write(
        _os.path.join(
            _os.path.dirname(__file__), "T012_geant4GenericPolycone2Fluka.flair"
        )
    )

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)
