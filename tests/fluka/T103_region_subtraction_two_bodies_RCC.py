import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RCC, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rcc1 = RCC("RCC1_BODY", [0, 0, 0], [5, 5, 5], 2.5, flukaregistry=freg)
    rcc2 = RCC("RCC2_BODY", [-1, -1, -1], [6, 6, 6], 1.25, flukaregistry=freg)

    z = Zone()

    z.addIntersection(rcc1)
    z.addSubtraction(rcc2)    
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

    


    
