import numpy as _np
import os as _os
import pytest


import pyg4ometry

import T000_SolidBase
import T001_Box
import T002_Tubs
import T003_CutTubs
import T0031_CutTubs_number
import T0032_CutTubs_string
import T0033_CutTubs_expression
import T0034_CutTubs_DefineTree
import T004_Cons
import T005_Para
import T006_Trd
import T007_Trap
import T008_Sphere
import T009_Orb
import T010_Torus
import T011_Polycone
import T012_GenericPolycone
import T013_Polyhedra
import T014_GenericPolyhedra
import T015_EllipticalTube
import T016_Ellipsoid
import T017_EllipticalCone
import T018_Paraboloid
import T019_Hyperboloid
import T020_Tet
import T021_ExtrudedSolid
import T022_TwistedBox
import T023_TwistedTrap
import T024_TwistedTrd
import T025_TwistedTubs
import T026_GenericTrap
import T028_Union
import T029_Subtraction
import T030_Intersection
import T031_MultiUnion
import T032_Scaled
import T033_TessellatedSolid
import T101_physical_logical
import T102_overlap_none
import T103_overlap_copl
import T103_overlap_copl_simple
import T104_overlap_volu
import T105_assembly
import T106_replica_x
import T107_replica_y
import T108_replica_z
import T109_replica_phi
import T110_replica_rho
import T111_parameterised_box
import T112_parameterised_tube
import T201_Materials
import T202_OpticalSurface
import T203_MaterialsRegistry
import T204_NIST_Element
import T205_NIST_Material
import T300_overlap_assembly_regular_lv
import T301_overlap_assembly_none
import T302_overlap_assembly_coplanar
import T303_overlap_assembly_daughter_collision
import T304_overlap_assembly_volumetric
import T305_overlap_assembly_nested
import T306_overlap_replica_x
import T307_overlap_replica_x_internal
import T400_MergeRegistry
import T401_MergeRegistry_Box
import T402_MergeRegistry_Tubs
import T403_MergeRegistry_CutTubs
import T404_MergeRegistry_Cons
import T405_MergeRegistry_Para
import T406_MergeRegistry_Trd
import T407_MergeRegistry_Trap
import T408_MergeRegistry_Sphere
import T409_MergeRegistry_Orb
import T410_MergeRegistry_Torus
import T411_MergeRegistry_Polycone
import T412_MergeRegistry_GenericPolycone
import T413_MergeRegistry_Polyhedra
import T414_MergeRegistry_GenericPolyhedra
import T415_MergeRegistry_EllipticalTube
import T416_MergeRegistry_Ellipoid
import T417_MergeRegistry_EllipticalCone
import T418_MergeRegistry_Paraboloid
import T419_MergeRegistry_Hyperboloid
import T420_MergeRegistry_Tet
import T421_MergeRegistry_ExtrudedSolid
import T422_MergeRegistry_TwistedBox
import T423_MergeRegistry_TwistedTrap
import T424_MergeRegistry_TwistedTrd
import T425_MergeRegistry_TwistedTubs
import T426_MergeRegistry_GenericTrap
import T428_MergeRegistry_Union
import T429_MergeRegistry_Subtraction
import T430_MergeRegistry_Intersection
import T431_MergeRegistry_MultiUnion
import T432_MergeRegistry_Box_AssemblyConversion
import T433_MergeRegistry_Scale
import T434_MergeRegistry_CollapseAssembly
import T600_LVTessellated
import T601_reflect

# from . import T602_lv_cull_daughters
# from . import T603_lv_change_solid_and_trim
# from . import T604_lv_change_solid_and_trim_rot
import T605_LvChangeSolid
import T606_LvClipSolid
import T607_LvChangeAndClipSolid
import T608_LvClipSolidRecursive
import T609_LvClipSolidRecursiveAssembly

writeNISTMaterials = False


