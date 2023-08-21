import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import RPP, Region, Zone, FlukaRegistry, Material, Writer
import pyg4ometry.misc as _mi


def Test(vis=False, interactive=False, outputPath=None, refFilePath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    density = 2.48
    z = 87
    massNumber = None  # i.e. determine it automatically given z.
    fr = Material("FRANCIUM", z, density, massNumber=massNumber, flukaregistry=freg)
    card = fr.toCards()[0]
    assert card.keyword == "MATERIAL"
    assert card.what1 == z
    assert card.what3 == density

    rpp = RPP("RPP_BODY", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    zone = Zone()
    zone.addIntersection(rpp)
    region = Region("RPP_REG")  # should this be string or

    # material instance or maybe either?
    region.addZone(zone)
    freg.addRegion(region)

    freg.addMaterialAssignments(fr, region)

    greg = convert.fluka2Geant4(freg)

    lvmat = greg.logicalVolumeDict["RPP_REG_lv"].material
    assert lvmat.name == "FRANCIUM"
    assert lvmat.density == density
    assert lvmat.atomic_number == z
    assert lvmat.atomic_weight == 223
    greg.getWorldVolume().clipSolid()

    outputFile = outputPath / "T803_material_element.inp"

    w = Writer()
    w.addDetector(freg)
    w.write(outputFile)

    _mi.compareNumericallyWithAssert(refFilePath, outputFile)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
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
