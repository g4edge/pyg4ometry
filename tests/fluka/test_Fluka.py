from random import random
import numpy as np
import pytest

import pyg4ometry.visualisation.VtkViewerNew as _VtkViewerNew
from pyg4ometry.fluka.fluka_registry import RotoTranslationStore, FlukaRegistry
from pyg4ometry.fluka.directive import rotoTranslationFromTra2

import T001_RPP
import T002_BOX
import T003_SPH
import T004_RCC
import T005_REC
import T006_TRC
import T007_ELL
import T008_RAW
import T008_WED
import T009_ARB
import T010_XYP
import T010_XZP
import T010_YZP
import T011_PLA
import T012_XCC
import T012_YCC
import T012_ZCC
import T013_XEC
import T013_YEC
import T013_ZEC
import T014_QUA

import T051_expansion
import T052_translation
import T090_lattice

import T101_region_one_body
import T102_region_intersection_two_bodies
import T103_region_subtraction_two_bodies
import T103_region_subtraction_two_bodies_RCC
import T104_region_union_two_zones
import T104_region_union_two_zones_2
import T105_region_subzone_subtraction
import T106_region_subzone_subtraction_with_union
import T107_region_union_with_reused_bodies

import T201_RPP_coplanar
import T202_BOX_coplanar
import T203_SPH_coplanar
import T204_RCC_coplanar
import T205_REC_coplanar
import T206_TRC_coplanar
import T207_ELL_coplanar
import T208_RAW_coplanar
import T208_WED_coplanar
import T209_ARB_coplanar
import T210_PLA_coplanar
import T210_XYP_coplanar
import T210_XZP_coplanar
import T210_YZP_coplanar
import T212_XCC_coplanar
import T212_YCC_coplanar
import T212_ZCC_coplanar
import T213_XEC_coplanar
import T213_YEC_coplanar
import T213_ZEC_coplanar
import T214_QUA_coplanar

import T401_RPP_expansion
import T402_BOX_expansion
import T403_SPH_expansion
import T404_RCC_expansion
import T405_REC_expansion
import T406_TRC_expansion
import T407_ELL_expansion
import T408_RAW_expansion
import T408_WED_expansion
import T409_ARB_expansion
import T410_XYP_expansion
import T410_XZP_expansion
import T410_YZP_expansion
import T411_PLA_expansion
import T412_XCC_expansion
import T412_YCC_expansion
import T412_ZCC_expansion
import T413_XEC_expansion
import T413_YEC_expansion
import T413_ZEC_expansion
import T414_QUA_expansion
import T501_RPP_translation
import T502_BOX_translation
import T503_SPH_translation
import T504_RCC_translation
import T505_REC_translation
import T506_TRC_translation
import T507_ELL_translation
import T508_RAW_translation
import T508_WED_translation
import T509_ARB_translation
import T510_XYP_translation
import T510_XZP_translation
import T510_YZP_translation
import T511_PLA_translation
import T512_XCC_translation
import T512_YCC_translation
import T512_ZCC_translation
import T513_XEC_translation
import T513_YEC_translation
import T513_ZEC_translation
import T514_QUA_translation

import T601_RPP_rototranslation
import T602_BOX_rototranslation
import T603_SPH_rototranslation
import T604_RCC_rototranslation
import T605_REC_rototranslation
import T606_TRC_rototranslation
import T607_ELL_rototranslation
import T608_RAW_rototranslation
import T608_WED_rototranslation
import T609_ARB_rototranslation
import T610_XYP_rototranslation
import T610_XZP_rototranslation
import T610_YZP_rototranslation
import T611_PLA_rototranslation
import T612_XCC_rototranslation
import T612_YCC_rototranslation
import T612_ZCC_rototranslation
import T613_XEC_rototranslation
import T613_YEC_rototranslation
import T613_ZEC_rototranslation
import T614_QUA_rototranslation

