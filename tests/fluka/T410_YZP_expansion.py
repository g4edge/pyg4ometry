import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import YZP, Region, Zone, FlukaRegistry, Transform, infinity, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    with infinity(30):
        yzp = YZP("YZP_BODY", 10.0, transform=Transform(expansion=2.0), flukaregistry=freg)

        z = Zone()
        z.addIntersection(yzp)

        region = Region("REG_INF")
        region.addZone(z)

        freg.addRegion(region)
        freg.assignma("COPPER", region)

        greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T410_YZP_expansion.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

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