def test_PythonGeant_Plane():
    p = pyg4ometry.geant4.solid.Plane("plane", [0, 0, 1], 1000)
    str(p)


def test_PythonGeant_Wedge():
    w = pyg4ometry.geant4.solid.Wedge("wedge", 1000, 0, 1.5 * _np.pi, 10000)
    str(w)


def test_PythonGeant_T000_SolidBase():
    assert T000_SolidBase.Test()["testStatus"]


def test_PythonGeant_T001_Box(tmptestdir, testdata):
    T001_Box.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T001_Box.gdml"],
    )


def test_PythonGeant_T002_Tubs(tmptestdir, testdata):
    T002_Tubs.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T002_Tubs.gdml"],
    )


def test_PythonGeant_T003_CutTubs(tmptestdir, testdata):
    T003_CutTubs.Test(
        vis=False,
        interactive=False,
        type=T003_CutTubs.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        outputFile="T003_CutTubs.gdml",
        refFilePath=testdata["gdml/T003_CutTubs.gdml"],
    )

    T003_CutTubs.Test(
        vis=False,
        interactive=False,
        type=T003_CutTubs.flat_ends,
        outputPath=tmptestdir,
        outputFile="T003_CutTubs_flat_ends.gdml",
        refFilePath=testdata["gdml/T003_CutTubs_flat_ends.gdml"],
    )

    T0031_CutTubs_number.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        outputFile="T0031_CutTubs_numbers.gdml",
        refFilePath=testdata["gdml/T0031_CutTubs_numbers.gdml"],
    )

    T0032_CutTubs_string.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        outputFile="T0032_CutTubs_string.gdml",
        refFilePath=testdata["gdml/T0032_CutTubs_string.gdml"],
    )

    # TODO
    # T0033_CutTubs_expression.Test(vis=False, interactive=False, outputPath=tmptestdir, refFilePath=testdata["gdml/T001_Box.gdml"],)

    T0034_CutTubs_DefineTree.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        outputFile="T0034_CutTubs_DefineTree.gdml",
        refFilePath=testdata["gdml/T0034_CutTubs_DefineTree.gdml"],
    )


def test_PythonGeant_T004_Cons(tmptestdir, testdata):
    try:
        T004_Cons.Test(
            vis=False,
            interactive=False,
            type=T004_Cons.r1min_gt_r1max,
            writeNISTMaterials=writeNISTMaterials,
            outputPath=tmptestdir,
            refFilePath=testdata["gdml/T004_Cons.gdml"],
        )
    except ValueError:
        pass

    try:
        T004_Cons.Test(
            vis=False,
            interactive=False,
            type=T004_Cons.r2min_gt_r2max,
            outputPath=tmptestdir,
            refFilePath=None,
        )
    except ValueError:
        pass

    try:
        T004_Cons.Test(
            vis=False,
            interactive=False,
            type=T004_Cons.dphi_gt_2pi,
            outputPath=tmptestdir,
            refFilePath=None,
        )
    except ValueError:
        pass

    T004_Cons.Test(
        vis=False,
        interactive=False,
        type=T004_Cons.dphi_eq_2pi,
        outputPath=tmptestdir,
        outputFile="T004_Cons_dphi_eq_2pi.gdml",
        refFilePath=testdata["gdml/T004_Cons_dphi_eq_2pi.gdml"],
    )

    T004_Cons.Test(
        vis=False,
        interactive=False,
        type=T004_Cons.cone_up,
        outputPath=tmptestdir,
        outputFile="T004_Cons_cone_up.gdml",
        refFilePath=testdata["gdml/T004_Cons_cone_up.gdml"],
    )

    T004_Cons.Test(
        vis=False,
        interactive=False,
        type=T004_Cons.inner_cylinder,
        outputPath=tmptestdir,
        outputFile="T004_Cons_inner_cylinder.gdml",
        refFilePath=testdata["gdml/T004_Cons_inner_cylinder.gdml"],
    )

    T004_Cons.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        outputFile="T003_Cons.gdml",
        refFilePath=testdata["gdml/T004_Cons.gdml"],
    )