import T710_XYP_XZP_YZP_minimisation
import T711_PLA_minimisation
import T712_XCC_minimisation
import T712_YCC_minimisation
import T712_ZCC_minimisation
import T713_XEC_minimisation
import T713_YEC_minimisation
import T713_ZEC_minimisation

import T801_filter_redundant_halfspaces
import T803_material_element

import T901_cube_from_XYP_XZP_YZP
import T902_cube_from_six_PLAs


def test_PythonFluka_T001_RPP(tmptestdir, testdata):
    T001_RPP.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T001_RPP.inp"],
    )


def test_PythonFluka_T002_BOX(tmptestdir, testdata):
    T002_BOX.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T002_BOX.inp"],
    )


def test_PythonFluka_T003_SPH(tmptestdir, testdata):
    T003_SPH.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T003_SPH.inp"],
    )


def test_PythonFluka_T004_RCC(tmptestdir, testdata):
    T004_RCC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T004_RCC.inp"],
    )


def test_PythonFluka_T005_REC(tmptestdir, testdata):
    T005_REC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T005_REC.inp"],
    )


def test_PythonFluka_T006_TRC(tmptestdir, testdata):
    T006_TRC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T006_TRC.inp"],
    )


def test_PythonFluka_T007_ELL(tmptestdir, testdata):
    T007_ELL.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T007_ELL.inp"],
    )


def test_PythonFluka_T008_RAW(tmptestdir, testdata):
    T008_RAW.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T008_RAW.inp"],
    )


def test_PythonFluka_T008_WED(tmptestdir, testdata):
    T008_WED.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T008_WED.inp"],
    )


def test_PythonFluka_T009_ARB(tmptestdir, testdata):
    T009_ARB.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T009_ARB.inp"],
    )


def test_PythonFluka_T010_XYP(tmptestdir, testdata):
    T010_XYP.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T010_XYP.inp"],
    )


def test_PythonFluka_T010_XZP(tmptestdir, testdata):
    T010_XZP.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T010_XZP.inp"],
    )


def test_PythonFluka_T010_YZP(tmptestdir, testdata):
    T010_YZP.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T010_YZP.inp"],
    )


def test_PythonFluka_T011_PLA(tmptestdir, testdata):
    T011_PLA.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T011_PLA.inp"],
    )


def test_PythonFluka_T012_XCC(tmptestdir, testdata):
    T012_XCC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T012_XCC.inp"],
    )


def test_PythonFluka_T012_YCC(tmptestdir, testdata):
    T012_YCC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T012_YCC.inp"],
    )


def test_PythonFluka_T012_ZCC(tmptestdir, testdata):
    T012_ZCC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T012_ZCC.inp"],
    )


def test_PythonFluka_T013_XEC(tmptestdir, testdata):
    T013_XEC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T013_XEC.inp"],
    )


def test_PythonFluka_T013_YEC(tmptestdir, testdata):
    T013_YEC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T013_YEC.inp"],
    )


def test_PythonFluka_T013_ZEC(tmptestdir, testdata):
    T013_ZEC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T013_ZEC.inp"],
    )


def test_PythonFluka_T014_QUA(tmptestdir, testdata):
    T014_QUA.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T014_QUA.inp"],
    )


def test_PythonFluka_T051_expansion(tmptestdir, testdata):
    T051_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T051_expansion.inp"],
    )


def test_PythonFluka_T052_translation(tmptestdir, testdata):
    T052_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T052_translation.inp"],
    )


def test_PythonFluka_T090_lattice(tmptestdir, testdata):
    T090_lattice.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T090_lattice.inp"],
    )


# 1111111111
def test_PythonFluka_T101_region_one_body(tmptestdir, testdata):
    T101_region_one_body.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T101_region_one_body.inp"],
    )


def test_PythonFluka_T102_region_intersection_two_bodies(tmptestdir, testdata):
    T102_region_intersection_two_bodies.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T102_region_intersection_two_bodies.inp"],
    )


