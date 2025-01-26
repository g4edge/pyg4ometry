import pyg4ometry

import pytest
import os as _os
import git as _git

from subprocess import Popen as _Popen, PIPE as _PIPE
from hashlib import md5 as _md5
from collections import OrderedDict as _OrderedDict

# logger = _log.getLogger()
# logger.disabled = True


def _pj(filename):
    """
    Append the absolute path to *this* directory to the filename so the tests
    can be ran from anywhere
    """
    return _os.path.join(_os.path.dirname(__file__), filename)


def pyg4ometryLoadWriteTest(filename, vis=False, interactive=False):
    filepath = _pj(filename)

    # Loading
    reader = pyg4ometry.gdml.Reader(filepath)
    registry = reader.getRegistry()

    # World logical
    worldLogical = registry.getWorldVolume()

    # test extent of physical volume
    extentBB = worldLogical.extent(includeBoundingSolid=True)

    # Visualisation
    if vis:
        v = pyg4ometry.visualisation.VtkViewer()
        v.addLogicalVolume(registry.getWorldVolume())
        v.addAxes(pyg4ometry.visualisation.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    # Writing
    newFilename = filepath.replace(".gdml", "_processed.gdml")

    writer = pyg4ometry.gdml.Writer()
    writer.addDetector(registry)
    writer.write(newFilename)

    return registry, newFilename


def geant4LoadTest(filename, visualiser=False, physics=False, verbose=True):
    # check if GDML file has updated
    # if not checkIfGdmlFileUpdated(filename) :
    #     return True

    print("geant4LoadTest> running G4")
    script_path = _pj("simple_G4_loader/build/simple_loader")
    if not _os.path.isfile(script_path):
        print(f"Geant4 test executable not found in {script_path}, skip test.")
        return True

    proc = _Popen(
        [script_path, _pj(filename), str(int(visualiser)), str(int(physics))],
        stdout=_PIPE,
        stderr=_PIPE,
    )
    outs, errs = proc.communicate()

    status = proc.returncode
    if status:
        if verbose:
            print(f"\nError! Geant4 load failed: \nOutput>>> {outs} \nErrors>>> {errs}")
        return False

    return True


def checkIfGdmlFileUpdated(filename):
    filename = _os.path.basename(filename)
    repo = _git.Repo(_os.path.join(_os.path.dirname(__file__), "../../../../"))
    head_commit = repo.head.commit
    diffs = head_commit.diff(None)

    for d in diffs:
        if _os.path.basename(d.a_path).find(filename) != -1:
            return True

    return False


# solid name : (nslice , nstack)
# nslice is normally used for granularity of curvature in radius
# nstack is normally used for granularity of curvature in Z
# solids not listed here do not have discretised curves
curved_solids = {
    "Tubs": (16, None),
    "CutTubs": (16, None),
    "Cons": (16, None),
    "Sphere": (6, 6),
    "Orb": (16, 8),
    "Torus": (6, 6),
    "Polycone": (16, None),
    "GenericPolycone": (16, None),
    "EllipticalTube": (6, 6),
    "Ellipsoid": (8, 8),
    "EllipticalCone": (16, 16),
    "Paraboloid": (16, 8),
    "Hype": (6, 6),
    "TwistedBox": (None, 20),
    "TwistedTrap": (None, 20),
    "TwistedTrd": (None, 20),
    "TwistedTubs": (16, 16),
    "GenericTrap": (None, 20),
}


def computeGDMLFileChecksum(filename):
    with open(_pj(filename)) as gdml_file:
        contents = gdml_file.read()
    checksum = int(_md5(contents.encode()).hexdigest(), 16)

    return checksum


def loadChecksumTable():
    checksum_filepath = _pj("processed_file_checksums.dat")
    checksum_table = _OrderedDict()

    if _os.path.exists(checksum_filepath):
        with open(checksum_filepath) as checksum_file:
            for line in checksum_file:
                sline = line.split()
                checksum_table[sline[0]] = int(sline[1])

    return checksum_table


def writeChecksumTable(checksum_table):
    checksum_filepath = _pj("processed_file_checksums.dat")
    with open(checksum_filepath, "w") as checksum_file:
        for filename, checksum in checksum_table.items():
            checksum_file.write(f"{filename}\t{checksum}\n")


def validateProcessedFile(filename):
    checksum_table = loadChecksumTable()
    checksum = computeGDMLFileChecksum(filename)
    checksum = computeGDMLFileChecksum(filename)

    isValid = False
    # Handle missing cases by using get
    if checksum_table.get(filename, -1) == checksum:
        isValid = True
    else:
        isValid = geant4LoadTest(filename)
        if isValid:
            checksum_table[filename] = checksum
            writeChecksumTable(checksum_table)

    return isValid


def getSolidChecksum(solid):
    if solid.type in curved_solids:
        mesh_density = curved_solids[solid.type]
        if mesh_density[0]:
            setattr(solid, "nslice", mesh_density[0])
        if mesh_density[1]:
            setattr(solid, "nstack", mesh_density[1])

    checksum = hash(solid.pycsgmesh())
    return checksum


def test_GdmlLoad_001_BoxLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/001_box.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["box1"]), -1)


