import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    rpp1 = RPP("RPP_BODY1", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    rpp2 = RPP("RPP_BODY2", 5, 15, 0, 10, 0, 10, flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()

    z1.addIntersection(rpp1)
    z2.addIntersection(rpp2)

    region = Region("RPP_REG")
    region.addZone(z1)
    region.addZone(z2)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T104_region_union_two_zones.inp"

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