def test_PythonFluka_T103_region_subtraction_two_bodies(tmptestdir, testdata):
    T103_region_subtraction_two_bodies.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T103_region_subtraction_two_bodies.inp"],
    )


def test_PythonFluka_T103_region_subtraction_two_bodies_RCC(tmptestdir, testdata):
    T103_region_subtraction_two_bodies_RCC.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T103_region_subtraction_two_bodies_RCC.inp"],
    )


def test_PythonFluka_T104_region_union_two_zones(tmptestdir, testdata):
    T104_region_union_two_zones.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T104_region_union_two_zones.inp"],
    )


def test_PythonFluka_T104_region_union_two_zones_2(tmptestdir, testdata):
    T104_region_union_two_zones_2.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T104_region_union_two_zones_2.inp"],
    )


def test_PythonFluka_T105_region_subzone_subtraction(tmptestdir, testdata):
    T105_region_subzone_subtraction.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T105_region_subzone_subtraction.inp"],
    )


def test_PythonFluka_T106_region_subzone_subtraction_with_union(tmptestdir, testdata):
    T106_region_subzone_subtraction_with_union.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T106_region_subzone_subtraction_with_union.inp"],
    )


def test_PythonFluka_T107_region_union_with_reused_bodies(tmptestdir, testdata):
    T107_region_union_with_reused_bodies.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T107_region_union_with_reused_bodies.inp"],
    )


# 2222222222
def test_PythonFluka_T201_RPP_coplanar(tmptestdir, testdata):
    T201_RPP_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T201_RPP_coplanar.inp"],
    )


def test_PythonFluka_T202_BOX_coplanar(tmptestdir, testdata):
    T202_BOX_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T202_BOX_coplanar.inp"],
    )


def test_PythonFluka_T203_SPH_coplanar(tmptestdir, testdata):
    T203_SPH_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T203_SPH_coplanar.inp"],
    )


def test_PythonFluka_T204_RCC_coplanar(tmptestdir, testdata):
    T204_RCC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T204_RCC_coplanar.inp"],
    )


def test_PythonFluka_T205_REC_coplanar(tmptestdir, testdata):
    T205_REC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T205_REC_coplanar.inp"],
    )


def test_PythonFluka_T206_TRC_coplanar(tmptestdir, testdata):
    T206_TRC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T206_TRC_coplanar.inp"],
    )


def test_PythonFluka_T207_ELL_coplanar(tmptestdir, testdata):
    T207_ELL_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T207_ELL_coplanar.inp"],
    )


def test_PythonFluka_T208_RAW_coplanar(tmptestdir, testdata):
    T208_RAW_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T208_RAW_coplanar.inp"],
    )


def test_PythonFluka_T208_WED_coplanar(tmptestdir, testdata):
    T208_WED_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T208_WED_coplanar.inp"],
    )


def test_PythonFluka_T209_ARB_coplanar(tmptestdir, testdata):
    T209_ARB_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T209_ARB_coplanar.inp"],
    )


def test_PythonFluka_T210_PLA_coplanar(tmptestdir, testdata):
    T210_PLA_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T210_PLA_coplanar.inp"],
    )


def test_PythonFluka_T210_XYP_coplanar(tmptestdir, testdata):
    T210_XYP_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T210_XYP_coplanar.inp"],
    )


def test_PythonFluka_T210_XZP_coplanar(tmptestdir, testdata):
    T210_XZP_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T210_ZXP_coplanar.inp"],
    )


def test_PythonFluka_T210_YZP_coplanar(tmptestdir, testdata):
    T210_YZP_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T210_YZP_coplanar.inp"],
    )


def test_PythonFluka_T212_XCC_coplanar(tmptestdir, testdata):
    T212_XCC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T212_XCC_coplanar.inp"],
    )


def test_PythonFluka_T212_YCC_coplanar(tmptestdir, testdata):
    T212_YCC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T212_YCC_coplanar.inp"],
    )


def test_PythonFluka_T212_ZCC_coplanar(tmptestdir, testdata):
    T212_ZCC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T212_ZCC_coplanar.inp"],
    )


