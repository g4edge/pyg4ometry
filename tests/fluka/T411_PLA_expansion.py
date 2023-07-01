import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import (PLA, Region, Zone, FlukaRegistry,
                              Transform, infinity)

def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    with infinity(30):

        pla1 = PLA("PLA1_BODY",
                   [0, 0, 10],
                   [0, 0, 10],
                   transform=Transform(expansion=2.0),
                   flukaregistry=freg)

        z1 = Zone()

        z1.addIntersection(pla1)

        region = Region("REG_INF")
        region.addZone(z1)

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
