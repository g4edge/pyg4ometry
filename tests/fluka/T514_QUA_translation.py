import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import QUA, Region, Zone, FlukaRegistry, AABB, XYP, XZP, Transform


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    translation = Transform(translation=[0, 0, -1000])

    parabolicCylinder = QUA(
        "parab",
        0.006,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        -200,
        transform=translation,
        flukaregistry=freg,
    )

    # 1 metre long parabolic cylinder 10cm tall from base to tip.
    end1 = XYP("end1", 1000, transform=translation, flukaregistry=freg)
    end2 = XYP("end2", 0, transform=translation, flukaregistry=freg)
    end3 = XZP("end3", 100, transform=translation, flukaregistry=freg)

    z = Zone()
    z.addIntersection(parabolicCylinder)
    z.addIntersection(end1)
    z.addSubtraction(end2)
    z.addSubtraction(end3)

    region = Region("QUA_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    quaAABB = {"QUA_REG": AABB([-150.0, 100.0, -1000.0], [150.0, 200.0, 0.0])}

    greg = convert.fluka2Geant4(freg, quadricRegionAABBs=quaAABB)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(origin=[0, 0, 0], length=500)
        v.addAxes(origin=[0, 0, -1000], length=1000)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}


if __name__ == "__main__":
    Test(True, True)
