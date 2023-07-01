import numpy as np
import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import (QUA, Region, Zone, FlukaRegistry,
                              AABB, XYP, XZP,
                              Transform)
from pyg4ometry.fluka.directive import rotoTranslationFromTra2

def Test(vis=False, interactive=False) :
    freg = FlukaRegistry()


    rtrans = rotoTranslationFromTra2("quaTRF",
                                     [[0, 0, np.pi/4],
                                      [0, 0, 0]])
    transform = Transform(rotoTranslation=rtrans)

    parabolicCylinder = QUA("parab",
                            0.006, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -200,
                            transform=transform,
                            flukaregistry=freg)

    # 1 metre long parabolic cylinder 10cm tall from base to tip.
    end1 = XYP("end1", 1000, flukaregistry=freg, transform=transform)
    end2 = XYP("end2",  0, flukaregistry=freg, transform=transform)
    end3 = XZP("end3", 100, flukaregistry=freg, transform=transform)

    z = Zone()
    z.addIntersection(parabolicCylinder)
    z.addIntersection(end1)
    z.addSubtraction(end2)
    z.addSubtraction(end3)

    region = Region("QUA_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    quaAABB = {"QUA_REG": AABB([-190., 40., 0], [50., 200., 1000.])}

    greg = convert.fluka2Geant4(freg, quadricRegionAABBs=quaAABB)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(origin=[0, 100, 0], length=100)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer":v}

if __name__ == '__main__':
    Test(True, True)