def test_PythonFluka_T213_XEC_coplanar(tmptestdir, testdata):
    T213_XEC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T213_XEC_coplanar.inp"],
    )


def test_PythonFluka_T213_YEC_coplanar(tmptestdir, testdata):
    T213_YEC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T213_YEC_coplanar.inp"],
    )


def test_PythonFluka_T213_ZEC_coplanar(tmptestdir, testdata):
    T213_ZEC_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T213_ZEC_coplanar.inp"],
    )


def test_PythonFluka_T214_QUA_coplanar(tmptestdir, testdata):
    T214_QUA_coplanar.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T214_QUA_coplanar.inp"],
    )


# 4444444444
def test_PythonFluka_T401_RPP_expansion(tmptestdir, testdata):
    T401_RPP_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T401_RPP_expansion.inp"],
    )


def test_PythonFluka_T402_BOX_expansion(tmptestdir, testdata):
    T402_BOX_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T402_BOX_expansion.inp"],
    )


def test_PythonFluka_T403_SPH_expansion(tmptestdir, testdata):
    T403_SPH_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T403_SPH_expansion.inp"],
    )


def test_PythonFluka_T404_RCC_expansion(tmptestdir, testdata):
    T404_RCC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T404_RCC_expansion.inp"],
    )


def test_PythonFluka_T405_REC_expansion(tmptestdir, testdata):
    T405_REC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T404_REC_expansion.inp"],
    )


def test_PythonFluka_T406_TRC_expansion(tmptestdir, testdata):
    T406_TRC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T406_TRC_expansion.inp"],
    )


def test_PythonFluka_T407_ELL_expansion(tmptestdir, testdata):
    T407_ELL_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T407_ELL_expansion.inp"],
    )


def test_PythonFluka_T408_RAW_expansion(tmptestdir, testdata):
    T408_RAW_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T408_RAW_expansion.inp"],
    )


def test_PythonFluka_T408_WED_expansion(tmptestdir, testdata):
    T408_WED_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T408_WED_expansion.inp"],
    )


def test_PythonFluka_T409_ARB_expansion(tmptestdir, testdata):
    T409_ARB_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T409_ARB_expansion.inp"],
    )


def test_PythonFluka_T410_XYP_expansion(tmptestdir, testdata):
    T410_XYP_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T410_XYP_expansion.inp"],
    )


def test_PythonFluka_T410_XZP_expansion(tmptestdir, testdata):
    T410_XZP_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T410_XZP_expansion.inp"],
    )


def test_PythonFluka_T410_YZP_expansion(tmptestdir, testdata):
    T410_YZP_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T410_YZP_expansion.inp"],
    )


def test_PythonFluka_T411_PLA_expansion(tmptestdir, testdata):
    T411_PLA_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T411_PLA_expansion.inp"],
    )


def test_PythonFluka_T412_XCC_expansion(tmptestdir, testdata):
    T412_XCC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T412_XCC_expansion.inp"],
    )


def test_PythonFluka_T412_YCC_expansion(tmptestdir, testdata):
    T412_YCC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T412_YCC_expansion.inp"],
    )


def test_PythonFluka_T412_ZCC_expansion(tmptestdir, testdata):
    T412_ZCC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T412_ZCC_expansion.inp"],
    )


def test_PythonFluka_T413_XEC_expansion(tmptestdir, testdata):
    T413_XEC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T413_XEC_expansion.inp"],
    )


def test_PythonFluka_T413_YEC_expansion(tmptestdir, testdata):
    T413_YEC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T413_YEC_expansion.inp"],
    )


def test_PythonFluka_T413_ZEC_expansion(tmptestdir, testdata):
    T413_ZEC_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T413_ZEC_expansion.inp"],
    )


def test_PythonFluka_T414_QUA_expansion(tmptestdir, testdata):
    T414_QUA_expansion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T414_QUA_expansion.inp"],
    )