def test_GdmlLoad_002_TubeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/002_tubs.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["tube1"]), -1)


def test_GdmlLoad_003_CutTubeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/003_cut_tubs.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["cuttube1"]), -1)


def test_GdmlLoad_004_ConeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/004_cons.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["cone1"]), -1)


def test_GdmlLoad_005_ParaLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/005_para.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["para1"]), -1)


def test_GdmlLoad_006_TrdLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/006_trd.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["trd1"]), -1)


def test_GdmlLoad_007_TrapLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/007_trap.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["trap1"]), -1)


def test_GdmlLoad_008_SphereLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/008_sphere.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["sphere1"]), -1)


def test_GdmlLoad_009_OrbLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/009_orb.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["orb1"]), -1)


def test_GdmlLoad_010_TorusLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/010_torus.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["torus1"]), -1)


def test_GdmlLoad_011_PolyconeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/011_polycone.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["polycone1"]), -1)


def test_GdmlLoad_012_GenericPolyconeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/012_generic_polycone.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["genpoly1"]), -1)


def test_GdmlLoad_013_PolyhedraLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/013_polyhedra.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["polyhedra1"]), -1)


def test_GdmlLoad_014_GenericPolyhedraLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/014_generic_polyhedra.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["genpolyhedra1"]), -1)


def test_GdmlLoad_015_EltubeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/015_eltube.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["eltube1"]), -1)


def test_GdmlLoad_016_EllipsoidLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/016_ellipsoid.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["ellipsoid"]), -1)


def test_GdmlLoad_017_ElconeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/017_elcone.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["elcone1"]), -1)


def test_GdmlLoad_018_ParaboloidLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/018_paraboloid.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["paraboloid1"]), -1)


def test_GdmlLoad_019_HypeLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/019_hype.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["hype1"]), -1)


def test_GdmlLoad_020_TetLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/020_tet.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["tet1"]), -1)


def test_GdmlLoad_021_ExtrudedSolid(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/021_xtru.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["xtru1"]), -1)


def test_GdmlLoad_022_TwistedBox(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/022_twisted_box.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["twistbox1"]), -1)


def test_GdmlLoad_023_TwistedTrap(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/023_twisted_trap.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["twisttrap1"]), -1)


def test_GdmlLoad_024_TwistedTrd(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/024_twisted_trd.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["twisttrd1"]), -1)


def test_GdmlLoad_025_TwistedTubs(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/025_twisted_tube.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["twisttube1"]), -1)


def test_GdmlLoad_026_GenericTrap(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/026_generic_trap.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["arb81"]), -1)


def test_GdmlLoad_027_TessellatedSolid(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/027_tesselated.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["tessellated"]), -1)


def test_GdmlLoad_028_UnionLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/028_union.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["union1"]), -1)


