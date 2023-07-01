import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import (PLA, Region, Zone, FlukaRegistry,
                              Transform, infinity)
from pyg4ometry.fluka.directive import rotoTranslationFromTra2

def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rtrans = rotoTranslationFromTra2("plaTRF",
                                     [[np.pi/4, np.pi/4, np.pi/4],
                                      [0, 0, 20]])

    transform = Transform(rotoTranslation=rtrans)

    with infinity(30):

        pla1 = PLA("PLA1_BODY",
                   [1, 1, 1],
                   [0, 0.0, 0],
                   transform=transform,
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
