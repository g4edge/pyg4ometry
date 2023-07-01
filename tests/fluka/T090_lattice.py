import os.path

import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import (RCC, Region, Zone, FlukaRegistry,
                              RotoTranslation,
                              RecursiveRotoTranslation,
                              Transform, Lattice)
from pyg4ometry.fluka.directive import rotoTranslationFromTra2
from pyg4ometry.gdml import Writer



def Test(vis=False, interactive=False, write=False):
    freg = FlukaRegistry()

    # This is simply test/flairFluka/701_LATTICE.inp in pure python form.

    rtrans = RecursiveRotoTranslation(
        "rtrans",
        [RotoTranslation("rtrans", translation=[0, -20, -300]),
         RotoTranslation("rtrans", axis="x", azimuth=-45)])

    target = RCC("target", [0.0, 0.0, -50.], [0.0, 0.0, 100.], 50.,
                 flukaregistry=freg)
    ztarget = Zone()
    ztarget.addIntersection(target)

    targRepl = RCC("targRepl", [0.0, 0.0, -50.], [0.0, 0.0, 100.], 50.,
                   transform=Transform(rotoTranslation=rtrans,
                                       invertRotoTranslation=True))
    zrepl = Zone()
    zrepl.addIntersection(targRepl)

    targetRegion = Region("TARGET")
    targetRegion.addZone(ztarget)
    replicaRegion = Region("REPLICA")
    replicaRegion.addZone(zrepl)


    lattice = Lattice(replicaRegion, rotoTranslation=rtrans, flukaregistry=freg)

    freg.addRegion(targetRegion)

    freg.assignma("COPPER", targetRegion)

    greg = convert.fluka2Geant4(freg, worldDimensions=[100, 100, 100])

    assert len(greg.logicalVolumeDict) == 2

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    if write:
        w = Writer()
        w.addDetector(greg)
        dirname = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.basename(__file__)
        name, _ = os.path.splitext(__file__)

        gdml_name = "{}.gdml".format(name)
        gmad_name = "{}.gmad".format(name)
        w.write(os.path.join(dirname, gdml_name))
        w.writeGMADTesterNoBeamline(os.path.join(dirname, gmad_name), gdml_name)


    return {"testStatus": True,
            "logicalVolume": greg.getWorldVolume(),
            "vtkViewer":v}

if __name__ == '__main__':
    Test(True, True, True)