def test_GdmlLoad_029_SubtractionLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/029_subtraction.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["subtraction1"]), -1)


def test_GdmlLoad_030_IntersetionLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/030_intersection.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["intersection1"]), -1)


def test_GdmlLoad_031_MultiUnionLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/031_multiUnion.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["multiunion1"]), -1)


def test_GdmlLoad_032_ScaledLoad(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/032_scaled.gdml"])
    assert geant4LoadTest(writtenFilename)
    # self.assertEqual(getSolidChecksum(registry.solidDict["box1Scaled"]), -1)


def test_GdmlLoad_106_ReplicaVolume_x(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/106_replica_x.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_107_ReplicaVolume_y(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/107_replica_y.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_108_ReplicaVolume_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/108_replica_z.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_109_ReplicaVolume_phi(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/109_replica_phi.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_110_ReplicaVolume_rho(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/110_replica_rho.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_111_ParameterisedVolume_box(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/111_parameterised_box.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_112_ParameterisedVolume_tube(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/112_parameterised_tube.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_113_ParameterisedVolume_cone(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/113_parameterised_cone.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_114_ParameterisedVolume_orb(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/114_parameterised_orb.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_115_ParameterisedVolume_sphere(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/115_parameterised_sphere.gdml"]
    )
    assert geant4LoadTest(writtenFilename)  # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_116_ParameterisedVolume_torus(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/116_parameterised_torus.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_117_ParameterisedVolume_hype(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/117_parameterised_hype.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_118_ParameterisedVolume_para(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/118_parameterised_para.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_119_ParameterisedVolume_trd(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/119_parameterised_trd.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_120_ParameterisedVolume_trap(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/120_parameterised_trap.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_121_ParameterisedVolume_polycone(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/121_parameterised_polycone.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_122_ParameterisedVolume_polyhedron(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/122_parameterised_polyhedron.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_123_ParameterisedVolume_ellipsoid(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/123_parameterised_ellipsoid.gdml"]
    )
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid = volume.meshes[0].solid


def test_GdmlLoad_124_DivisionVolume_box_x(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/124_division_box_x.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_125_DivisionVolume_box_y(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/125_division_box_y.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_126_DivisionVolume_box_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/126_division_box_z.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_127_DivisionVolume_tubs_rho(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/127_division_tubs_rho.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_128_DivisionVolume_tubs_phi(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/128_division_tubs_phi.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_129_DivisionVolume_tubs_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/129_division_tubs_z.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_130_DivisionVolume_cons_rho(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/130_division_cons_rho.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_131_DivisionVolume_cons_phi(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/131_division_cons_phi.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_132_DivisionVolume_cons_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/132_division_cons_z.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_133_DivisionVolume_trd_x(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/133_division_trd_x.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_134_DivisionVolume_trd_y(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/134_division_trd_y.gdml"])
    assert geant4LoadTest(writtenFilename)

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_135_DivisionVolume_trd_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/135_division_trd_z.gdml"])
    # assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_136_DivisionVolume_para_x(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/136_division_para_x.gdml"])
    # assert(geant4LoadTest(writtenFilename))  # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_137_DivisionVolume_para_y(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/137_division_para_y.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_138_DivisionVolume_para_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/138_division_para_z.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_139_DivisionVolume_polycone_rho(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/139_division_polycone_rho.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_140_DivisionVolume_polycone_phi(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/140_division_polycone_phi.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename)) # Faulty gdml

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_141_DivisionVolume_polycone_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/141_division_polycone_z.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_142_DivisionVolume_polyhedra_rho(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/142_division_polyhedra_rho.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_143_DivisionVolume_polyhedra_phi(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/143_division_polyhedra_phi.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename))   # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_144_DivisionVolume_polyhedra_z(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/144_division_polyhedra_z.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid = volume.meshes[0].solid
    # self.assertEqual(getSolidChecksum(solid), -1)


def test_GdmlLoad_150_OpticalSurfaces(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/150_opticalsurfaces.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_201_Materials(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/201_materials.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_Auxiliary(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/202_auxiliary.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_Entity(testdata):
    # Need to process the GDML file to inject the absolute path to the entity file
    with open(testdata["gdml/203_entity.gdml"]) as infile:
        contents = infile.read()

        contents_replaced = contents.replace("203_materials.xml", _pj("203_materials.xml"))
        with open(_pj("203_temp.gdml"), "w") as tempfile:
            tempfile.write(contents_replaced)

    # TODO write in tmp dir
    # registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/203_temp.gdml"])


def test_GdmlLoad_300_MalformedGdml(testdata):
    import xml.parsers.expat as _expat

    # TODO reinstate
    # with pytest.raises(_expat.ExpatError):
    #    r = pyg4ometry.gdml.Reader(testdata["gdml/300_malformed.gdml"])


def test_GdmlLoad_301_Quantity(testdata):
    assert pyg4ometryLoadWriteTest(testdata["gdml/301_quantity.gdml"])


def test_GdmlLoad_302_Variable(testdata):
    assert pyg4ometryLoadWriteTest(testdata["gdml/302_variable.gdml"])


def test_GdmlLoad_303_Matrix(testdata):
    assert pyg4ometryLoadWriteTest(testdata["gdml/303_matrix.gdml"])


def test_GdmlLoad_304_Scale(testdata):
    assert pyg4ometryLoadWriteTest(testdata["gdml/304_scale.gdml"])


def test_GdmlLoad_305_UnrecognisedDefine(testdata):
    assert pyg4ometryLoadWriteTest(testdata["gdml/305_unrecognised_define.gdml"])


def test_GdmlLoad_306_Tubs_Bad_Pi(testdata):
    pass
    # TODO check it raises an exception
    # with pytest.raises(ValueError):
    #    pyg4ometryLoadWriteTest(testdata["gdml/306_tubs_hand_written_bad_pi.gdml"])


def test_GdmlLoad_ChargeExhangeMC(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/ChargeExchangeMC/lht.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Overlaps in the original file


def test_GdmlLoad_G01assembly(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/assembly.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Overlaps in the original file


def test_GdmlLoad_G01auxiliary(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/auxiliary.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01axes(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/axes.gdml"])
    # assert(geant4LoadTest(writtenFilename)) # Overlaps in the original file


def test_GdmlLoad_G01divisionvol(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml//G01/divisionvol.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01mat_nist(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/mat_nist.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01multiUnion(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/multiUnion.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01pTube(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/pTube.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01parameterized(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/parameterized.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01replicated(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml//G01/replicated.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01scale(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/scale.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01solids(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/solids.gdml"])
    assert geant4LoadTest(writtenFilename)


def test_GdmlLoad_G01tess(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G01/tess.gdml"])
    # assert(geant4LoadTest(writtenFilename))


def test_GdmlLoad_G02test(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G02/test.gdml"])
    # assert(geant4LoadTest(writtenFilename))


def test_GdmlLoad_G04auxiliary(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(testdata["gdml/G04/auxiliary.gdml"])
    # assert(geant4LoadTest(writtenFilename))


def test_GdmlLoad_Par02FullDetector(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/Par02/Par02FullDetector.gdml"]
    )
    # assert(geant4LoadTest(writtenFilename)) # Overlaps in the orignal file


def test_GdmlLoad_BDSIM_colour(testdata):
    registry, writtenFilename = pyg4ometryLoadWriteTest(
        testdata["gdml/CompoundExamples/bdsim/vkickers-coloured.gdml"]
    )


def test_GdmlLoad_BDSIM_colour_force_visible(testdata):
    filepath = _pj(testdata["gdml/CompoundExamples/bdsim/vkickers-coloured.gdml"])

    reader = pyg4ometry.gdml.Reader(filepath, makeAllVisible=True)
    wlv = reader.getRegistry().getWorldVolume()
    assert wlv.daughterVolumes[0].logicalVolume.visOptions.visible