def test_PythonFluka_T501_RPP_translation(tmptestdir, testdata):
    T501_RPP_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T501_RPP_translation.inp"],
    )


def test_PythonFluka_T502_BOX_translation(tmptestdir, testdata):
    T502_BOX_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T502_BOX_translation.inp"],
    )


def test_PythonFluka_T503_SPH_translation(tmptestdir, testdata):
    T503_SPH_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T503_SPH_translation.inp"],
    )


def test_PythonFluka_T504_RCC_translation(tmptestdir, testdata):
    T504_RCC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T504_RCC_translation.inp"],
    )


def test_PythonFluka_T505_REC_translation(tmptestdir, testdata):
    T505_REC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T505_REC_translation.inp"],
    )


def test_PythonFluka_T506_TRC_translation(tmptestdir, testdata):
    T506_TRC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T506_TRC_translation.inp"],
    )


def test_PythonFluka_T507_ELL_translation(tmptestdir, testdata):
    T507_ELL_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T507_ELL_translation.inp"],
    )


def test_PythonFluka_T508_RAW_translation(tmptestdir, testdata):
    T508_RAW_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T508_RAW_translation.inp"],
    )


def test_PythonFluka_T508_WED_translation(tmptestdir, testdata):
    T508_WED_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T508_WED_translation.inp"],
    )


def test_PythonFluka_T509_ARB_translation(tmptestdir, testdata):
    T509_ARB_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T509_ARB_translation.inp"],
    )


def test_PythonFluka_T510_XYP_translation(tmptestdir, testdata):
    T510_XYP_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T510_XYP_translation.inp"],
    )


def test_PythonFluka_T510_XZP_translation(tmptestdir, testdata):
    T510_XZP_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T510_XZP_translation.inp"],
    )


def test_PythonFluka_T510_YZP_translation(tmptestdir, testdata):
    T510_YZP_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T510_YZP_translation.inp"],
    )


def test_PythonFluka_T511_PLA_translation(tmptestdir, testdata):
    T511_PLA_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T511_PLA_translation.inp"],
    )


def test_PythonFluka_T512_XCC_translation(tmptestdir, testdata):
    T512_XCC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T512_XCC_translation.inp"],
    )


def test_PythonFluka_T512_YCC_translation(tmptestdir, testdata):
    T512_YCC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T512_YCC_translation.inp"],
    )


def test_PythonFluka_T512_ZCC_translation(tmptestdir, testdata):
    T512_ZCC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T512_ZCC_translation.inp"],
    )


def test_PythonFluka_T513_XEC_translation(tmptestdir, testdata):
    T513_XEC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T513_XEC_translation.inp"],
    )


def test_PythonFluka_T513_YEC_translation(tmptestdir, testdata):
    T513_YEC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T513_YEC_translation.inp"],
    )


def test_PythonFluka_T513_ZEC_translation(tmptestdir, testdata):
    T513_ZEC_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T513_ZEC_translation.inp"],
    )


def test_PythonFluka_T514_QUA_translation(tmptestdir, testdata):
    T514_QUA_translation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T514_QUA_translation.inp"],
    )


# 6666666666
def test_PythonFluka_T601_RPP_rototranslation(tmptestdir, testdata):
    T601_RPP_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T601_RPP_rototranslation.inp"],
    )


def test_PythonFluka_T602_BOX_rototranslation(tmptestdir, testdata):
    T602_BOX_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T602_BOX_rototranslation.inp"],
    )


def test_PythonFluka_T603_SPH_rototranslation(tmptestdir, testdata):
    T603_SPH_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T603_SPH_rototranslation.inp"],
    )


def test_PythonFluka_T604_RCC_rototranslation(tmptestdir, testdata):
    T604_RCC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T604_RCC_rototranslation.inp"],
    )


def test_PythonFluka_T605_REC_rototranslation(tmptestdir, testdata):
    T605_REC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T605_REC_rototranslation.inp"],
    )


