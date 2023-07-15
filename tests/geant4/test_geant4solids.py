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

writeNISTMaterials = True


def test_PythonGeant_Plane():
    p = pyg4ometry.geant4.solid.Plane("plane", [0, 0, 1], 1000)
    str(p)


def test_PythonGeant_Wedge():
    w = pyg4ometry.geant4.solid.Wedge("wedge", 1000, 0, 1.5 * _np.pi, 10000)
    str(w)


def test_PythonGeant_T000_SolidBase():
    assert T000_SolidBase.Test()["testStatus"]


def test_PythonGeant_T001_Box(tmptestdir):
    T001_Box.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T002_Tubs(tmptestdir):
    T002_Tubs.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T003_CutTubs(tmptestdir):
    T003_CutTubs.Test(
        vis=False,
        interactive=False,
        type=T003_CutTubs.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )
    T003_CutTubs.Test(
        vis=False, interactive=False, type=T003_CutTubs.flat_ends, outputPath=tmptestdir
    )
    T0031_CutTubs_number.Test(vis=False, interactive=False, outputPath=tmptestdir)
    T0032_CutTubs_string.Test(vis=False, interactive=False, outputPath=tmptestdir)
    # TODO
    # T0033_CutTubs_expression.Test(vis=False, interactive=False, outputPath=tmptestdir)
    T0034_CutTubs_DefineTree.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T004_Cons(tmptestdir):
    try:
        T004_Cons.Test(
            vis=False,
            interactive=False,
            type=T004_Cons.r1min_gt_r1max,
            writeNISTMaterials=writeNISTMaterials,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass

    try:
        T004_Cons.Test(
            vis=False,
            interactive=False,
            type=T004_Cons.r2min_gt_r2max,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass

    try:
        T004_Cons.Test(
            vis=False,
            interactive=False,
            type=T004_Cons.dphi_gt_2pi,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass

    T004_Cons.Test(
        vis=False, interactive=False, type=T004_Cons.dphi_eq_2pi, outputPath=tmptestdir
    )
    T004_Cons.Test(
        vis=False, interactive=False, type=T004_Cons.cone_up, outputPath=tmptestdir
    )
    T004_Cons.Test(
        vis=False,
        interactive=False,
        type=T004_Cons.inner_cylinder,
        outputPath=tmptestdir,
    )

    T004_Cons.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T005_Para(tmptestdir):
    T005_Para.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T006_Trd(tmptestdir):
    T006_Trd.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T007_Trap(tmptestdir):
    T007_Trap.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T008_Sphere(tmptestdir):
    assert T008_Sphere.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T009_Orb(tmptestdir):
    T009_Orb.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T010_Torus(tmptestdir):
    T010_Torus.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T011_Polycone(tmptestdir):
    T011_Polycone.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T012_GenericPolycone(tmptestdir):
    T012_GenericPolycone.Test(
        vis=False,
        interactive=False,
        type=T012_GenericPolycone.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    try:
        T012_GenericPolycone.Test(
            vis=False,
            interactive=False,
            type=T012_GenericPolycone.two_planes,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass


def test_PythonGeant_T013_Polyhedra(tmptestdir):
    T013_Polyhedra.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T014_GenericPolyhedra(tmptestdir):
    T014_GenericPolyhedra.Test(
        vis=False,
        interactive=False,
        type=T014_GenericPolyhedra.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    try:
        T014_GenericPolyhedra.Test(
            vis=False,
            interactive=False,
            type=T014_GenericPolyhedra.two_planes,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass


def test_PythonGeant_T015_EllipticalTube(tmptestdir):
    T015_EllipticalTube.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T016_Ellipsoid(tmptestdir):
    assert T016_Ellipsoid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T017_EllipticalCone(tmptestdir):
    T017_EllipticalCone.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    try:
        T017_EllipticalCone.Test(
            vis=False,
            interactive=False,
            type=T017_EllipticalCone.zcut_outofrange,
            writeNISTMaterials=writeNISTMaterials,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass


def test_PythonGeant_T018_Paraboloid(tmptestdir):
    T018_Paraboloid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T019_Hyperboloid(tmptestdir):
    T019_Hyperboloid.Test(
        vis=False,
        interactive=False,
        type=T019_Hyperboloid.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    T019_Hyperboloid.Test(
        vis=False,
        interactive=False,
        type=T019_Hyperboloid.rmin_eq_zero,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    try:
        T019_Hyperboloid.Test(
            vis=False,
            interactive=False,
            type=T019_Hyperboloid.rmin_gt_rmax,
            writeNISTMaterials=writeNISTMaterials,
            outputPath=tmptestdir,
        )
    except ValueError:
        pass


def test_PythonGeant_T020_Tet(tmptestdir):
    T020_Tet.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T021_ExtrudedSolid(tmptestdir):
    T021_ExtrudedSolid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T022_TwistedBox(tmptestdir):
    T022_TwistedBox.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T023_TwistedTrap(tmptestdir):
    T023_TwistedTrap.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T024_TwistedTrd(tmptestdir):
    T024_TwistedTrd.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T025_TwistedTubs(tmptestdir):
    T025_TwistedTubs.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T026_GenericTrap(tmptestdir):
    T026_GenericTrap.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T028_Union(tmptestdir):
    T028_Union.Test(
        vis=False,
        interactive=False,
        disjoint=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    T028_Union.Test(
        vis=False,
        interactive=False,
        disjoint=True,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T029_Subtraction(tmptestdir):
    T029_Subtraction.Test(
        vis=False,
        interactive=False,
        nullMesh=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    # try :
    #    T029_Subtraction.Test(False,False,True)
    # except pyg4ometry.exceptions.NullMeshError :
    #    pass


def test_PythonGeant_T030_Intersection(tmptestdir):
    T030_Intersection.Test(
        vis=False,
        interactive=False,
        type=T030_Intersection.normal,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )

    # try :
    #    T030_Intersection.Test(False,False,T030_Intersection.non_intersecting)
    # except pyg4ometry.exceptions.NullMeshError :
    #    pass


def test_PythonGeant_T031_MultiUnion(tmptestdir):
    T031_MultiUnion.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T032_Scaled(tmptestdir):
    T032_Scaled.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T033_Tessellated(tmptestdir):
    T033_TessellatedSolid.Test(
        vis=False,
        interactive=False,
        writeNISTMaterials=writeNISTMaterials,
        outputPath=tmptestdir,
    )


def test_PythonGeant_T101_PhysicalLogical(tmptestdir):
    T101_physical_logical.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T102_OverlapMone(tmptestdir):
    T102_overlap_none.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T103_OverlapCopl(tmptestdir):
    T103_overlap_copl.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T103_OverlapCopl_Simple(tmptestdir):
    T103_overlap_copl_simple.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T104_OverlapVolu(tmptestdir):
    T104_overlap_volu.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T105_Assembly(tmptestdir):
    T105_assembly.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T106_ReplicaX(tmptestdir):
    T106_replica_x.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T107_ReplicaY(tmptestdir):
    T107_replica_y.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T108_ReplicaZ(tmptestdir):
    T108_replica_z.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T109_ReplicaPhi(tmptestdir):
    T109_replica_phi.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T110_ReplicaRho(tmptestdir):
    T110_replica_rho.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T111_parameterised_box(tmptestdir):
    T111_parameterised_box.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T112_parameterised_tube(tmptestdir):
    T112_parameterised_tube.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T201_Materials(tmptestdir):
    T201_Materials.Test_MaterialPredefined(outputPath=tmptestdir)
    T201_Materials.Test_MaterialSingleElement(outputPath=tmptestdir)
    T201_Materials.Test_MaterialCompoundMassFraction(outputPath=tmptestdir)
    T201_Materials.Test_MaterialCompoundAtoms(outputPath=tmptestdir)
    T201_Materials.Test_MaterialMixture(outputPath=tmptestdir)
    T201_Materials.Test_MaterialIsotopes(outputPath=tmptestdir)


def test_PythonGeant_T202_OpticalSurface(tmptestdir):
    T202_OpticalSurface.Test_OpticalSurface(outputPath=tmptestdir)


def test_PythonGeant_T203_MaterialsRegistry(tmptestdir):
    T203_MaterialsRegistry.Test_MaterialsRegistry(outputPath=tmptestdir)


def test_PythonGeant_T204_NIST_Element(tmptestdir):
    T204_NIST_Element.Test_NIST_Element(outputPath=tmptestdir)


def test_PythonGeant_T205_NIST_Material(tmptestdir):
    T205_NIST_Material.Test_NIST_Material(outputPath=tmptestdir)


def test_PythonGeant_T400_MergeRegistry(tmptestdir):
    T400_MergeRegistry.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T401_MergeRegistry_Box(tmptestdir):
    T401_MergeRegistry_Box.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T402_MergeRegistry_Tubs(tmptestdir):
    T402_MergeRegistry_Tubs.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T403_MergeRegistry_CutTubs(tmptestdir):
    T403_MergeRegistry_CutTubs.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T404_MergeRegistry_Cons(tmptestdir):
    T404_MergeRegistry_Cons.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T405_MergeRegistry_Para(tmptestdir):
    T405_MergeRegistry_Para.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T406_MergeRegistry_Trd(tmptestdir):
    T406_MergeRegistry_Trd.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T407_MergeRegistry_Trap(tmptestdir):
    T407_MergeRegistry_Trap.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T408_MergeRegistry_Sphere(tmptestdir):
    T408_MergeRegistry_Sphere.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T409_MergeRegistry_Orb(tmptestdir):
    T409_MergeRegistry_Orb.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T410_MergeRegistry_Torus(tmptestdir):
    T410_MergeRegistry_Torus.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T411_MergeRegistry_Polycone(tmptestdir):
    T411_MergeRegistry_Polycone.Test(
        vis=False, interactive=tmptestdir, outputPath=tmptestdir
    )


def test_PythonGeant_T412_MergeRegistry_GenericPolycone(tmptestdir):
    T412_MergeRegistry_GenericPolycone.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T413_MergeRegistry_Polyhedra(tmptestdir):
    T413_MergeRegistry_Polyhedra.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T414_MergeRegistry_GenericPolyhedra(tmptestdir):
    T414_MergeRegistry_GenericPolyhedra.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T415_MergeRegistry_EllipticalTube(tmptestdir):
    T415_MergeRegistry_EllipticalTube.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T416_MergeRegistry_Ellipsoid(tmptestdir):
    T416_MergeRegistry_Ellipoid.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T417_MergeRegistry_EllipticalCone(tmptestdir):
    T417_MergeRegistry_EllipticalCone.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T418_MergeRegistry_EllipticalParaboloid(tmptestdir):
    T418_MergeRegistry_Paraboloid.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T419_MergeRegistry_Hyperboloid(tmptestdir):
    T419_MergeRegistry_Hyperboloid.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T420_MergeRegistry_Tet(tmptestdir):
    T420_MergeRegistry_Tet.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T421_MergeRegistry_ExtrudedSolid(tmptestdir):
    T421_MergeRegistry_ExtrudedSolid.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T422_MergeRegistry_TwistedBox(tmptestdir):
    T422_MergeRegistry_TwistedBox.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T423_MergeRegistry_TwistedTrap(tmptestdir):
    T423_MergeRegistry_TwistedTrap.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T424_MergeRegistry_TwistedTrd(tmptestdir):
    T424_MergeRegistry_TwistedTrd.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T425_MergeRegistry_TwistedTubs(tmptestdir):
    T425_MergeRegistry_TwistedTubs.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T426_MergeRegistry_GenericTrap(tmptestdir):
    T426_MergeRegistry_GenericTrap.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T428_MergeRegistry_Union(tmptestdir):
    T428_MergeRegistry_Union.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T429_MergeRegistry_Subtraction(tmptestdir):
    T429_MergeRegistry_Subtraction.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T430_MergeRegistry_Intersection(tmptestdir):
    T430_MergeRegistry_Intersection.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T431_MergeRegistry_MultiUnion(tmptestdir):
    T431_MergeRegistry_MultiUnion.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T432_MergeRegistryBoxAssemblyConverion(tmptestdir):
    T432_MergeRegistry_Box_AssemblyConversion.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T433_MergeRegistry_Scale(tmptestdir):
    T433_MergeRegistry_Scale.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T434_MergeRegistry_CollapseAssembly(tmptestdir):
    T434_MergeRegistry_CollapseAssembly.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )


def test_PythonGeant_T600_LVTessellated(tmptestdir):
    T600_LVTessellated.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T601_reflect(tmptestdir):
    T601_reflect.Test(vis=False, interactive=False, outputPath=tmptestdir)


# def test_PythonGeant_T602_lv_cull_daughters():
#    assert T602_lv_cull_daughters.Test()["testStatus"]

# def test_PythonGeant_T603_lv_change_solid_and_trim():
#    assert T603_lv_change_solid_and_trim.Test()["testStatus"]

# def test_PythonGeant_T604_lv_change_solid_and_trim_rot():
#    assert T604_lv_change_solid_and_timr_rot.Test()["testStatus"]


def test_PythonGeant_T605_LvChangeSolid(tmptestdir):
    T605_LvChangeSolid.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T606_LvClipSolid(tmptestdir):
    T606_LvClipSolid.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T607_LvChangeAndClipSolid(tmptestdir):
    T607_LvChangeAndClipSolid.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T608_LvClipSolidRecursive(tmptestdir):
    T608_LvClipSolidRecursive.Test(vis=False, interactive=False, outputPath=tmptestdir)


def test_PythonGeant_T609_LvClipSolidRecursiveAssembly(tmptestdir):
    T609_LvClipSolidRecursiveAssembly.Test(
        vis=False, interactive=False, outputPath=tmptestdir
    )
