import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import QUA, Region, Zone, FlukaRegistry, AABB, XYP, XZP, Transform, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    expansion = Transform(expansion=0.5)

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
        transform=expansion,
        flukaregistry=freg,
    )

    # 1 metre long parabolic cylinder 10cm tall from base to tip.
    end1 = XYP("end1", 1000, transform=expansion, flukaregistry=freg)
    end2 = XYP("end2", 0, transform=expansion, flukaregistry=freg)
    end3 = XZP("end3", 100, transform=expansion, flukaregistry=freg)

    z = Zone()
    z.addIntersection(parabolicCylinder)
    z.addIntersection(end1)
    z.addSubtraction(end2)
    z.addSubtraction(end3)

    region = Region("QUA_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    quaAABB = {"QUA_REG": AABB([-70.0, 50.0, 0], [70.0, 100.0, 500.0])}

    greg = convert.fluka2Geant4(freg, quadricRegionAABBs=quaAABB)

    outputFile = outputPath / "T414_QUA_expansion.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(origin=[0, 0, 0], length=500)  # XYP end1's position in z.
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
