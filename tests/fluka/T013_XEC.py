import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XEC, YZP, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting body is of the correct length and radius
    # is trivial.

    # Bigger semi axis is y, smaller is z
    xec = XEC("XEC_BODY", 0, 0, 20, 10, flukaregistry=freg)

    yzp_hi = YZP("YZP1_BODY", 20, flukaregistry=freg)
    yzp_lo = YZP("YZP2_BODY", 0, flukaregistry=freg)

    z = Zone()

    z.addIntersection(xec)
    z.addIntersection(yzp_hi)
    z.addSubtraction(yzp_lo)

    region = Region("REG_INF")
    region.addZone(z)

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


if __name__ == "__main__":
    Test(True, True)
