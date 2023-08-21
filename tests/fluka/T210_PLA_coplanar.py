import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import PLA, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # Bigger cube.
    pla_a1 = PLA("PLA_A1_BODY", [0, 0, 20], [0, 0, 20], flukaregistry=freg)
    pla_a2 = PLA("PLA_A2_BODY", [0, 0, 20], [0, 0, 0], flukaregistry=freg)
    pla_b1 = PLA("PLA_B1_BODY", [0, 20, 0], [0, 20, 0], flukaregistry=freg)
    pla_b2 = PLA("PLA_B2_BODY", [0, 20, 0], [0, 0, 0], flukaregistry=freg)
    pla_c1 = PLA("PLA_C1_BODY", [20, 0, 0], [20, 0, 0], flukaregistry=freg)
    pla_c2 = PLA("PLA_C2_BODY", [20, 0, 0], [0, 0, 0], flukaregistry=freg)

    # smaller cube.
    pla_d1 = PLA("PLA_D1_BODY", [0, 0, 20], [0, 0, 15], flukaregistry=freg)
    pla_d2 = PLA("PLA_D2_BODY", [0, 0, 20], [0, 0, 5.0], flukaregistry=freg)
    pla_e1 = PLA("PLA_e1_BODY", [0, 20, 0], [0, 15, 0], flukaregistry=freg)
    pla_e2 = PLA("PLA_e2_BODY", [0, 20, 0], [0, 5.0, 0], flukaregistry=freg)
    pla_f1 = PLA("PLA_f1_BODY", [20, 0, 0], [15, 0, 0], flukaregistry=freg)
    pla_f2 = PLA("PLA_f2_BODY", [20, 0, 0], [5, 0, 0], flukaregistry=freg)

    z1 = Zone()
    z2 = Zone()

    # Box1:
    z1.addIntersection(pla_a1)
    z1.addSubtraction(pla_a2)
    z1.addIntersection(pla_b1)
    z1.addSubtraction(pla_b2)
    z1.addIntersection(pla_c1)
    z1.addSubtraction(pla_c2)

    # box 2
    z2.addIntersection(pla_d1)
    z2.addSubtraction(pla_d2)
    z2.addIntersection(pla_e1)
    z2.addSubtraction(pla_e2)
    z2.addIntersection(pla_f1)
    z2.addSubtraction(pla_f2)
    # make hole in box1 with box2
    z1.addSubtraction(z2)

    region1 = Region("REG_INF1")
    region1.addZone(z1)

    # # fill hole with box.
    region2 = Region("REG_INF2")
    region2.addZone(z2)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    greg = convert.fluka2Geant4(freg, withLengthSafety=True, splitDisjointUnions=False)

    wlv = greg.getWorldVolume()
    wlv.checkOverlaps(recursive=False, coplanar=True, debugIO=False)

    outputFile = outputPath / "T210_PLA_coplanar.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(wlv)
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
