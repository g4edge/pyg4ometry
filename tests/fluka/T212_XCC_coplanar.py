import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XCC, YZP, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting body is of the correct length and radius
    # is trivial.
    xcc1 = XCC("XCC_BODY1", 0, 0, 20, flukaregistry=freg)
    xcc2 = XCC("XCC_BODY2", 0, 0, 10, flukaregistry=freg)

    yzp1 = YZP("YZP1_BODY", 20, flukaregistry=freg)
    yzp2 = YZP("YZP2_BODY", 0, flukaregistry=freg)

    yzp3 = YZP("YZP3_BODY", 15, flukaregistry=freg)
    yzp4 = YZP("YZP4_BODY", 5, flukaregistry=freg)

    z1 = Zone()
    z1.addIntersection(xcc1)
    z1.addIntersection(yzp1)
    z1.addSubtraction(yzp2)

    z2 = Zone()
    z2.addIntersection(xcc2)
    z2.addIntersection(yzp3)
    z2.addSubtraction(yzp4)

    z1.addSubtraction(z2)

    region1 = Region("REG_INF1")
    region2 = Region("REG_INF2")
    region1.addZone(z1)
    region2.addZone(z2)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    greg = convert.fluka2Geant4(freg, withLengthSafety=True, splitDisjointUnions=False)

    wlv = greg.getWorldVolume()
    wlv.checkOverlaps(recursive=False, coplanar=True, debugIO=False)

    outputFile = outputPath / "T212_XCC_coplanar.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(wlv)
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
