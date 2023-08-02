import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import WED, Region, Zone, FlukaRegistry

import numpy as np


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    # What I expect to see in the visualiser is a cube formed by the
    # union of two wedeges. with sides equal to 20cm.  The mesh shows
    # the two wedges.

    wed1 = WED(
        "WED1_BODY",
        [0, 0, 0],  # vertex position
        [20, 0, 0],  # one transverse side.
        [0, 0, 20],  # length vector.
        [0, 20, 0],  # the other transverse side.
        flukaregistry=freg,
    )

    wed2 = WED(
        "WED2_BODY",
        [5, 5, 5],  # vertex position
        [5, 0, 0],  # one transverse side.
        [0, 0, 5],  # length vector.
        [0, 5, 0],  # the other transverse side.
        flukaregistry=freg,
    )

    z1 = Zone()
    z1.addIntersection(wed1)
    z1.addSubtraction(wed2)

    z2 = Zone()
    z2.addIntersection(wed2)

    region1 = Region("WED_REG1")
    region1.addZone(z1)

    region2 = Region("WED_REG2")
    region2.addZone(z2)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    # default is True, but to be explicit:
    greg = convert.fluka2Geant4(freg, withLengthSafety=True, splitDisjointUnions=False)

    wlv = greg.getWorldVolume()
    wlv.checkOverlaps(recursive=False, coplanar=True, debugIO=False)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes()
        v.addLogicalVolume(wlv)
        v.setRandomColours()
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}


if __name__ == "__main__":
    Test(True, True)
