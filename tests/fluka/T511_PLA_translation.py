import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import PLA, Region, Zone, FlukaRegistry, Transform, infinity, Writer
import pyg4ometry.fluka.body
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    with infinity(30):
        pla1 = PLA(
            "PLA1_BODY",
            [1, 1, 1],
            [20, 20.0, 20],
            transform=Transform(translation=[-20, -20, -20]),
            flukaregistry=freg,
        )

        z1 = Zone()

        z1.addIntersection(pla1)

        region = Region("REG_INF")
        region.addZone(z1)

        freg.addRegion(region)
        freg.assignma("COPPER", region)

        greg = convert.fluka2Geant4(freg)

    outputFile = outputPath / "T511_PLA_translation.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

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
