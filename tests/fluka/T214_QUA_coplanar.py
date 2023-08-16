import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import QUA, Region, Zone, FlukaRegistry, AABB, XYP, XZP, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    parabolicCylinderOuter = QUA(
        "parabo",
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
        flukaregistry=freg,
    )

    parabolicCylinderInner = QUA(
        "parabi",
        0.012,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        -150,
        flukaregistry=freg,
    )

    # 1 metre long parabolic cylinder 10cm tall from base to tip.
    end1outer = XYP("end1o", 1000, flukaregistry=freg)
    end2outer = XYP("end2o", 0, flukaregistry=freg)
    end3outer = XZP("end3o", 0, flukaregistry=freg)

    end1inner = XYP("end1i", 750, flukaregistry=freg)
    end2inner = XYP("end2i", 250, flukaregistry=freg)
    end3inner = XZP("end3i", 50, flukaregistry=freg)

    # Outer parabolic cylinder
    z1 = Zone()
    z1.addIntersection(parabolicCylinderOuter)
    z1.addIntersection(end1outer)
    z1.addSubtraction(end2outer)
    z1.addSubtraction(end3outer)

    # Inner parabolic cylinder
    z2 = Zone()
    z2.addIntersection(parabolicCylinderInner)
    z2.addIntersection(end1inner)
    z2.addSubtraction(end2inner)
    z2.addSubtraction(end3inner)

    z1.addSubtraction(z2)

    r1 = Region("OUTER")
    r1.addZone(z1)

    r2 = Region("INNER")
    r2.addZone(z2)

    freg.addRegion(r1)
    freg.addRegion(r2)

    freg.assignma("IRON", r1, r2)

    quaAABB = {
        "OUTER": AABB([-200.0, 0.0, 0.0], [200, 200, 1100]),
        "INNER": AABB([-100.0, 50.0, 250], [100.0, 150.0, 850.0]),
    }

    greg = convert.fluka2Geant4(freg, quadricRegionAABBs=quaAABB)

    outputFile = outputPath / "T214_QUA_coplanar.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(origin=[0, 100, 0], length=100)
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
