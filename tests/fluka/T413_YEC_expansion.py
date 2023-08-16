import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import YEC, XZP, Region, Zone, FlukaRegistry, Transform, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting body is of the correct length and radius
    # is trivial.

    # Bigger semi axis is z, smaller is x
    yec = YEC(
        "YEC_BODY",
        2.5,
        5,
        2.5,
        5,
        transform=Transform(expansion=2.0),
        flukaregistry=freg,
    )

    xzp_hi = XZP("XZP1_BODY", 20, flukaregistry=freg)
    xzp_lo = XZP("XZP2_BODY", 0, flukaregistry=freg)

    z = Zone()

    z.addIntersection(yec)
    z.addIntersection(xzp_hi)
    z.addSubtraction(xzp_lo)

    region = Region("REG_INF")
    region.addZone(z)

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T413_YEC_expansion.inp"

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
