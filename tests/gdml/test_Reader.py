import pyg4ometry

import pytest as _pytest
import os as _os
import git as _git

from subprocess import Popen as _Popen, PIPE as _PIPE
from hashlib import md5 as _md5
from collections import OrderedDict as _OrderedDict

#logger = _log.getLogger()
#logger.disabled = True

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
    if vis : 
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
        print("Geant4 test executable not found in {}, skip test.".format(script_path))
        return True

    proc = _Popen([script_path, _pj(filename), str(int(visualiser)), str(int(physics))],
                  stdout=_PIPE, stderr=_PIPE)
    outs, errs = proc.communicate()

    status = proc.returncode
    if status:
        if verbose:
            print("\nError! Geant4 load failed: \nOutput>>> {} \nErrors>>> {}".format(outs, errs))
        return False

    return True

def checkIfGdmlFileUpdated(filename) :
    filename    = _os.path.basename(filename)
    repo        = _git.Repo(_os.path.join(_os.path.dirname(__file__),"../../../../"))
    head_commit = repo.head.commit
    diffs       = head_commit.diff(None)

    for d in diffs :
        if _os.path.basename(d.a_path).find(filename) != -1 :
            return True

    return False


# solid name : (nslice , nstack)
# nslice is normally used for granularity of curvature in radius
# nstack is normally used for granularity of curvature in Z
# solids not listed here do not have discretised curves
curved_solids = {
    "Tubs" : (16, None),
    "CutTubs" : (16, None),
    "Cons" : (16, None),
    "Sphere" : (6, 6),
    "Orb" : (16, 8),
    "Torus" : (6, 6),
    "Polycone" : (16, None),
    "GenericPolycone" : (16, None),
    "EllipticalTube" : (6, 6),
    "Ellipsoid" : (8, 8),
    "EllipticalCone" : (16, 16),
    "Paraboloid" : (16, 8),
    "Hype" : (6, 6),
    "TwistedBox" : (None, 20),
    "TwistedTrap" : (None, 20),
    "TwistedTrd" : (None, 20),
    "TwistedTubs" : (16, 16),
    "GenericTrap" : (None, 20),
}

def computeGDMLFileChecksum(filename):
    with open(_pj(filename), "r") as gdml_file:
        contents = gdml_file.read()
    checksum = int(_md5(contents.encode()).hexdigest(), 16)

    return checksum

def loadChecksumTable():
    checksum_filepath = _pj("processed_file_checksums.dat")
    checksum_table = _OrderedDict()

    if _os.path.exists(checksum_filepath):
        with open(checksum_filepath, "r") as checksum_file:
            for line in checksum_file:
                sline = line.split()
                checksum_table[sline[0]] = int(sline[1])

    return checksum_table


def writeChecksumTable(checksum_table):
    checksum_filepath = _pj("processed_file_checksums.dat")
    with open(checksum_filepath, "w") as checksum_file:
        for filename, checksum in checksum_table.items():
            checksum_file.write("{}\t{}\n".format(filename, checksum))


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

