import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RAW, Region, Zone, FlukaRegistry


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    # What I expect to see in the visualiser is a cube formed by the
    # union of two wedeges. with sides equal to 20cm.  The mesh shows
    # the two wedges.

    raw1 = RAW("RAW1_BODY",
              [20, 20, 20], # vertex position
              [-20, 0, 0], # one transverse side.
              [0, 0, -20], # the other transverse side.
              [0, -20, 0], # length vector.
              flukaregistry=freg)

    raw2 = RAW("RAW2_BODY",
               [0, 0, 0],
               [20, 0, 0], # one transverse side.
               [0, 0, 20], # the other transverse side.
               [0, 20, 0], # length vector.
               flukaregistry=freg)

    # better test please...?

    z1 = Zone()
    z1.addIntersection(raw1)

    z2 = Zone()
    z2.addIntersection(raw2)

    region = Region("RAW_REG")
    region.addZone(z1)
    region.addZone(z2)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes()
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}

if __name__ == '__main__':
    Test(True, True)
