import logging

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import (XZP, YZP, XYP, PLA, RPP, Region, Zone,
                              FlukaRegistry)

def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rpp = RPP("RPP_BODY", 0, 10, 0, 10, 0, 10, flukaregistry=freg)

    # logging.getLogger("pyg4ometry.convert.fluka2Geant4").setLevel(logging.DEBUG)

    faraway = 10000

    xzp = XZP("XZP", faraway, flukaregistry=freg)
    xzpsub = XZP("XZPsub", -faraway, flukaregistry=freg)
    yzp = YZP("YZP", faraway, flukaregistry=freg)
    yzpsub = YZP("YZPsub", -faraway, flukaregistry=freg)
    xyp = XYP("XYP", faraway, flukaregistry=freg)
    xypsub = XYP("XYPsub", -faraway, flukaregistry=freg)

    pla = PLA("PLA", [1, 1, 1],
              [faraway, faraway, faraway],
              flukaregistry=freg)
    plasub = PLA("PLAsub", [1, 1, 1], [-faraway, -faraway, -faraway],
                 flukaregistry=freg) 


    plaDoesIntersect = PLA("PLAint", [1, 1, 1], [3, 3, 3],
                           flukaregistry=freg)
    

    z = Zone()
    z.addIntersection(rpp)
    z.addIntersection(xyp)
    z.addIntersection(xzp)
    z.addIntersection(yzp)
    z.addIntersection(pla)
    
    z.addIntersection(plaDoesIntersect)

    z.addSubtraction(xzpsub)
    z.addSubtraction(yzpsub)
    z.addSubtraction(xypsub)
    z.addSubtraction(plasub)

    region = Region("RPP_REG")
    region.addZone(z)

    assert len(region.bodies()) == 10

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    assert len(greg.solidDict) == 4 # world, rpp, plaDoesInt, and rpp+plaDoesInt

    greg.getWorldVolume().clipSolid()

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer":v}

if __name__ == '__main__':
    Test(True, True)
