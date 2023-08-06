import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import YZP, Region, Zone, FlukaRegistry, Transform, infinity, Writer


def Test(vis=False, interactive=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    with infinity(30):
        yzp = YZP(
            "YZP_BODY",
            20.0,
            transform=Transform(translation=[-20, 0, 0]),
            flukaregistry=freg,
        )

        z = Zone()
        z.addIntersection(yzp)

        region = Region("REG_INF")
        region.addZone(z)

        freg.addRegion(region)
        freg.assignma("COPPER", region)

        greg = convert.fluka2Geant4(freg)

    w = Writer()
    w.addDetector(freg)
    w.write(outputPath / "T510_YZP_translation.inp")

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {
        "testStatus": True,
        "logicalVolume": greg.getWorldVolume(),
        "vtkViewer": v,
        "flukaRegistry": freg,
        "geant4Registry": greg,
    }


if __name__ == "__main__":
    Test(True, True)
