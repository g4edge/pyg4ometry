import os.path

import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry, Transform
from pyg4ometry.fluka.directive import rotoTranslationFromTra2
from pyg4ometry.gdml import Writer


def Test(vis=False, interactive=False, write=False):
    freg = FlukaRegistry()

    rtrans = rotoTranslationFromTra2("rppTRF",
                                     [[np.pi/4, np.pi/4, np.pi/4],
                                      [0, 0, 20]])
    transform = Transform(rotoTranslation=rtrans)

    rpp = RPP("RPP_BODY", 0, 10, 0, 10, 0, 10,
              transform=transform,
              flukaregistry=freg)

    z = Zone()
    z.addIntersection(rpp)
    region = Region("RPP_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg, worldDimensions=[100, 100, 100])

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
