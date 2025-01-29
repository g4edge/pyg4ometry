import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RAW, Region, Zone, FlukaRegistry, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    # What I expect to see in the visualiser is a cube formed by the
    # union of two wedeges. with sides equal to 20cm.  The mesh shows
    # the two wedges.

    raw1 = RAW(
        "RAW1_BODY",
        [0, 0, 0],  # vertex position
        [20, 0, 0],  # one transverse side.
        [0, 0, 20],  # length vector.
        [0, 20, 0],  # the other transverse side.
        flukaregistry=freg,
    )

    raw2 = RAW(
        "RAW2_BODY",
        [5, 5, 5],  # vertex position
        [5, 0, 0],  # one transverse side.
        [0, 0, 5],  # length vector.
        [0, 5, 0],  # the other transverse side.
        flukaregistry=freg,
    )

    z1 = Zone()
    z1.addIntersection(raw1)
    z1.addSubtraction(raw2)

    z2 = Zone()
    z2.addIntersection(raw2)

    region1 = Region("RAW_REG1")
    region1.addZone(z1)

    region2 = Region("RAW_REG2")
    region2.addZone(z2)

    freg.addRegion(region1)
    freg.addRegion(region2)
    freg.assignma("COPPER", region1, region2)

    # default is True, but to be explicit:
    greg = convert.fluka2Geant4(freg, withLengthSafety=True, splitDisjointUnions=False)

    wlv = greg.getWorldVolume()
    wlv.checkOverlaps(recursive=False, coplanar=True)

    outputFile = outputPath / "T208_RAW_coplanar.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes()
        v.addLogicalVolume(wlv)
        v.setRandomColours()
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
