import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, RCC, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()
    # I pick 20 because that's the length of the axes added below, so
    # verifying the resulting cube is of the correct length is trivial.
    rpp = RPP("RPP_BODY", 0, 20.0, 0, 20.0, 0.0, 20.0, flukaregistry=freg)
    rcc = RCC("RCC_BODY", [0.0, 0.0, 20.0], [0.0, 20.0, 0.0], 10.0, flukaregistry=freg)

    # RPP is used in the definitions of both zone1 and zone2.

    z1 = Zone()
    z1.addIntersection(rpp)
    z2 = Zone()
    z2.addIntersection(rcc)
    z2.addSubtraction(rpp)

    region = Region("REG_INF")
    region.addZone(z1)
    region.addZone(z2)

    freg.addRegion(region)
    freg.assignma("COPPER", region)
    greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T107_region_union_with_reused_bodies.inp"

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
