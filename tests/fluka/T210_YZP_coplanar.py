import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XYP, XZP, YZP, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # the first box..
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting cube is of the correct length is trivial.
    xyp_lo1 = XYP("XYP1_BODY1", 0, flukaregistry=freg)
    xyp_hi1 = XYP("XYP2_BODY1", 20.0, flukaregistry=freg)
    xzp_lo1 = XZP("XZP1_BODY1", 0, flukaregistry=freg)
    xzp_hi1 = XZP("XZP2_BODY1", 20.0, flukaregistry=freg)
    yzp_lo1 = YZP("YZP1_BODY1", 0, flukaregistry=freg)
    yzp_hi1 = YZP("YZP2_BODY1", 20.0, flukaregistry=freg)

    # the second box...
    xyp_lo2 = XYP("XYP1_BODY2", 5, flukaregistry=freg)
    xyp_hi2 = XYP("XYP2_BODY2", 15.0, flukaregistry=freg)
    xzp_lo2 = XZP("XZP1_BODY2", 5, flukaregistry=freg)
    xzp_hi2 = XZP("XZP2_BODY2", 15.0, flukaregistry=freg)
    yzp_lo2 = YZP("YZP1_BODY2", 5, flukaregistry=freg)
    yzp_hi2 = YZP("YZP2_BODY2", 15.0, flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()
    z3 = Zone()

    z1.addIntersection(xyp_hi1)
    z1.addSubtraction(xyp_lo1)
    z1.addIntersection(xzp_hi1)
    z1.addSubtraction(xzp_lo1)
    z1.addIntersection(yzp_hi1)
    z1.addSubtraction(yzp_lo1)

    z2.addIntersection(xyp_hi2)
    z2.addSubtraction(xyp_lo2)
    z2.addIntersection(xzp_hi2)
    z2.addSubtraction(xzp_lo2)
    z2.addIntersection(yzp_hi2)
    z2.addSubtraction(yzp_lo2)

    z1.addSubtraction(z2)
    z3.addIntersection(z2)

    region1 = Region("REG_INF1")
    region2 = Region("REG_INF2")
    region1.addZone(z1)
    region2.addZone(z3)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    greg = convert.fluka2Geant4(freg, withLengthSafety=True)

    wlv = greg.getWorldVolume()

    wlv.checkOverlaps(recursive=False, coplanar=True)

    outputFile = outputPath / "T210_YZP_coplanar.inp"

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
