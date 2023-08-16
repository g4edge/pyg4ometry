import pathlib as _pl
import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import REC, Region, Zone, FlukaRegistry, Transform, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    face = [0, 0, 0]
    direction = [0, 0, 10]
    semiminor = [10, 0, 0]
    semimajor = [0, 5, 0]

    rec = REC(
        "REC_BODY",
        face,
        direction,
        semiminor,
        semimajor,
        transform=Transform(expansion=2.0),
        flukaregistry=freg,
    )

    z = Zone()
    z.addIntersection(rec)
    region = Region("REC_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T404_REC_expansion.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes()
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
