import os as _os

import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import pyg4ometry.gdml as _gdml
from pyg4ometry.convert import fluka2Geant4 as _fluka2Geant4
import pyg4ometry.geant4.solid


def _pj(filename):
    """
    Append the absolute path to *this* directory to the filename so the tests
    can be ran from anywhere
    """
    return _os.path.join(_os.path.dirname(__file__), filename)


def flairLoadWriteTest(fileName, vis=True, interactive=False, quadricRegionAABBs=None):
    r = _fluka.Reader(_pj(fileName))

    greg = _fluka2Geant4(r.flukaregistry, quadricRegionAABBs=quadricRegionAABBs)

    wlv = greg.getWorldVolume()

    if vis:
        v = _vi.VtkViewer()
        v.addAxes(length=20)
        wlv.checkOverlaps()
        v.addLogicalVolume(wlv)
        v.view(interactive)

    w = _gdml.Writer()
    w.addDetector(greg)

    # TODO write to temporary directory
    # gdmlFileName = fileName.replace(".inp", ".gdml")
    # gmadFileName  = fileName.replace(".inp", ".gmad")
    # w.write(_os.path.join(_os.path.dirname(__file__), gdmlFileName))
    # w.writeGmadTester(_os.path.join(_os.path.dirname(__file__),gmadFileName),gdmlFileName)

    return r.flukaregistry, greg


def test_FlairLoad_T001_RPP(testdata):
    flairLoadWriteTest(testdata["fluka/001_RPP.inp"], False, False)


def test_FlairLoad_T002_BOX(testdata):
    flairLoadWriteTest(testdata["fluka/002_BOX.inp"], False, False)


def test_FlairLoad_T003_SPH(testdata):
    flairLoadWriteTest(testdata["fluka/003_SPH.inp"], False, False)


def test_FlairLoad_T004_RCC(testdata):
    flairLoadWriteTest(testdata["fluka/004_RCC.inp"], False, False)


def test_FlairLoad_T005_REC(testdata):
    flairLoadWriteTest(testdata["fluka/005_REC.inp"], False, False)


def test_FlairLoad_T006_TRC(testdata):
    flairLoadWriteTest(testdata["fluka/006_TRC.inp"], False, False)


def test_FlairLoad_T007_ELL(testdata):
    flairLoadWriteTest(testdata["fluka/007_ELL.inp"], False, False)


def test_FlairLoad_T009_ARB(testdata):
    flairLoadWriteTest(testdata["fluka/009_ARB.inp"], False, False)


def test_FlairLoad_T009_ARB_cube_anticlockwise(testdata):
    flairLoadWriteTest(testdata["fluka/009_ARB_cube_anticlockwise.inp"], False, False)


def test_FlairLoad_T009_ARB_cube_clockwise(testdata):
    flairLoadWriteTest(testdata["fluka/009_ARB_cube_clockwise.inp"], False, False)


def test_FlairLoad_T011_XYP(testdata):
    flairLoadWriteTest(testdata["fluka/011_XYP.inp"], False, False)


def test_FlairLoad_T012_XZP(testdata):
    flairLoadWriteTest(testdata["fluka/012_XZP.inp"], False, False)


def test_FlairLoad_T013_YZP(testdata):
    flairLoadWriteTest(testdata["fluka/013_YZP.inp"], False, False)


def test_FlairLoad_T014_PLA(testdata):
    flairLoadWriteTest(testdata["fluka/014_PLA.inp"], False, False)


def test_FlairLoad_T015_XCC(testdata):
    flairLoadWriteTest(testdata["fluka/015_XCC.inp"], False, False)


def test_FlairLoad_T016_YCC(testdata):
    flairLoadWriteTest(testdata["fluka/016_YCC.inp"], False, False)


def test_FlairLoad_T017_ZCC(testdata):
    flairLoadWriteTest(testdata["fluka/017_ZCC.inp"], False, False)


def test_FlairLoad_T018_XEC(testdata):
    flairLoadWriteTest(testdata["fluka/018_XEC.inp"], False, False)


