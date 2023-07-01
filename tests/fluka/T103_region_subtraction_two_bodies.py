import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rpp1 = RPP("RPP_BODY1", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    rpp2 = RPP("RPP_BODY2", 5, 15, 0, 10, 0, 10, flukaregistry=freg)

    z = Zone()
    z.addIntersection(rpp1)
    z.addSubtraction(rpp2)
    region = Region("RPP_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True, True)
