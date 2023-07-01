import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import TRC, Region, Zone, FlukaRegistry, Transform


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    trc = TRC("TRC_BODY",
              [5, 0, 0], [5, 0, 0], 10, 5,
              transform=Transform(expansion=2.0),
              flukaregistry=freg)
    z = Zone()
    z.addIntersection(trc)
    region = Region("TRC_REG")
    region.addZone(z)
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
