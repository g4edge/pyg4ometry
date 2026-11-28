import textwrap

import pytest

from pyg4ometry import config, convert, fluka


@pytest.fixture(autouse=True)
def _noMeshing(monkeypatch):
    # Only the materials are under test, so skip the slow meshing.
    monkeypatch.setattr(config, "doMeshing", False)


def _addBoxRegion(freg, material, name="REG"):
    zone = fluka.Zone()
    zone.addIntersection(
        fluka.RPP(f"{name}BOX", 0, 10, 0, 10, 0, 10, flukaregistry=freg)
    )
    region = fluka.Region(name)
    region.addZone(zone)
    freg.addRegion(region)
    freg.assignma(material, region)


def _componentNames(greg):
    return {c[0].name for c in greg.logicalVolumeDict["REG_lv"].material.components}


def test_redefined_builtin_compound_of_later_element():
    # Redefining a builtin keeps its early position in freg.materials, so the compound
    # comes before the user element it is made of. Converting in dict order then failed
    # with a KeyError on the element.
    freg = fluka.FlukaRegistry()
    deut = fluka.Material("DEUTER", 1, 0.169, massNumber=2, flukaregistry=freg)
    oxygen = freg.getMaterial("OXYGEN")
    fluka.Compound(
        "WATER",
        1.1,
        [(deut, 2.0), (oxygen, 1.0)],
        fractionType="atomic",
        flukaregistry=freg,
    )
    names = list(freg.materials)
    assert names.index("WATER") < names.index("DEUTER")

    _addBoxRegion(freg, "WATER")
    greg = convert.fluka2Geant4(freg)

    assert len(_componentNames(greg)) == 2


def test_redefined_builtin_compound_of_later_element_from_file(tmp_path):
    # As above, but read from a FLUKA input file, which is how it is met in the wild.
    # The reader orders materials by dependency, but the registry still keeps the
    # builtin's position for WATER.
    path = tmp_path / "heavywater.inp"
    path.write_text(
        textwrap.dedent(
            """\
            TITLE
            Heavy water
            FREE
            GEOBEGIN, , , , , , , COMBNAME
            0 0
            RPP BOX 0 1 0 1 0 1
            END
            REG 5 +BOX
            END
            GEOEND
            MATERIAL, 1., 2.014, 0.169, , , 2., DEUTER
            MATERIAL, , , 1.1, , , , WATER
            COMPOUND, 2.0, DEUTER, 1.0, OXYGEN, , , WATER
            ASSIGNMA, WATER, REG
            STOP
            """
        )
    )
    freg = fluka.Reader(str(path)).flukaregistry

    greg = convert.fluka2Geant4(freg)

    assert len(_componentNames(greg)) == 2


def test_redefined_builtin_compound_of_later_compound():
    # Converting all elements first does not help when the redefined builtin is made of
    # a user compound that comes later in freg.materials.
    freg = fluka.FlukaRegistry()
    deut = fluka.Material("DEUTER", 1, 0.169, massNumber=2, flukaregistry=freg)
    oxygen = freg.getMaterial("OXYGEN")
    heavy = fluka.Compound(
        "HEAVYH2O",
        1.1,
        [(deut, 2.0), (oxygen, 1.0)],
        fractionType="atomic",
        flukaregistry=freg,
    )
    fluka.Compound(
        "WATER", 1.05, [(heavy, 1.0)], fractionType="mass", flukaregistry=freg
    )

    _addBoxRegion(freg, "WATER")
    greg = convert.fluka2Geant4(freg)

    assert len(_componentNames(greg)) == 1


def test_redefined_builtin_used_by_earlier_compound():
    # A compound built with the original CARBON builtin, which is then redefined with a
    # different density. Both the compound part and a region using CARBON directly must
    # get the redefinition, not the builtin G4 material.
    freg = fluka.FlukaRegistry()
    builtinCarbon = freg.getMaterial("CARBON")
    oxygen = freg.getMaterial("OXYGEN")
    fluka.Compound(
        "MIX",
        1.5,
        [(builtinCarbon, 1.0), (oxygen, 1.0)],
        fractionType="mass",
        flukaregistry=freg,
    )
    fluka.Material("CARBON", 6, 2.0, flukaregistry=freg)  # Density in g/cm3.

    _addBoxRegion(freg, "MIX", name="MIXREG")
    _addBoxRegion(freg, "CARBON", name="CREG")
    greg = convert.fluka2Geant4(freg)

    carbon = greg.logicalVolumeDict["CREG_lv"].material
    assert carbon.name == "CARBON"
    assert carbon.density == 2.0
    mixParts = {
        c[0].name: c[0] for c in greg.logicalVolumeDict["MIXREG_lv"].material.components
    }
    assert mixParts["CARBON"] is carbon
