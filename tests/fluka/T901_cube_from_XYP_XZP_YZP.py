import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XYP, YZP, XZP, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting cube is of the correct length is trivial.
    xyp_lo = XYP("XYP1_BODY", 0, flukaregistry=freg)
    xyp_hi = XYP("XYP2_BODY", 20.0, flukaregistry=freg)

    xzp_lo = XZP("XZP1_BODY", 0, flukaregistry=freg)
    xzp_hi = XZP("XZP2_BODY", 20.0, flukaregistry=freg)

    yzp_lo = YZP("YZP1_BODY", 0, flukaregistry=freg)
    yzp_hi = YZP("YZP2_BODY", 20.0, flukaregistry=freg)

    z = Zone()

    z.addIntersection(xyp_hi)
    z.addSubtraction(xyp_lo)

    z.addIntersection(xzp_hi)
    z.addSubtraction(xzp_lo)

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

if __name__ == '__main__':
    Test(True, True)