def test_PythonGeant_T005_Para(tmptestdir, testdata):
    T005_Para.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T005_Para.gdml"],
    )


def test_PythonGeant_T006_Trd(tmptestdir, testdata):
    T006_Trd.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T006_Trd.gdml"],
    )


def test_PythonGeant_T007_Trap(tmptestdir, testdata):
    T007_Trap.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T007_Trap.gdml"],
    )


def test_PythonGeant_T008_Sphere(tmptestdir, testdata):
    assert T008_Sphere.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T008_Sphere.gdml"],
    )


def test_PythonGeant_T009_Orb(tmptestdir, testdata):
    T009_Orb.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T009_Orb.gdml"],
    )


def test_PythonGeant_T010_Torus(tmptestdir, testdata):
    T010_Torus.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T010_Torus.gdml"],
    )


def test_PythonGeant_T011_Polycone(tmptestdir, testdata):
    T011_Polycone.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T011_Polycone.gdml"],
    )


def test_PythonGeant_T012_GenericPolycone(tmptestdir, testdata):
    T012_GenericPolycone.Test(
        vis=False,
        interactive=False,
        type=T012_GenericPolycone.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T012_GenericPolycone.gdml"],
    )

    try:
        T012_GenericPolycone.Test(
            vis=False,
            interactive=False,
            type=T012_GenericPolycone.two_planes,
            outputPath=tmptestdir,
            refFilePath=testdata["gdml/T001_Box.gdml"],
        )
    except ValueError:
        pass


def test_PythonGeant_T013_Polyhedra(tmptestdir, testdata):
    T013_Polyhedra.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T013_Polyhedra.gdml"],
    )


def test_PythonGeant_T014_GenericPolyhedra(tmptestdir, testdata):
    T014_GenericPolyhedra.Test(
        vis=False,
        interactive=False,
        type=T014_GenericPolyhedra.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T014_GenericPolyhedra.gdml"],
    )

    try:
        T014_GenericPolyhedra.Test(
            vis=False,
            interactive=False,
            type=T014_GenericPolyhedra.two_planes,
            outputPath=tmptestdir,
            refFilePath=testdata["gdml/T001_Box.gdml"],
        )
    except ValueError:
        pass


def test_PythonGeant_T015_EllipticalTube(tmptestdir, testdata):
    T015_EllipticalTube.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T015_EllipticalTube.gdml"],
    )


def test_PythonGeant_T016_Ellipsoid(tmptestdir, testdata):
    assert T016_Ellipsoid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T016_Ellipsoid.gdml"],
    )


def test_PythonGeant_T017_EllipticalCone(tmptestdir, testdata):
    T017_EllipticalCone.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        outputFile="T017_EllipticalCone.gdml",
        refFilePath=testdata["gdml/T017_EllipticalCone.gdml"],
    )

    T017_EllipticalCone.Test(
        vis=False,
        interactive=False,
        type=T017_EllipticalCone.zcut_outofrange,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        outputFile="T017_EllipticalCone_zcut_outofrange.gdml",
        refFilePath=testdata["gdml/T017_EllipticalCone_zcut_outofrange.gdml"],
    )


def test_PythonGeant_T018_Paraboloid(tmptestdir, testdata):
    T018_Paraboloid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T018_Paraboloid.gdml"],
    )