def test_PythonFluka_T606_TRC_rototranslation(tmptestdir, testdata):
    T606_TRC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T606_TRC_rototranslation.inp"],
    )


def test_PythonFluka_T607_ELL_rototranslation(tmptestdir, testdata):
    T607_ELL_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T607_ELL_rototranslation.inp"],
    )


def test_PythonFluka_T608_RAW_rototranslation(tmptestdir, testdata):
    T608_RAW_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T608_RAW_rototranslation.inp"],
    )


def test_PythonFluka_T608_WED_rototranslation(tmptestdir, testdata):
    T608_WED_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T608_WED_rototranslation.inp"],
    )


def test_PythonFluka_T609_ARB_rototranslation(tmptestdir, testdata):
    T609_ARB_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T609_ARB_rototranslation.inp"],
    )


def test_PythonFluka_T610_XYP_rototranslation(tmptestdir, testdata):
    T610_XYP_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T610_XYP_rototranslation.inp"],
    )


def test_PythonFluka_T610_XZP_rototranslation(tmptestdir, testdata):
    T610_XZP_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T610_XZP_rototranslation.inp"],
    )


def test_PythonFluka_T610_YZP_rototranslation(tmptestdir, testdata):
    T610_YZP_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T610_YZP_rototranslation.inp"],
    )


def test_PythonFluka_T611_PLA_rototranslation(tmptestdir, testdata):
    T611_PLA_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T610_PLA_rototranslation.inp"],
    )


def test_PythonFluka_T612_XCC_rototranslation(tmptestdir, testdata):
    T612_XCC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T612_XCC_rototranslation.inp"],
    )


def test_PythonFluka_T612_YCC_rototranslation(tmptestdir, testdata):
    T612_YCC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T612_YCC_rototranslation.inp"],
    )


def test_PythonFluka_T612_ZCC_rototranslation(tmptestdir, testdata):
    T612_ZCC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T612_ZCC_rototranslation.inp"],
    )


def test_PythonFluka_T613_XEC_rototranslation(tmptestdir, testdata):
    T613_XEC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T613_XEC_rototranslation.inp"],
    )


def test_PythonFluka_T613_YEC_rototranslation(tmptestdir, testdata):
    T613_YEC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T613_YEC_rototranslation.inp"],
    )


def test_PythonFluka_T613_ZEC_rototranslation(tmptestdir, testdata):
    T613_ZEC_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T613_ZEC_rototranslation.inp"],
    )


def test_PythonFluka_T614_QUA_rototranslation(tmptestdir, testdata):
    T614_QUA_rototranslation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T614_QUA_rototranslation.inp"],
    )


# 7777777777
def test_PythonFluka_T710_XYP_XZP_YZP_minimisation(tmptestdir, testdata):
    T710_XYP_XZP_YZP_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T710_XYP_ZXP_YZP_minimiation.inp"],
    )


def test_PythonFluka_T711_PLA_minimisation(tmptestdir, testdata):
    T711_PLA_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T711_PLA_minimisation.inp"],
    )


def test_PythonFluka_T712_XCC_minimisation(tmptestdir, testdata):
    T712_XCC_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T712_XCC_minimisation.inp"],
    )


def test_PythonFluka_T712_YCC_minimisation(tmptestdir, testdata):
    T712_YCC_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T713_YCC_minimisation.inp"],
    )


def test_PythonFluka_T712_ZCC_minimisation(tmptestdir, testdata):
    T712_ZCC_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T713_ZCC_minimisation.inp"],
    )


def test_PythonFluka_T713_XEC_minimisation(tmptestdir, testdata):
    T713_XEC_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T713_XEC_minimisation.inp"],
    )


def test_PythonFluka_T713_YEC_minimisation(tmptestdir, testdata):
    T713_YEC_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T713_YEC_minimisation.inp"],
    )


def test_PythonFluka_T713_ZEC_minimisation(tmptestdir, testdata):
    T713_ZEC_minimisation.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T713_ZEC_minimisation.inp"],
    )


