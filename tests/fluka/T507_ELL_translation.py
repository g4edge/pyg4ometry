import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import ELL, Region, Zone, FlukaRegistry, Transform, Three, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # ellipsoid with major axes poining in the y direction, total
    # legnth=20, offset in x.
    focus1 = Three([20, 5, 0])
    focus2 = Three([20, 15, 0])
    length = 20

    ell = ELL(
        "ELL_BODY",
        focus1,
        focus2,
        length,
        transform=Transform(translation=[-20, -20, 20]),
        flukaregistry=freg,
    )

    z = Zone()
    z.addIntersection(ell)
    region = Region("ELL_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T507_ELL_translation.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(20, [0, 0, 0])

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
