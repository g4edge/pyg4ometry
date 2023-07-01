import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, ZCC, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    rpp = RPP("RPP_BODY", -20, 20, -20, 20, -20, 20, flukaregistry=freg)
    rppsub = RPP("RPP2_BODY", -10, 10, -10, 10, -30, 30, flukaregistry=freg)

    zcc = ZCC("ZCC_BODY", 0, 0, 10, flukaregistry=freg)

    # +rpp -(+rppsub -zcc):

    z = Zone()
    z.addIntersection(rpp)

    z2 = Zone()
    z2.addIntersection(rppsub)
    z2.addSubtraction(zcc)

    # Adding zone2 as a subtraction to the first zone.
    z.addSubtraction(z2)

    region = Region("RPP_REG")

    region.addZone(z)

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True,True)
