import pathlib as _pl
import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import REC, Region, Zone, FlukaRegistry, Transform, Writer
from pyg4ometry.fluka.directive import rotoTranslationFromTra2
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    rtrans = rotoTranslationFromTra2("recTRF", [[np.pi / 4, np.pi / 4, np.pi / 4], [0, 0, 20]])
    transform = Transform(rotoTranslation=rtrans)

    face = [0, 0, 0]  # one face is situated at (0, 0, 0).
    direction = [3, 3, 3]  # length pointing from above face in the
    # i+j+k direction.
    semiminor = [0.5, -1, 0.5]  # one axis line intercepts the y-axis, length= ~1.22
    semiminor_length = np.linalg.norm(semiminor)
    semimajor = np.cross(direction, semiminor)
    semimajor = 2 * (
        semiminor_length * semimajor / np.linalg.norm(semimajor)
    )  # Twice the length of semiminor

    rec = REC(
        "REC_BODY",
        face,
        direction,
        semiminor,
        semimajor,
        transform=transform,
        flukaregistry=freg,
    )

    z = Zone()
    z.addIntersection(rec)
    region = Region("REC_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T605_REC_rototranslation.inp"

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
