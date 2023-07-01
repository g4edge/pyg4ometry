import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RCC, Region, Zone, FlukaRegistry, Transform

def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rcc = RCC("RCC_BODY",
              [20, 20, 20],
              [5, 5, 5], 2.5,
              transform=Transform(translation=[-20, -20, -20]),
              flukaregistry=freg)
    z = Zone()
    z.addIntersection(rcc)
    region = Region("RCC_REG")
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
