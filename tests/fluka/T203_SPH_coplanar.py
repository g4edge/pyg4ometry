import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import SPH, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    sph1 = SPH("SPH_BODY1", [0, 0, 0], 10, flukaregistry=freg)
    sph2 = SPH("SPH_BODY2", [0, 0, 0], 5, flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()

    z1.addIntersection(sph1)
    z1.addSubtraction(sph2)

    z2.addIntersection(sph2)

    region1 = Region("SPH_REG1")
    region2 = Region("SPH_REG2")

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
        v.addAxes()
        v.addLogicalVolume(wlv)
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True, True)
