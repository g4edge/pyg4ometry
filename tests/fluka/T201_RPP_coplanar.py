import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rpp1 = RPP("RPP_BODY1", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    rpp2 = RPP("RPP_BODY2", 2, 8, 2, 8, 2, 8, flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()

    z1.addIntersection(rpp1)
    z1.addSubtraction(rpp2)

    z2.addIntersection(rpp2)

    region1 = Region("RPP_REG1")
    region2 = Region("RPP_REG2")

    region1.addZone(z1)
    region2.addZone(z2)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    greg = convert.fluka2Geant4(freg, withLengthSafety=True)

    wlv = greg.getWorldVolume()
    wlv.checkOverlaps(recursive = False, coplanar = True, debugIO = False)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(wlv)
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True, True)