def test_GdmlLoad_001_BoxLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("001_box.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["box1"]), -1)

def test_GdmlLoad_002_TubeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("002_tubs.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["tube1"]), -1)

def test_GdmlLoad_003_CutTubeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("003_cut_tubs.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["cuttube1"]), -1)

def test_GdmlLoad_004_ConeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("004_cons.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["cone1"]), -1)

def test_GdmlLoad_005_ParaLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("005_para.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["para1"]), -1)

def test_GdmlLoad_006_TrdLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("006_trd.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["trd1"]), -1)

def test_GdmlLoad_007_TrapLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("007_trap.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["trap1"]), -1)

def test_GdmlLoad_008_SphereLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("008_sphere.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["sphere1"]), -1)

def test_GdmlLoad_009_OrbLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("009_orb.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["orb1"]), -1)

def test_GdmlLoad_010_TorusLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("010_torus.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["torus1"]), -1)

def test_GdmlLoad_011_PolyconeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("011_polycone.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["polycone1"]), -1)

def test_GdmlLoad_012_GenericPolyconeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("012_generic_polycone.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["genpoly1"]), -1)

def test_GdmlLoad_013_PolyhedraLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("013_polyhedra.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["polyhedra1"]), -1)

def test_GdmlLoad_014_GenericPolyhedraLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("014_generic_polyhedra.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["genpolyhedra1"]), -1)

def test_GdmlLoad_015_EltubeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("015_eltube.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["eltube1"]), -1)

def test_GdmlLoad_016_EllipsoidLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("016_ellipsoid.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["ellipsoid"]), -1)

def test_GdmlLoad_017_ElconeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("017_elcone.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["elcone1"]), -1)

def test_GdmlLoad_018_ParaboloidLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("018_paraboloid.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["paraboloid1"]), -1)

def test_GdmlLoad_019_HypeLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("019_hype.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["hype1"]), -1)

def test_GdmlLoad_020_TetLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("020_tet.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["tet1"]), -1)

def test_GdmlLoad_021_ExtrudedSolid():
    registry, writtenFilename = pyg4ometryLoadWriteTest("021_xtru.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["xtru1"]), -1)

def test_GdmlLoad_022_TwistedBox():
    registry, writtenFilename = pyg4ometryLoadWriteTest("022_twisted_box.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["twistbox1"]), -1)

def test_GdmlLoad_023_TwistedTrap():
    registry, writtenFilename = pyg4ometryLoadWriteTest("023_twisted_trap.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["twisttrap1"]), -1)

def test_GdmlLoad_024_TwistedTrd():
    registry, writtenFilename = pyg4ometryLoadWriteTest("024_twisted_trd.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["twisttrd1"]), -1)

def test_GdmlLoad_025_TwistedTubs():
    registry, writtenFilename = pyg4ometryLoadWriteTest("025_twisted_tube.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["twisttube1"]), -1)

def test_GdmlLoad_026_GenericTrap():
    registry, writtenFilename = pyg4ometryLoadWriteTest("026_generic_trap.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["arb81"]), -1)

def test_GdmlLoad_027_TessellatedSolid():
    registry, writtenFilename = pyg4ometryLoadWriteTest("027_tesselated.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["tessellated"]), -1)

def test_GdmlLoad_028_UnionLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("028_union.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["union1"]), -1)

def test_GdmlLoad_029_SubtractionLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("029_subtraction.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["subtraction1"]), -1)

def test_GdmlLoad_030_IntersetionLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("030_intersection.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["intersection1"]), -1)

def test_GdmlLoad_031_MultiUnionLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("031_multiUnion.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["multiunion1"]), -1)

def test_GdmlLoad_032_ScaledLoad():
    registry, writtenFilename = pyg4ometryLoadWriteTest("032_scaled.gdml")
    assert(geant4LoadTest(writtenFilename))
    #self.assertEqual(getSolidChecksum(registry.solidDict["box1Scaled"]), -1)

def test_GdmlLoad_106_ReplicaVolume_x():
    registry, writtenFilename = pyg4ometryLoadWriteTest("106_replica_x.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_107_ReplicaVolume_y():
    registry, writtenFilename = pyg4ometryLoadWriteTest("107_replica_y.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_108_ReplicaVolume_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("108_replica_z.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_109_ReplicaVolume_phi():
    registry, writtenFilename = pyg4ometryLoadWriteTest("109_replica_phi.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_110_ReplicaVolume_rho():
    registry, writtenFilename = pyg4ometryLoadWriteTest("110_replica_rho.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "replica":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_111_ParameterisedVolume_box():
    registry, writtenFilename = pyg4ometryLoadWriteTest("111_parameterised_box.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_112_ParameterisedVolume_tube():
    registry, writtenFilename = pyg4ometryLoadWriteTest("112_parameterised_tube.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_113_ParameterisedVolume_cone():
    registry, writtenFilename = pyg4ometryLoadWriteTest("113_parameterised_cone.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_114_ParameterisedVolume_orb():
    registry, writtenFilename = pyg4ometryLoadWriteTest("114_parameterised_orb.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_115_ParameterisedVolume_sphere():
    registry, writtenFilename = pyg4ometryLoadWriteTest("115_parameterised_sphere.gdml")
    assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_116_ParameterisedVolume_torus():
    registry, writtenFilename = pyg4ometryLoadWriteTest("116_parameterised_torus.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_117_ParameterisedVolume_hype():
    registry, writtenFilename = pyg4ometryLoadWriteTest("117_parameterised_hype.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_118_ParameterisedVolume_para():
    registry, writtenFilename = pyg4ometryLoadWriteTest("118_parameterised_para.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_119_ParameterisedVolume_trd():
    registry, writtenFilename = pyg4ometryLoadWriteTest("119_parameterised_trd.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_120_ParameterisedVolume_trap():
    registry, writtenFilename = pyg4ometryLoadWriteTest("120_parameterised_trap.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_121_ParameterisedVolume_polycone():
    registry, writtenFilename = pyg4ometryLoadWriteTest("121_parameterised_polycone.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_122_ParameterisedVolume_polyhedron():
    registry, writtenFilename = pyg4ometryLoadWriteTest("122_parameterised_polyhedron.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_123_ParameterisedVolume_ellipsoid():
    registry, writtenFilename = pyg4ometryLoadWriteTest("123_parameterised_ellipsoid.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "parametrised":
            solid= volume.meshes[0].solid

def test_GdmlLoad_124_DivisionVolume_box_x():
    registry, writtenFilename = pyg4ometryLoadWriteTest("124_division_box_x.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_125_DivisionVolume_box_y():
    registry, writtenFilename = pyg4ometryLoadWriteTest("125_division_box_y.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_126_DivisionVolume_box_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("126_division_box_z.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_127_DivisionVolume_tubs_rho():
    registry, writtenFilename = pyg4ometryLoadWriteTest("127_division_tubs_rho.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_128_DivisionVolume_tubs_phi():
    registry, writtenFilename = pyg4ometryLoadWriteTest("128_division_tubs_phi.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_129_DivisionVolume_tubs_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("129_division_tubs_z.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_130_DivisionVolume_cons_rho():
    registry, writtenFilename = pyg4ometryLoadWriteTest("130_division_cons_rho.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_131_DivisionVolume_cons_phi():
    registry, writtenFilename = pyg4ometryLoadWriteTest("131_division_cons_phi.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_132_DivisionVolume_cons_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("132_division_cons_z.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_133_DivisionVolume_trd_x():
    registry, writtenFilename = pyg4ometryLoadWriteTest("133_division_trd_x.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_134_DivisionVolume_trd_y():
    registry, writtenFilename = pyg4ometryLoadWriteTest("134_division_trd_y.gdml")
    assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_135_DivisionVolume_trd_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("135_division_trd_z.gdml")
    #assert(geant4LoadTest(writtenFilename))

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_136_DivisionVolume_para_x():
    registry, writtenFilename = pyg4ometryLoadWriteTest("136_division_para_x.gdml")
    #assert(geant4LoadTest(writtenFilename))  # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_137_DivisionVolume_para_y():
    registry, writtenFilename = pyg4ometryLoadWriteTest("137_division_para_y.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_138_DivisionVolume_para_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("138_division_para_z.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_139_DivisionVolume_polycone_rho():
    registry, writtenFilename = pyg4ometryLoadWriteTest("139_division_polycone_rho.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_140_DivisionVolume_polycone_phi():
    registry, writtenFilename = pyg4ometryLoadWriteTest("140_division_polycone_phi.gdml")
    # assert(geant4LoadTest(writtenFilename)) # Faulty gdml

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_141_DivisionVolume_polycone_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("141_division_polycone_z.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_142_DivisionVolume_polyhedra_rho():
    registry, writtenFilename = pyg4ometryLoadWriteTest("142_division_polyhedra_rho.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_143_DivisionVolume_polyhedra_phi():
    registry, writtenFilename = pyg4ometryLoadWriteTest("143_division_polyhedra_phi.gdml")
    #assert(geant4LoadTest(writtenFilename))   # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_144_DivisionVolume_polyhedra_z():
    registry, writtenFilename = pyg4ometryLoadWriteTest("144_division_polyhedra_z.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Faulty in Geant4

    for volname, volume in registry.physicalVolumeDict.items():
        if volume.type == "division":
            solid= volume.meshes[0].solid
    #self.assertEqual(getSolidChecksum(solid), -1)

def test_GdmlLoad_150_OpticalSurfaces():
    registry, writtenFilename = pyg4ometryLoadWriteTest("150_opticalsurfaces.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_201_Materials():
    registry, writtenFilename = pyg4ometryLoadWriteTest("201_materials.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_Auxiliary():
    registry, writtenFilename = pyg4ometryLoadWriteTest("202_auxiliary.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_Entity():
    # Need to process the GDML file to inject the absolute path to the entity file
    with open(_pj("203_entity.gdml")) as infile:
        contents = infile.read()

        contents_replaced = contents.replace("203_materials.xml", _pj("203_materials.xml"))
        with open(_pj("203_temp.gdml"), "w") as tempfile:
            tempfile.write(contents_replaced)

    registry, writtenFilename = pyg4ometryLoadWriteTest("203_temp.gdml")
    _os.unlink(_pj("203_temp.gdml"))
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_300_MalformedGdml():
    import xml.parsers.expat                 as _expat

    try :
        r = pyg4ometry.gdml.Reader(_pj("./300_malformed_gdml.gdml"))
    except _expat.ExpatError:
        pass

def test_GdmlLoad_301_Quantity():
    assert(pyg4ometryLoadWriteTest("301_quantity.gdml"))

def test_GdmlLoad_302_Variable():
    assert(pyg4ometryLoadWriteTest("302_variable.gdml"))

def test_GdmlLoad_303_Matrix():
    assert(pyg4ometryLoadWriteTest("303_matrix.gdml"))

def test_GdmlLoad_304_Scale():
    assert(pyg4ometryLoadWriteTest("304_scale.gdml"))

def test_GdmlLoad_305_UnrecognisedDefine():
    assert(pyg4ometryLoadWriteTest("305_unrecognised_define.gdml"))
    
def test_GdmlLoad_306_Tubs_Bad_Pi():
    # check it raises an exception
    with _pytest.raises(ValueError):
        pyg4ometryLoadWriteTest("306_tubs_hand_written_bad_pi.gdml")

def test_GdmlLoad_ChargeExhangeMC():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/ChargeExchangeMC/lht.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Overlaps in the original file

def test_GdmlLoad_G01assembly():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/assembly.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Overlaps in the original file

def test_GdmlLoad_G01auxiliary():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/auxiliary.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01axes():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/axes.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Overlaps in the original file

def test_GdmlLoad_G01divisionvol():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/divisionvol.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01mat_nist():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/mat_nist.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01multiUnion():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/multiUnion.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01pTube():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/pTube.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01parameterized():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/parameterized.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01replicated():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/replicated.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01scale():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/scale.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01solids():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/solids.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G01tess():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G01/tess.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G02test():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G02/test.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_G04auxiliary():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/G04/auxiliary.gdml")
    assert(geant4LoadTest(writtenFilename))

def test_GdmlLoad_Par02FullDetector():
    registry, writtenFilename = pyg4ometryLoadWriteTest("../gdmlG4examples/Par02/Par02FullDetector.gdml")
    #assert(geant4LoadTest(writtenFilename)) # Overlaps in the orignal file

