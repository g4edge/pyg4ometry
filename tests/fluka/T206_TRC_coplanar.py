import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import TRC, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # trivially coplanar:
    trc1 = TRC("TRC_BODY1", [0, 0, 0], [5, 5, 5], 5, 2, flukaregistry=freg)
    trc2 = TRC("TRC_BODY2", [10, 10, 10], [-5, -5, -5], 5, 2, flukaregistry=freg)
    trc3 = TRC("TRC_BODY3", [10, 10, 10], [5, 5, 5], 5, 2, flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()
    z3 = Zone()

    z1.addIntersection(trc1)
    z2.addIntersection(trc2)
    z3.addIntersection(trc3)

    region1 = Region("TRC_REG1")
    region2 = Region("TRC_REG2")
    region3 = Region("TRC_REG3")

    region1.addZone(z1)
    region2.addZone(z2)
    region3.addZone(z3)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2, region3)
    freg.addRegion(region3)

    # default is True, but to be explicit:
    greg = convert.fluka2Geant4(freg, withLengthSafety=True, splitDisjointUnions=False)

    wv = greg.getWorldVolume()
    wv.checkOverlaps(recursive=False, coplanar=True)

    outputFile = outputPath / "T206_TRC_coplanar.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(wv)
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