def test_PythonGeant_T019_Hyperboloid(tmptestdir, testdata):
    T019_Hyperboloid.Test(
        vis=False,
        interactive=False,
        type=T019_Hyperboloid.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T019_Hyperboloid.gdml"],
    )

    T019_Hyperboloid.Test(
        vis=False,
        interactive=False,
        type=T019_Hyperboloid.rmin_eq_zero,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        outputFile="T019_Hyperboloid_rmin_eq_zero.gdml",
        refFilePath=testdata["gdml/T019_Hyperboloid_rmin_eq_zero.gdml"],
    )

    try:
        T019_Hyperboloid.Test(
            vis=False,
            interactive=False,
            type=T019_Hyperboloid.rmin_gt_rmax,
            writeNISTMaterials=writeNISTMaterials,
            outputPath=tmptestdir,
            refFilePath=testdata["gdml/T001_Box.gdml"],
        )
    except ValueError:
        pass


def test_PythonGeant_T020_Tet(tmptestdir, testdata):
    T020_Tet.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T020_Tet.gdml"],
    )


def test_PythonGeant_T021_ExtrudedSolid(tmptestdir, testdata):
    T021_ExtrudedSolid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T021_ExtrudedSolid.gdml"],
    )


def test_PythonGeant_T022_TwistedBox(tmptestdir, testdata):
    T022_TwistedBox.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T022_TwistedBox.gdml"],
    )


def test_PythonGeant_T023_TwistedTrap(tmptestdir, testdata):
    T023_TwistedTrap.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T023_TwistedTrap.gdml"],
    )


def test_PythonGeant_T024_TwistedTrd(tmptestdir, testdata):
    T024_TwistedTrd.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T024_TwistedTrd.gdml"],
    )


def test_PythonGeant_T025_TwistedTubs(tmptestdir, testdata):
    T025_TwistedTubs.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T025_TwistedTubs.gdml"],
    )


def test_PythonGeant_T026_GenericTrap(tmptestdir, testdata):
    T026_GenericTrap.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T026_GenericTrap.gdml"],
    )


def test_PythonGeant_T028_Union(tmptestdir, testdata):
    T028_Union.Test(
        vis=False,
        interactive=False,
        disjoint=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T028_Union.gdml"],
    )


def test_PythonGeant_T029_Subtraction(tmptestdir, testdata):
    T029_Subtraction.Test(
        vis=False,
        interactive=False,
        nullMesh=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T029_Subtraction.gdml"],
    )


def test_PythonGeant_T030_Intersection(tmptestdir, testdata):
    T030_Intersection.Test(
        vis=False,
        interactive=False,
        type=T030_Intersection.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T030_Intersection.gdml"],
    )


def test_PythonGeant_T031_MultiUnion(tmptestdir, testdata):
    T031_MultiUnion.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T031_MultiUnion.gdml"],
    )


def test_PythonGeant_T032_Scaled(tmptestdir, testdata):
    T032_Scaled.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T032_Scaled.gdml"],
    )


def test_PythonGeant_T033_Tessellated(tmptestdir, testdata):
    T033_TessellatedSolid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T033_TessellatedSolid.gdml"],
    )


def test_PythonGeant_T101_PhysicalLogical(tmptestdir, testdata):
    T101_physical_logical.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T101_physical_logical.gdml"],
    )


def test_PythonGeant_T102_OverlapNone(tmptestdir, testdata):
    T102_overlap_none.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T102_overlap_none.gdml"],
    )


def test_PythonGeant_T103_OverlapCopl(tmptestdir, testdata):
    T103_overlap_copl.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T103_overlap_copl.gdml"],
    )


def test_PythonGeant_T103_OverlapCopl_Simple(tmptestdir, testdata):
    T103_overlap_copl_simple.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T103_overlap_copl_simple.gdml"],
    )


def test_PythonGeant_T104_OverlapVolu(tmptestdir, testdata):
    T104_overlap_volu.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T104_overlap_volu.gdml"],
    )


def test_PythonGeant_T105_Assembly(tmptestdir, testdata):
    T105_assembly.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T105_assembly.gdml"],
    )


def test_PythonGeant_T106_ReplicaX(tmptestdir, testdata):
    T106_replica_x.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T106_replica_x.gdml"],
    )


