import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import XYP, YZP, XZP, Region, Zone, FlukaRegistry, Writer
from pyg4ometry.fluka.body import INFINITY
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting cube is of the correct length is trivial.
    xyp_lo = XYP("XYP1_BODY", 0, flukaregistry=freg)
    xyp_hi = XYP("XYP2_BODY", 20.0, flukaregistry=freg)

    xzp_lo = XZP("XZP1_BODY", 0, flukaregistry=freg)
    xzp_hi = XZP("XZP2_BODY", 20.0, flukaregistry=freg)

    yzp_lo = YZP("YZP1_BODY", 0, flukaregistry=freg)
    yzp_hi = YZP("YZP2_BODY", 20.0, flukaregistry=freg)

    z = Zone()

    z.addIntersection(xyp_hi)
    z.addSubtraction(xyp_lo)

    z.addIntersection(xzp_hi)
    z.addSubtraction(xzp_lo)

    z.addIntersection(yzp_hi)
    z.addSubtraction(yzp_lo)

    region = Region("REG_INF")
    region.addZone(z)

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg, withLengthSafety=True, minimiseSolids=True)

    names = [
        "XYP1_BODY_e",
        "XYP2_BODY_s",
        "XZP1_BODY_e",
        "XZP2_BODY_s",
        "YZP1_BODY_e",
        "YZP2_BODY_s",
    ]

    for name in names:
        # Subtract 10 because we expect some of them to be strictly
        # smaller than INFINITY anyway because of automatic length safety.
        assert greg.solidDict[name].pX < INFINITY - 10
        assert greg.solidDict[name].pY < INFINITY - 10
        assert greg.solidDict[name].pZ < INFINITY - 10

    outputFile = outputPath / "T710_XYP_ZXP_YZP_minimiation.inp"

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
