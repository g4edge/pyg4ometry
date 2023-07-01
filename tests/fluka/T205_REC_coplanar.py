import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import REC, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    # trivially coplanar:
    rec1 = REC("REC_BODY1",
               [0, 0, 0],
               [20, 0, 0],
               [0, 0, 5],
               [0, 10, 0], flukaregistry=freg)

    rec2 = REC("REC_BODY2",
               [5, 0, 0],
               [10, 0, 0],
               [0, 0, 2.5],
               [0, 5, 0], flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()

    z1.addIntersection(rec1)
    z1.addSubtraction(rec2)

    z2.addIntersection(rec2)

    region1 = Region("REC_REG1")
    region2 = Region("REC_REG2")

    region1.addZone(z1)
    region2.addZone(z2)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    # default is True, but to be explicit:
    greg = convert.fluka2Geant4(freg,
                                withLengthSafety=True,
                                splitDisjointUnions=False)

    wv = greg.getWorldVolume()
    wv.checkOverlaps(recursive = False, coplanar = True, debugIO = False)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(wv)
        v.view(interactive=interactive)


    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True, True)