def test_PythonGeant_T107_ReplicaY(tmptestdir, testdata):
    T107_replica_y.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T107_replica_y.gdml"],
    )


def test_PythonGeant_T108_ReplicaZ(tmptestdir, testdata):
    T108_replica_z.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T108_replica_z.gdml"],
    )


def test_PythonGeant_T109_ReplicaPhi(tmptestdir, testdata):
    T109_replica_phi.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T109_replica_phi.gdml"],
    )


def test_PythonGeant_T110_ReplicaRho(tmptestdir, testdata):
    T110_replica_rho.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T110_replica_rho.gdml"],
    )


def test_PythonGeant_T111_parameterised_box(tmptestdir, testdata):
    T111_parameterised_box.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T111_parameterised_box.gdml"],
    )


def test_PythonGeant_T112_parameterised_tube(tmptestdir, testdata):
    T112_parameterised_tube.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T112_parameterised_tube.gdml"],
    )


def test_PythonGeant_T201_Materials(tmptestdir, testdata):
    T201_Materials.Test_MaterialPredefined(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T201_MaterialPredefined.gdml"],
    )
    T201_Materials.Test_MaterialSingleElement(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T201_MaterialSingleElement.gdml"],
    )
    T201_Materials.Test_MaterialCompoundMassFraction(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T201_MaterialCompoundMassFraction.gdml"],
    )
    T201_Materials.Test_MaterialCompoundAtoms(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T201_MaterialCompoundNumberAtoms.gdml"],
    )
    T201_Materials.Test_MaterialMixture(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T201_MaterialMixture.gdml"],
    )
    T201_Materials.Test_MaterialIsotopes(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T201_MaterialIsotopes.gdml"],
    )


def test_PythonGeant_T202_OpticalSurface(tmptestdir, testdata):
    T202_OpticalSurface.Test_OpticalSurface(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T202_Optical.gdml"],
    )


def test_PythonGeant_T203_MaterialsRegistry(tmptestdir, testdata):
    T203_MaterialsRegistry.Test_MaterialsRegistry(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T203_MaterialsRegistry.gdml"],
    )


def test_PythonGeant_T204_NIST_Element(tmptestdir, testdata):
    T204_NIST_Element.Test_NIST_Element(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T204_NIST_Element.gdml"],
    )


def test_PythonGeant_T205_NIST_Material(tmptestdir, testdata):
    T205_NIST_Material.Test_NIST_Material(
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T205_NIST_Element.gdml"],
    )


def test_PythonGeant_T400_MergeRegistry(tmptestdir, testdata):
    T400_MergeRegistry.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T400_MergeRegistry.gdml"],
    )


def test_PythonGeant_T401_MergeRegistry_Box(tmptestdir, testdata):
    T401_MergeRegistry_Box.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T401_MergeRegistry_Box.gdml"],
    )


def test_PythonGeant_T402_MergeRegistry_Tubs(tmptestdir, testdata):
    T402_MergeRegistry_Tubs.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T402_MergeRegistry_Tubs.gdml"],
    )


def test_PythonGeant_T403_MergeRegistry_CutTubs(tmptestdir, testdata):
    T403_MergeRegistry_CutTubs.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T403_MergeRegistry_CutTubs.gdml"],
    )


def test_PythonGeant_T404_MergeRegistry_Cons(tmptestdir, testdata):
    T404_MergeRegistry_Cons.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T404_MergeRegistry_Cons.gdml"],
    )


def test_PythonGeant_T405_MergeRegistry_Para(tmptestdir, testdata):
    T405_MergeRegistry_Para.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T405_MergeRegistry_Para.gdml"],
    )


def test_PythonGeant_T406_MergeRegistry_Trd(tmptestdir, testdata):
    T406_MergeRegistry_Trd.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T406_MergeRegistry_Trd.gdml"],
    )


