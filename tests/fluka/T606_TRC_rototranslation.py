import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import TRC, Region, Zone, FlukaRegistry, Transform
from pyg4ometry.fluka.directive import rotoTranslationFromTra2


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rtrans = rotoTranslationFromTra2("trcTRF", [[np.pi / 4, np.pi / 4, np.pi / 4], [0, 0, 20]])
    transform = Transform(rotoTranslation=rtrans)

    # big face (r=5) is at the origin, smaller face (r=2) is at [5, 5, 5].
    trc = TRC("TRC_BODY", [0, 0, 0], [5, 5, 5], 5, 2, transform=transform, flukaregistry=freg)
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


if __name__ == "__main__":
    Test(True, True)
