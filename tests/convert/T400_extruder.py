import pathlib as _pl
import pyg4ometry


def Test(vis=False, interactive=False, fluka=True, writeNISTMaterials=True, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = pyg4ometry.geant4.Registry()

    # defines
    wx = pyg4ometry.gdml.Constant("wx", "1000", reg, True)
    wy = pyg4ometry.gdml.Constant("wy", "1000", reg, True)
    wz = pyg4ometry.gdml.Constant("wz", "1000", reg, True)

    # materials
    if writeNISTMaterials:
        wm = pyg4ometry.geant4.nist_material_2geant4Material("G4_Galactic", reg)
        em1 = pyg4ometry.geant4.nist_material_2geant4Material("G4_Au", reg)
        em2 = pyg4ometry.geant4.nist_material_2geant4Material("G4_Fe", reg)
    else:
        wm = pyg4ometry.geant4.MaterialPredefined("G4_Galactic")
        em1 = pyg4ometry.geant4.MaterialPredefined("G4_Au")
        em2 = pyg4ometry.geant4.MaterialPredefined("G4_Fe")

    ws = pyg4ometry.geant4.solid.Box("ws", wx, wy, wz, reg, "mm")
    es = pyg4ometry.fluka.Extruder("Magnet", length=500, registry=reg)

    r1 = es.addRegion("outer")
    es.setRegionMaterial("outer", em1)
    r1.append([-100, -100])
    r1.append([-100, 100])
    r1.append([100, 100])
    r1.append([100, -100])
    es.setRegionToOuterBoundary("outer")

    r2 = es.addRegion("pole")
    es.setRegionMaterial("pole", em2)
    r2.append([-50, -50])
    r2.append([-50, 50])
    r2.append([50, 50])
    r2.append([50, -50])

    es.buildCgalPolygons()
    es.buildGeant4Extrusions()

    # structure
    wl = pyg4ometry.geant4.LogicalVolume(ws, wm, "wl", reg)
    el = pyg4ometry.geant4.LogicalVolume(es, em1, "el", reg)
    ep = pyg4ometry.geant4.PhysicalVolume([0, 0, 0], [0, 0, 0], el, "el_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # fluka conversion
    if fluka:
        freg = pyg4ometry.convert.geant4Reg2FlukaReg(reg)

        # fluka running
        freg.addDefaults(default="PRECISIO")
        freg.addBeam(energy=10)
        freg.addBeamPos()
        freg.addUsrBin(name="bin1")
        freg.addUsrBin(name="bin2")
        freg.addLowMatAllMaterials()
        # freg.addLowPwxs()
        freg.addRandomiz()
        freg.addStart(maxPrimHistories=100)

        w = pyg4ometry.fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / "T400_extruder.inp")

    if vis:
        es.plot()
        es.plot(decompositions=True)

        v = pyg4ometry.visualisation.VtkViewerNew()
        v.addLogicalVolume(reg.getWorldVolume())
        v.buildPipelinesAppend()
        v.view(interactive=interactive)

    return es
