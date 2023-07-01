import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import REC, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    face = [0, 0, 0] # one face is situated at (0, 0, 0).
    direction = [3, 3, 3] # length pointing from above face in the
                          # i+j+k direction.
    semiminor = [0.5, -1, 0.5] # one axis line intercepts the y-axis, length= ~1.22
    semiminor_length = np.linalg.norm(semiminor)
    semimajor = np.cross(direction, semiminor)
    semimajor = 2 * (semiminor_length * semimajor /
                     np.linalg.norm(semimajor)) # Twice the length of semiminor

    rec = REC("REC_BODY",
              face,
              direction,
              semiminor,
              semimajor,
              flukaregistry=freg)

    z = Zone()
    z.addIntersection(rec)
    region = Region("REC_REG")
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
