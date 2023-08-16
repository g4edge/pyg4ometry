import pathlib as _pl
import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XYP, Region, Zone, FlukaRegistry, Transform, infinity, Writer
from pyg4ometry.fluka.directive import rotoTranslationFromTra2
import pyg4ometry.misc as _mi

import pyg4ometry.fluka.body


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    rtrans = rotoTranslationFromTra2("rppTRF", [[np.pi / 4, np.pi / 4, np.pi / 4], [0, 0, 20]])
    transform = Transform(rotoTranslation=rtrans)

    with infinity(30):
        xyp = XYP("XYP_BODY", 20.0, transform=transform, flukaregistry=freg)

        z = Zone()
        z.addIntersection(xyp)

        region = Region("REG_INF")
        region.addZone(z)

        freg.addRegion(region)
        freg.assignma("COPPER", region)
        greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T610_XYP_rototranslation.inp"

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