def test_PythonGeant_T407_MergeRegistry_Trap(tmptestdir, testdata):
    T407_MergeRegistry_Trap.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T407_MergeRegistry_Trap.gdml"],
    )


def test_PythonGeant_T408_MergeRegistry_Sphere(tmptestdir, testdata):
    T408_MergeRegistry_Sphere.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T408_MergeRegistry_Sphere.gdml"],
    )


def test_PythonGeant_T409_MergeRegistry_Orb(tmptestdir, testdata):
    T409_MergeRegistry_Orb.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T409_MergeRegistry_Orb.gdml"],
    )


def test_PythonGeant_T410_MergeRegistry_Torus(tmptestdir, testdata):
    T410_MergeRegistry_Torus.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T410_MergeRegistry_Torus.gdml"],
    )


def test_PythonGeant_T411_MergeRegistry_Polycone(tmptestdir, testdata):
    T411_MergeRegistry_Polycone.Test(
        vis=False,
        interactive=tmptestdir,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T411_MergeRegistry_Polycone.gdml"],
    )


def test_PythonGeant_T412_MergeRegistry_GenericPolycone(tmptestdir, testdata):
    T412_MergeRegistry_GenericPolycone.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T412_MergeRegistry_GenericPolycone.gdml"],
    )


def test_PythonGeant_T413_MergeRegistry_Polyhedra(tmptestdir, testdata):
    T413_MergeRegistry_Polyhedra.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T413_MergeRegistry_Polyhedra.gdml"],
    )


def test_PythonGeant_T414_MergeRegistry_GenericPolyhedra(tmptestdir, testdata):
    T414_MergeRegistry_GenericPolyhedra.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T414_MergeRegistry_GenericPolyhedra.gdml"],
    )


def test_PythonGeant_T415_MergeRegistry_EllipticalTube(tmptestdir, testdata):
    T415_MergeRegistry_EllipticalTube.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T415_MergeRegistry_EllipticalTube.gdml"],
    )


def test_PythonGeant_T416_MergeRegistry_Ellipsoid(tmptestdir, testdata):
    T416_MergeRegistry_Ellipoid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T416_MergeRegistry_Ellipsoid.gdml"],
    )


def test_PythonGeant_T417_MergeRegistry_EllipticalCone(tmptestdir, testdata):
    T417_MergeRegistry_EllipticalCone.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T417_MergeRegistry_EllipticalCone.gdml"],
    )


def test_PythonGeant_T418_MergeRegistry_EllipticalParaboloid(tmptestdir, testdata):
    T418_MergeRegistry_Paraboloid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T418_MergeRegistry_Paraboloid.gdml"],
    )


def test_PythonGeant_T419_MergeRegistry_Hyperboloid(tmptestdir, testdata):
    T419_MergeRegistry_Hyperboloid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T419_MergeRegistry_Hyperboloid.gdml"],
    )


def test_PythonGeant_T420_MergeRegistry_Tet(tmptestdir, testdata):
    T420_MergeRegistry_Tet.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T420_MergeRegistry_Tet.gdml"],
    )


def test_PythonGeant_T421_MergeRegistry_ExtrudedSolid(tmptestdir, testdata):
    T421_MergeRegistry_ExtrudedSolid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T421_MergeRegistry_ExtrudedSolid.gdml"],
    )


def test_PythonGeant_T422_MergeRegistry_TwistedBox(tmptestdir, testdata):
    T422_MergeRegistry_TwistedBox.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T422_MergeRegistry_TwistedBox.gdml"],
    )


def test_PythonGeant_T423_MergeRegistry_TwistedTrap(tmptestdir, testdata):
    T423_MergeRegistry_TwistedTrap.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T423_MergeRegistry_TwistedTrap.gdml"],
    )


def test_PythonGeant_T424_MergeRegistry_TwistedTrd(tmptestdir, testdata):
    T424_MergeRegistry_TwistedTrd.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T424_MergeRegistry_TwistedTrd.gdml"],
    )


