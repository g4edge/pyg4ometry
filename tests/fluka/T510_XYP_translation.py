import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XZP, Region, Zone, FlukaRegistry, Transform, infinity


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    with infinity(30):
        xzp = XZP(
            "XZP_BODY",
            20.0,
            transform=Transform(translation=[0, -20, 0]),
            flukaregistry=freg,
        )

        z = Zone()
        z.addIntersection(xzp)

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