def test_FlairLoad_T019_YEC(testdata):
    flairLoadWriteTest(testdata["fluka/019_YEC.inp"], False, False)


def test_FlairLoad_T020_ZEC(testdata):
    flairLoadWriteTest(testdata["fluka/020_ZEC.inp"], False, False)


def test_FlairLoad_T021_QUA(testdata):
    quaAABB = {
        "QUA_REG": _fluka.AABB([-150.0, 100.0, 0], [150.0, 200.0, 1000.0]),
        "blackhol": _fluka.AABB([-150.0, 100.0, 0], [150.0, 200.0, 1000.0]),
    }
    flairLoadWriteTest(testdata["fluka/021_QUA.inp"], False, False, quadricRegionAABBs=quaAABB)


def test_FlairLoad_T050_RPP_Translate(testdata):
    flairLoadWriteTest(testdata["fluka/050_RPP_Translate.inp"], False, False)


def test_FlairLoad_T051_RPP_Expansion(testdata):
    flairLoadWriteTest(testdata["fluka/051_RPP_Expansion.inp"], False, False)


def test_FlairLoad_T052_RPP_RotDefi(testdata):
    flairLoadWriteTest(testdata["fluka/052_RPP_RotDefi.inp"], False, False)


def test_FlairLoad_T053_RPP_RotDefi2(testdata):
    flairLoadWriteTest(testdata["fluka/053_RPP_RotDefi2.inp"], False, False)


def test_FlairLoad_T054_RPP_TranslateExpansionRotDefi(testdata):
    flairLoadWriteTest(testdata["fluka/054_RPP_TranslateExpansionRotDefi.inp"], False, False)


def test_FlairLoad_T100_Multiple(testdata):
    flairLoadWriteTest(testdata["fluka/100_Multiple.inp"], False, False)


def test_FlairLoad_T101_Intersection(testdata):
    flairLoadWriteTest(testdata["fluka/101_Intersection.inp"], False, False)


def test_FlairLoad_T102_Difference(testdata):
    flairLoadWriteTest(testdata["fluka/102_Difference.inp"], False, False)


def test_FlairLoad_T103_Union(testdata):
    flairLoadWriteTest(testdata["fluka/103_Union.inp"], False, False)


def test_FlairLoad_T104_Union(testdata):
    flairLoadWriteTest(testdata["fluka/104_shift_cylinders.inp"], False, False)


def test_FlairLoad_T301_RPP_transform(testdata):
    flairLoadWriteTest(testdata["fluka/301_RPP_transform.inp"], False, False)


def test_FlairLoad_T302_BOX_transform(testdata):
    flairLoadWriteTest(testdata["fluka/302_BOX_transform.inp"], False, False)


def test_FlairLoad_T303_SPH_transform(testdata):
    flairLoadWriteTest(testdata["fluka/303_SPH_transform.inp"], False, False)


def test_FlairLoad_T304_RCC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/304_RCC_transform.inp"], False, False)


def test_FlairLoad_T305_REC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/305_REC_transform.inp"], False, False)


def test_FlairLoad_T306_TRC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/306_TRC_transform.inp"], False, False)


def test_FlairLoad_T307_ELL_transform(testdata):
    flairLoadWriteTest(testdata["fluka/307_ELL_transform.inp"], False, False)


def test_FlairLoad_T308_RAW_transform(testdata):
    flairLoadWriteTest(testdata["fluka/308_RAW_transform.inp"], False, False)


def test_FlairLoad_T308_WED_transform(testdata):
    flairLoadWriteTest(testdata["fluka/308_WED_transform.inp"], False, False)


def test_FlairLoad_T309_ARB_transform(testdata):
    flairLoadWriteTest(testdata["fluka/309_ARB_transform.inp"], False, False)


def test_FlairLoad_T310_XYP_transform(testdata):
    flairLoadWriteTest(testdata["fluka/310_XYP_transform.inp"], False, False)


def test_FlairLoad_T310_XZP_transform(testdata):
    flairLoadWriteTest(testdata["fluka/310_XZP_transform.inp"], False, False)


