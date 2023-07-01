import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import TRC, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    # big face (r=5) is at the origin, smaller face (r=2) is at [5, 5, 5].
    trc = TRC("TRC_BODY", [0, 0, 0], [5, 5, 5], 5, 2, flukaregistry=freg)
    # big face (r=5) is at the [4, 4, 4]    , smaller face (r=2) is at
    # [9, 9, 9].
    trc2 = TRC("TRC2_BODY", [4, 4, 4], [5, 5, 5], 5, 2, flukaregistry=freg)

    z = Zone()
    z2 = Zone()
    z.addIntersection(trc)
    z2.addIntersection(trc2)

    region = Region("TRC_REG")
    region.addZone(z)
    region.addZone(z2)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes()
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True, True)