def test_PythonGeant_T425_MergeRegistry_TwistedTubs(tmptestdir, testdata):
    T425_MergeRegistry_TwistedTubs.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T425_MergeRegistry_TwistedTubs.gdml"],
    )


def test_PythonGeant_T426_MergeRegistry_GenericTrap(tmptestdir, testdata):
    T426_MergeRegistry_GenericTrap.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T426_MergeRegistry_GenericTrap.gdml"],
    )


def test_PythonGeant_T428_MergeRegistry_Union(tmptestdir, testdata):
    T428_MergeRegistry_Union.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T428_MergeRegistry_Union.gdml"],
    )


def test_PythonGeant_T429_MergeRegistry_Subtraction(tmptestdir, testdata):
    T429_MergeRegistry_Subtraction.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T429_MergeRegistry_Subtraction.gdml"],
    )


def test_PythonGeant_T430_MergeRegistry_Intersection(tmptestdir, testdata):
    T430_MergeRegistry_Intersection.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T430_MergeRegistry_Intersection.gdml"],
    )


def test_PythonGeant_T431_MergeRegistry_MultiUnion(tmptestdir, testdata):
    T431_MergeRegistry_MultiUnion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T431_MergeRegistry_MultiUnion.gdml"],
    )


def test_PythonGeant_T432_MergeRegistryBoxAssemblyConverion(tmptestdir, testdata):
    T432_MergeRegistry_Box_AssemblyConversion.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T432_MergeRegistry_Box_AssemblyConversion.gdml"],
    )


def test_PythonGeant_T433_MergeRegistry_Scale(tmptestdir, testdata):
    T433_MergeRegistry_Scale.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T433_MergeRegistry_Scale.gdml"],
    )


def test_PythonGeant_T434_MergeRegistry_CollapseAssembly(tmptestdir, testdata):
    T434_MergeRegistry_CollapseAssembly.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T434_MergeRegistry_CollapseAssembly.gdml"],
    )


def test_PythonGeant_T600_LVTessellated(tmptestdir, testdata):
    T600_LVTessellated.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=None,
        # refFilePath=testdata["gdml/T600_LVTessellated.gdml"], TODO put back in
    )


def test_PythonGeant_T601_reflect(tmptestdir, testdata):
    T601_reflect.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T601_reflect.gdml"],
    )


# def test_PythonGeant_T602_lv_cull_daughters():
#    assert T602_lv_cull_daughters.Test()["testStatus"]

# def test_PythonGeant_T603_lv_change_solid_and_trim():
#    assert T603_lv_change_solid_and_trim.Test()["testStatus"]

# def test_PythonGeant_T604_lv_change_solid_and_trim_rot():
#    assert T604_lv_change_solid_and_timr_rot.Test()["testStatus"]


def test_PythonGeant_T605_LvChangeSolid(tmptestdir, testdata):
    T605_LvChangeSolid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T605_LvChangeSolid.gdml"],
    )


def test_PythonGeant_T606_LvClipSolid(tmptestdir, testdata):
    T606_LvClipSolid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T606_LvClipSolid.gdml"],
    )


def test_PythonGeant_T607_LvChangeAndClipSolid(tmptestdir, testdata):
    T607_LvChangeAndClipSolid.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T607_LvChangeAndClipSolid.gdml"],
    )


def test_PythonGeant_T608_LvClipSolidRecursive(tmptestdir, testdata):
    T608_LvClipSolidRecursive.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T608_LvClipSolidRecursive.gdml"],
    )


def test_PythonGeant_T609_LvClipSolidRecursiveAssembly(tmptestdir, testdata):
    T609_LvClipSolidRecursiveAssembly.Test(
        vis=False,
        interactive=False,
        outputPath=tmptestdir,
        refFilePath=testdata["gdml/T609_LvClipSolidRecursiveAssembly.gdml"],
    )