def test_FlairLoad_T310_YZP_transform(testdata):
    flairLoadWriteTest(testdata["fluka/310_YZP_transform.inp"], False, False)


def test_FlairLoad_T311_PLA_transform(testdata):
    flairLoadWriteTest(testdata["fluka/311_PLA_transform.inp"], False, False)


def test_FlairLoad_T312_XCC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/312_XCC_transform.inp"], False, False)


def test_FlairLoad_T312_YCC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/312_YCC_transform.inp"], False, False)


def test_FlairLoad_T312_ZCC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/312_ZCC_transform.inp"], False, False)


def test_FlairLoad_T313_XEC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/313_XEC_transform.inp"], False, False)


def test_FlairLoad_T313_YEC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/313_YEC_transform.inp"], False, False)


def test_FlairLoad_T313_ZEC_transform(testdata):
    flairLoadWriteTest(testdata["fluka/313_ZEC_transform.inp"], False, False)


def test_FlairLoad_T314_QUA_transform(testdata):
    quaAABB = {
        "QUA_REG": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
        "blackhol": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
    }
    flairLoadWriteTest(
        testdata["fluka/314_QUA_transform.inp"],
        False,
        False,
        quadricRegionAABBs=quaAABB,
    )


def test_FlairLoad_T320_cube_from_halfspaces_transform(testdata):
    flairLoadWriteTest(testdata["fluka/320_cube_from_halfspaces_transform.inp"], False, False)


def test_FlairLoad_T321_cube_from_plas_transform(testdata):
    flairLoadWriteTest(testdata["fluka/321_cube_from_plas_transform.inp"], False, False)


def test_FlairLoad_T514_QUA_expansion(testdata):
    quaAABB = {
        "QUA_REG": _fluka.AABB([-70.0, 50.0, 0], [70.0, 100.0, 500.0]),
        "blackhol": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
    }
    flairLoadWriteTest(
        testdata["fluka/514_QUA_expansion.inp"],
        False,
        False,
        quadricRegionAABBs=quaAABB,
    )


def test_FlairLoad_T514_QUA_translation(testdata):
    quaAABB = {
        "QUA_REG": _fluka.AABB([-150.0, 100.0, -1000.0], [150.0, 200.0, 0.0]),
        "blackhol": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
    }
    flairLoadWriteTest(
        testdata["fluka/514_QUA_translation.inp"],
        False,
        False,
        quadricRegionAABBs=quaAABB,
    )


def test_FlairLoad_T514_QUA_rototranslation(testdata):
    quaAABB = {
        "QUA_REG": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
        "blackhol": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
    }
    flairLoadWriteTest(
        testdata["fluka/514_QUA_rototranslation.inp"],
        False,
        False,
        quadricRegionAABBs=quaAABB,
    )


def test_FlairLoad_T514_QUA_coplanar(testdata):
    quaAABB = {
        "OUTER": _fluka.AABB([-200.0, 0.0, 0.0], [200, 200, 1100]),
        "INNER": _fluka.AABB([-100.0, 50.0, 250], [100.0, 150.0, 850.0]),
        "blackhol": _fluka.AABB([-190.0, 40.0, 0], [50.0, 200.0, 1000.0]),
    }
    flairLoadWriteTest(
        testdata["fluka/514_QUA_coplanar.inp"], False, False, quadricRegionAABBs=quaAABB
    )


def test_FlairLoad_T601_filter_redundant_halfspaces(testdata):
    flairLoadWriteTest(testdata["fluka/601_filter_redundant_halfspaces.inp"], False, False)


def test_FlairLoad_T701_LATTICE(testdata):
    flairLoadWriteTest(testdata["fluka/701_LATTICE.inp"], False, False)


def test_FlairLoad_T702_LATTICE(testdata):
    flairLoadWriteTest(testdata["fluka/702_LATTICE.inp"], False, False)


def test_FlairLoad_T703_LATTICE(testdata):
    flairLoadWriteTest(testdata["fluka/703_LATTICE.inp"], False, False)


def test_FlairLoad_T801_nested_expansion(testdata):
    flairLoadWriteTest(testdata["fluka/801_nested_expansion.inp"], False, False)


