import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XEC, YZP, Region, Zone, FlukaRegistry, Transform


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()
    xec = XEC(
        "XEC_BODY",
        2.5,
        5,
        2.5,
        5,
        transform=Transform(expansion=2.0),
        flukaregistry=freg,
    )

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
