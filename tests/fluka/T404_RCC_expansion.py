import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RCC, Region, Zone, FlukaRegistry, Transform

def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rcc = RCC("RCC_BODY", [5, 5, 5],
              [5, 0, 0],
              5,
              transform=Transform(expansion=2.0),
              flukaregistry=freg)
    z = Zone()
    z.addIntersection(rcc)
    region = Region("RCC_REG")
    freg.assignma("COPPER", region)

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