def test_FlairLoad_T802_nested_translation(testdata):
    flairLoadWriteTest(testdata["fluka/802_nested_translation.inp"], False, False)


def test_FlairLoad_T803_nested_transform(testdata):
    flairLoadWriteTest(testdata["fluka/803_nested_transform.inp"], False, False)


def test_FlairLoad_T804_recursive_transform(testdata):
    flairLoadWriteTest(testdata["fluka/804_recursive_transform.inp"], False, False)


def test_FlairLoad_T805_inverse_transform(testdata):
    flairLoadWriteTest(testdata["fluka/805_inverse_transform.inp"], False, False)


def test_FlairLoad_T806_combined_translat_transform(testdata):
    flairLoadWriteTest(testdata["fluka/806_combined_translat_transform.inp"], False, False)


def test_FlairLoad_T901_preprocessor_if(testdata):
    freg, greg = flairLoadWriteTest(testdata["fluka/901_preprocessor_if.inp"], False, False)
    solids = greg.solidDict
    assert isinstance(solids["bb1_s"], pyg4ometry.geant4.solid.Cons)


def test_FlairLoad_T902_preprocessor_elif(testdata):
    freg, greg = flairLoadWriteTest(testdata["fluka/902_preprocessor_elif.inp"], False, False)
    solids = greg.solidDict
    assert isinstance(solids["bb1_s"], pyg4ometry.geant4.solid.Box)


def test_FlairLoad_T903_preprocessor_else(testdata):
    freg, greg = flairLoadWriteTest(testdata["fluka/903_preprocessor_else.inp"], False, False)
    solids = greg.solidDict
    assert isinstance(solids["bb1_s"], pyg4ometry.geant4.solid.Tubs)


def test_FlairLoad_T904_preprocessor_include(testdata):
    flairLoadWriteTest(testdata["fluka/904_preprocessor_include.inp"], False, False)


def test_FlairLoad_T905_preprocessor_nested_if(testdata):
    freg, greg = flairLoadWriteTest(testdata["fluka/905_preprocessor_nested_if.inp"], False, False)
    solids = greg.solidDict
    assert isinstance(solids["bb1_s"], pyg4ometry.geant4.solid.Cons)


def test_FlairLoad_T906_preprocessor_nested_elif(testdata):
    freg, greg = flairLoadWriteTest(
        testdata["fluka/906_preprocessor_nested_elif.inp"], False, False
    )
    solids = greg.solidDict
    assert isinstance(solids["bb1_s"], pyg4ometry.geant4.solid.Box)


def test_FlairLoad_T907_preprocessor_nested_else(testdata):
    freg, greg = flairLoadWriteTest(
        testdata["fluka/907_preprocessor_nested_else.inp"], False, False
    )
    solids = greg.solidDict
    assert isinstance(solids["bb1_s"], pyg4ometry.geant4.solid.Box)


def test_FlairLoad_T908_preprocessor_define(testdata):
    flairLoadWriteTest(testdata["fluka/908_preprocessor_define.inp"], False, False)


def test_FlairLoad_Tex_geometry(testdata):
    flairLoadWriteTest(testdata["fluka/ex-geometry.inp"], False, False)


def test_FlairLoad_Tex_Scoring(testdata):
    flairLoadWriteTest(testdata["fluka/ex_Scoring.inp"], False, False)


def test_FlairLoad_Texample_running(testdata):
    flairLoadWriteTest(testdata["fluka/example_running.inp"], False, False)


def test_FlairLoad_Texample_score(testdata):
    flairLoadWriteTest(testdata["fluka/example_score.inp"], False, False)


def test_FlairLoad_TmanualSimpleFileFixed(testdata):
    flairLoadWriteTest(testdata["fluka/manualSimpleFileFixed.inp"], False, False)


def test_FlairLoad_TmanualSimpleFileFree(testdata):
    flairLoadWriteTest(testdata["fluka/manualSimpleFileFree.inp"], False, False)


# def test_FlairLoad_TcorrectorDipole():
#    flairLoadWriteTest("corrector-dipole.inp", False, False)
