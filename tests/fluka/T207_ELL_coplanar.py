import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import ELL, Region, Zone, FlukaRegistry, Three, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # ellipsoid with major axes poining in the y direction, total
    # legnth=20, offset in x.

    ell1 = ELL(
        "ELL1_BODY",
        [20, 5, 0],  # focus1
        [20, 15, 0],  # focus2
        20,  # length
        flukaregistry=freg,
    )

    ell2 = ELL(
        "ELL2_BODY",
        [20, 7.5, 0],  # focus1
        [20, 12.5, 0],  # focus2
        15,  # length
        flukaregistry=freg,
    )

    z1 = Zone()
    z1.addIntersection(ell1)
    z1.addSubtraction(ell2)

    z2 = Zone()
    z2.addIntersection(ell2)

    region = Region("ELL_REG")
    region.addZone(z1)
    region.addZone(z2)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)
    wlv = greg.getWorldVolume()
    wlv.checkOverlaps(recursive=False, coplanar=True, debugIO=False)

    outputFile = outputPath / "T207_ELL_coplanar.inp"

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