# 8888888888
def test_PythonFluka_T801_filter_redundant_halfspaces(tmptestdir, testdata):
    T801_filter_redundant_halfspaces.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T801_filter_redundant_halfspace.inp"],
    )


def test_PythonFluka_T803_material_element(tmptestdir, testdata):
    T803_material_element.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T803_material_element.inp"],
    )


# 9999999999
def test_PythonFluka_T901_cube_from_XYP_XZP_YZP(tmptestdir, testdata):
    T901_cube_from_XYP_XZP_YZP.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T901_cube_from_XYP_ZXP_YZP.inp"],
    )


def test_PythonFluka_T902_cube_from_six_PLAs(tmptestdir, testdata):
    T902_cube_from_six_PLAs.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T902_cube_from_six_PLAs.inp"],
    )


def test_PythonFluka_empyRegistry():
    import pyg4ometry.convert as convert
    from pyg4ometry.fluka import FlukaRegistry

    freg = FlukaRegistry()
    try:
        greg = convert.fluka2Geant4(freg)
    except ValueError:
        pass


def _makeRotoTranslation(name="rppTRF"):
    angle = random() * np.pi
    rtrans = rotoTranslationFromTra2(name, [[angle, angle, angle], [0, 0, 20]])
    return name, rtrans


def _makeStore():
    return RotoTranslationStore()


def test_storeInit():
    _makeStore()


def test_gettingRotoTranslation():
    name, rtrans = _makeRotoTranslation()
    store = _makeStore()
    store[name] = rtrans
    r = store[name]


def test_RotoTranslation_fails_setting_with_wrong_name():
    name, rtrans = _makeRotoTranslation()
    store = _makeStore()
    # TODO
    # with pytest.raises(ValueError):
    #    store["asdasd"] = rtrans


def test_RotoTranslation_fails_without_rotoTranslation():
    name, rtrans = _makeRotoTranslation()
    store = _makeStore()
    # TODO check this test
    # with pytest.raises(TypeError):
    #    store[name] = "something"


def test_store_len():
    name, rtrans = _makeRotoTranslation()
    store = _makeStore()
    # assert(len(store), 0)
    store[name] = rtrans
    # assert(len(store), 1)


def test_store_del():
    name, rtrans = _makeRotoTranslation()
    store = _makeStore()
    # assert(len(store), 0)
    store[name] = rtrans
    # assert(len(store), 1)
    del store[name]
    # assert(len(store), 0)


def test_addRotoTranslation():
    name1, rtrans1 = _makeRotoTranslation(name="rtrans1")
    name2, rtrans2 = _makeRotoTranslation(name="rtrans2")
    name3, rtrans3 = _makeRotoTranslation(name="rtrans3")
    name4, rtrans4 = _makeRotoTranslation(name="rtrans4")
    name5, rtrans5 = _makeRotoTranslation(name="rtrans5")

    store = _makeStore()

    store.addRotoTranslation(rtrans1)
    store.addRotoTranslation(rtrans2)
    # assert(rtrans1.transformationIndex, 2000)
    # assert(rtrans2.transformationIndex, 3000)
    del store[name1]
    store.addRotoTranslation(rtrans3)
    # assert(rtrans3.transformationIndex, 4000)

    # assert(store.allTransformationIndices(), [3000, 4000])

    rtrans4.transformationIndex = 9000
    store.addRotoTranslation(rtrans4)
    # assert(rtrans4.transformationIndex, 9000)

    rtrans5.transformationIndex = 9000
    # TODO check
    # with pytest.raises(KeyError):
    #    store.addRotoTranslation(rtrans5)


def test_fluka_vis(tmptestdir, testdata):
    r = T902_cube_from_six_PLAs.Test(
        False,
        False,
        outputPath=tmptestdir,
        refFilePath=testdata["fluka/T902_cube_from_six_PLAs.inp"],
    )["flukaRegistry"]
    v = _VtkViewerNew()
    v.addFlukaRegions(r)
    v.buildPipelinesAppend()
