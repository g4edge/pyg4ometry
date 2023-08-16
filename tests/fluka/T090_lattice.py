import pathlib as _pl
import os.path

import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import (
    RCC,
    Region,
    Zone,
    FlukaRegistry,
    RotoTranslation,
    RecursiveRotoTranslation,
    Transform,
    Lattice,
    Writer,
)
from pyg4ometry.fluka.directive import rotoTranslationFromTra2
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # This is simply test/flairFluka/701_LATTICE.inp in pure python form.

    rtrans = RecursiveRotoTranslation(
        "rtrans",
        [
            RotoTranslation("rtrans", translation=[0, -20, -300]),
            RotoTranslation("rtrans", axis="x", azimuth=-45),
        ],
    )

    target = RCC("target", [0.0, 0.0, -50.0], [0.0, 0.0, 100.0], 50.0, flukaregistry=freg)
    ztarget = Zone()
    ztarget.addIntersection(target)

    targRepl = RCC(
        "targRepl",
        [0.0, 0.0, -50.0],
        [0.0, 0.0, 100.0],
        50.0,
        transform=Transform(rotoTranslation=rtrans, invertRotoTranslation=True),
        flukaregistry=freg,
    )

    zrepl = Zone()
    zrepl.addIntersection(targRepl)

    targetRegion = Region("TARGET")
    targetRegion.addZone(ztarget)
    replicaRegion = Region("REPLICA")
    replicaRegion.addZone(zrepl)

    lattice = Lattice(replicaRegion, rotoTranslation=rtrans, flukaregistry=freg)

    freg.addRegion(targetRegion)
    # freg.addRegion(replicaRegion)

    freg.assignma("COPPER", targetRegion)

    greg = convert.fluka2Geant4(freg, worldDimensions=[100, 100, 100])
    # assert len(greg.logicalVolumeDict) == 2

    outputFile = outputPath / "T090_lattice.inp"

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
    Test(True, True, True)
