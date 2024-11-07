from .. import transformation as _transformation
from .. import geant4 as _geant4
from .. import fluka as _fluka
from .. import pycgal as _pycgal
from ..pycgal.core import PolygonProcessing as _PolygonProcessing
from ..fluka.directive import (
    rotoTranslationFromTra2 as _rotoTranslationFromTra2,
)
import numpy as _np
import copy as _copy
import scipy.linalg as _la

# this should be refactored to rename namespaced (privately)
from ..fluka.body import *

# import matplotlib.pyplot as _plt


def geant4Reg2FlukaReg(greg, logicalVolumeName="", bakeTransforms=False):
    """
    Convert a Geant4 model to a FLUKA one. This is done by handing over a complete
    pyg4ometry.geant4.Registry instance.

    :param greg: geant4 registry
    :type greg: pyg4ometry.geant4.Registry

    returns:  pyg4ometry.fluka.FlukaRegistry
    """

    freg = _fluka.FlukaRegistry()

    if logicalVolumeName == "":
        logi = greg.getWorldVolume()
    else:
        logi = greg.logicalVolumeDict[logicalVolumeName]
    freg = geant4MaterialDict2Fluka(greg.materialDict, freg)
    freg = geant4Logical2Fluka(logi, freg, bakeTransforms)

    return freg


def geant4Logical2Fluka(logicalVolume, flukaRegistry=None, bakeTransforms=False):
    """
    Convert a single logical volume - not the main entry point for the conversion.
    """
    mtra = _np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    tra = _np.array([0, 0, 0])

    if not flukaRegistry:
        flukaRegistry = _fluka.FlukaRegistry()

    flukaNameCount = 0

    # find extent of logical
    extent = logicalVolume.extent(includeBoundingSolid=True)

    rotation = _transformation.matrix2tbxyz(mtra)
    position = tra

    blackBody = _fluka.RPP(
        "BLKBODY",
        2 * extent[0][0] / 10,
        2 * extent[1][0] / 10,
        2 * extent[0][1] / 10,
        2 * extent[1][1] / 10,
        2 * extent[0][2] / 10,
        2 * extent[1][2] / 10,
        transform=_rotoTranslationFromTra2(
            "BBROTDEF", [rotation, position], flukaregistry=flukaRegistry
        ),
        flukaregistry=flukaRegistry,
    )

    fzone = _fluka.Zone()
    fzone.addIntersection(blackBody)

    # create top logical volume
    if logicalVolume.type == "logical":
        flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            logicalVolume.solid,
            mtra,
            tra,
            flukaRegistry,
            commentName=logicalVolume.name,
            bakeTransforms=bakeTransforms,
        )
    elif logicalVolume.type == "assembly":
        e = logicalVolume.extent()
        b = _geant4.solid.Box(
            "ra",
            1.1 * (e[1][0] - e[0][0]),
            1.1 * (e[1][1] - e[0][1]),
            1.1 * (e[1][2] - e[0][2]),
            logicalVolume.registry,
            "mm",
            False,
        )
        flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            b,
            mtra,
            tra,
            flukaRegistry,
            commentName=logicalVolume.name,
            bakeTransforms=bakeTransforms,
        )
    else:
        # avoid warning about flukaMotherOuterRegion being used without assignment
        print(
            "Type (",
            logicalVolume.type,
            ") cannot be converted - skipping: ",
            logicalVolume.name,
        )
        return

    flukaMotherRegion = _copy.deepcopy(flukaMotherOuterRegion)
    flukaNameCount += 1

    for zone in flukaMotherOuterRegion.zones:
        fzone.addSubtraction(zone)

    for dv in logicalVolume.daughterVolumes:
        pvmrot = _transformation.tbzyx2matrix(-_np.array(dv.rotation.eval()))
        pvtra = _np.array(dv.position.eval())
        reflection = _np.diag([1, 1, 1])
        if dv.scale:
            reflection = _np.diag([dv.scale.eval()[0], dv.scale.eval()[1], dv.scale.eval()[2]])
        new_mtra = mtra @ pvmrot @ reflection
        new_tra = mtra @ pvtra + tra

        flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(
            dv, new_mtra, new_tra, flukaRegistry, flukaNameCount, bakeTransforms=bakeTransforms
        )

        # subtract daughters from black body
        for motherZones in flukaMotherRegion.zones:
            for daughterZones in flukaDaughterOuterRegion.zones:
                motherZones.addSubtraction(daughterZones)

    ###########################################
    # create black body region
    ###########################################
    fregion = _fluka.Region("BLKHOLE")
    fregion.addZone(fzone)
    flukaRegistry.addRegion(fregion)

    flukaRegistry.addRegion(flukaMotherRegion)

    ###########################################
    # assign material to blackhole
    ###########################################
    flukaRegistry.addMaterialAssignments("BLCKHOLE", "BLKHOLE")

    ###########################################
    # assign material to region
    ###########################################
    if logicalVolume.type == "logical":
        materialName = logicalVolume.material.name
        materialNameShort = flukaRegistry.materialShortName[materialName]

        try:
            flukaMaterial = flukaRegistry.materials[materialNameShort]
            flukaRegistry.addMaterialAssignments(flukaMaterial, flukaMotherRegion)
        except KeyError:
            pass
    elif logicalVolume.type == "assembly":
        flukaRegistry.addMaterialAssignments("AIR", flukaMotherRegion)

    return flukaRegistry


def geant4PhysicalVolume2Fluka(
    physicalVolume,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    flukaNameCount=0,
    bakeTransforms=False,
):
    # logical volume (outer and complete)
    if physicalVolume.logicalVolume.type == "logical":
        geant4LvOuterSolid = physicalVolume.logicalVolume.solid
        flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            geant4LvOuterSolid,
            mtra,
            tra,
            flukaRegistry,
            commentName=physicalVolume.name,
            bakeTransforms=bakeTransforms,
        )
    elif physicalVolume.logicalVolume.type == "assembly":
        name = "R" + format(flukaNameCount, "04")
        flukaMotherOuterRegion = _fluka.Region(name)
        flukaNameCount += 1
    else:
        # avoid warning about flukaMotherOuterRegion being used without assignment
        print(
            "Type (",
            physicalVolume.logicalVolume.type,
            ") cannot be converted - skipping: ",
            physicalVolume.name,
        )
        return

        # z = _fluka.Zone()
        # flukaMotherOuterRegion.addZone(z)

    flukaMotherRegion = _copy.deepcopy(flukaMotherOuterRegion)
    flukaMotherRegion.comment = physicalVolume.name

    # Check if we have a replica - a replica is a special case where we have an in-effect dummy mother
    # volume that the replica by-construction should entirely fill. Therefore, we cut out the pv shape
    # from the parent but we don't create it itself and just place the daughters from the replica in it.
    # A replica is detectable by there only being 1 daughter and it being a ReplicaVolume instance
    replicaCondition1 = len(physicalVolume.logicalVolume.daughterVolumes) == 1
    replicaCondition2 = False
    if replicaCondition1:  # can only do this if len > 0
        replicaCondition2 = (
            type(physicalVolume.logicalVolume.daughterVolumes[0]) is _geant4.ReplicaVolume
        )
    itsAReplica = replicaCondition1 and replicaCondition2
    if itsAReplica:
        replica = physicalVolume.logicalVolume.daughterVolumes[0]
        # this unintentionally adds the PVs to the mother LV
        daughterVolumes, transforms = replica.getPhysicalVolumes()
        for dv in daughterVolumes:
            pvmrot = _transformation.tbzyx2matrix(-_np.array(dv.rotation.eval()))
            pvtra = _np.array(dv.position.eval())
            reflection = _np.diag([1, 1, 1])
            if dv.scale:
                reflection = _np.diag([dv.scale.eval()[0], dv.scale.eval()[1], dv.scale.eval()[2]])
            new_mtra = mtra @ pvmrot @ reflection
            new_tra = mtra @ pvtra + tra
            flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(
                dv,
                new_mtra,
                new_tra,
                flukaRegistry=flukaRegistry,
                flukaNameCount=flukaNameCount,
                bakeTransforms=bakeTransforms,
            )

        materialName = daughterVolumes[0].logicalVolume.material.name
        materialNameShort = flukaRegistry.materialShortName[materialName]

        try:
            flukaMaterial = flukaRegistry.materials[materialNameShort]
            flukaRegistry.addMaterialAssignments(flukaMaterial, flukaMotherRegion)
        except KeyError:
            pass
    else:
        # loop over daughters and remove from mother region
        for dv in physicalVolume.logicalVolume.daughterVolumes:
            # placement information for daughter
            pvmrot = _transformation.tbzyx2matrix(-_np.array(dv.rotation.eval()))
            pvtra = _np.array(dv.position.eval())
            reflection = _np.diag([1, 1, 1])
            if dv.scale:
                reflection = _np.diag([dv.scale.eval()[0], dv.scale.eval()[1], dv.scale.eval()[2]])
            new_mtra = mtra @ pvmrot @ reflection
            new_tra = mtra @ pvtra + tra

            flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(
                dv,
                new_mtra,
                new_tra,
                flukaRegistry=flukaRegistry,
                flukaNameCount=flukaNameCount,
                bakeTransforms=bakeTransforms,
            )
            if physicalVolume.logicalVolume.type == "logical":
                for motherZones in flukaMotherRegion.zones:
                    for daughterZones in flukaDaughterOuterRegion.zones:
                        motherZones.addSubtraction(daughterZones)
            elif physicalVolume.logicalVolume.type == "assembly":
                # If assembly the daughters form the outer
                for daughterZones in flukaDaughterOuterRegion.zones:
                    flukaMotherOuterRegion.addZone(daughterZones)

        if (
            physicalVolume.logicalVolume.type == "logical"
            and physicalVolume.logicalVolume.solid.type != "extruder"
        ):
            flukaRegistry.addRegion(flukaMotherRegion)
            materialName = physicalVolume.logicalVolume.material.name
            materialNameShort = flukaRegistry.materialShortName[materialName]

            try:
                flukaMaterial = flukaRegistry.materials[materialNameShort]
                flukaRegistry.addMaterialAssignments(flukaMaterial, flukaMotherRegion)
            except KeyError:
                pass

    return flukaMotherOuterRegion, flukaNameCount


def geant4Solid2FlukaRegion(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransforms=False,
):
    from ..gdml import Units as _Units  # TODO move circular import

    name = format(flukaNameCount, "04")

    # add PV -> region map
    flukaRegistry.PhysVolToRegionMap[commentName] = "R" + name

    fregion = None
    fbodies = []

    pseudoVector = _np.linalg.det(mtra)
    rotation = _transformation.matrix2tbxyz(mtra)

    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)
    commentName = commentName + " " + solid.name

    # print 'geant4Solid2FlukaRegion',flukaNameCount,name,solid.type, rotation,position,transform

    if solid.type == "Box":
        fregion, flukaNameCount = geant4Box2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Tubs":
        fregion, flukaNameCount = geant4Tubs2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "CutTubs":
        fregion, flukaNameCount = geant4CutTubs2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Cons":
        fregion, flukaNameCount = geant4Cons2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Para":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, bakeTransforms
        )
        flukaNameCount += 1
    elif solid.type == "Trd":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, bakeTransforms
        )
        flukaNameCount += 1
    elif solid.type == "Trap":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, bakeTransforms
        )
        flukaNameCount += 1
    elif solid.type == "Sphere":
        fregion, flukaNameCount = geant4Sphere2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Orb":
        fregion, flukaNameCount = geant4Orb2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Torus":
        fregion, flukaNameCount = geant4Torus2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "GenericPolycone" or solid.type == "Polycone":
        fregion, flukaNameCount = geant4Polycone2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "GenericPolyhedra" or solid.type == "Polyhedra":
        fregion, flukaNameCount = geant4Polyhedra2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "EllipticalTube":
        fregion, flukaNameCount = geant4EllipticalTube2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Ellipsoid":
        fregion, flukaNameCount = geant4Ellipsoid2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "EllipticalCone":
        fregion, flukaNameCount = geant4EllipticalCone2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Paraboloid":
        fregion, flukaNameCount = geant4Paraboloid2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Hype":
        fregion, flukaNameCount = geant4Hype2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Tet":
        fregion, flukaNameCount = geant4Tet2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "ExtrudedSolid":
        fregion, flukaNameCount = geant4Extruded2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "TwistedBox":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, False
        )
        flukaNameCount += 1

    elif solid.type == "TwistedTrap":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, False
        )
        flukaNameCount += 1

    elif solid.type == "TwistedTrd":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, False
        )
        flukaNameCount += 1

    elif solid.type == "TwistedTubs":
        fregion = pycsgmesh2FlukaRegion(
            solid.mesh(), name, mtra, tra, flukaRegistry, commentName, False
        )
        flukaNameCount += 1

    elif solid.type == "GenericTrap":
        fregion, flukaNameCount = geant4GenericTrap2Fluka(
            flukaNameCount,
            solid,
            mtra,
            tra,
            flukaRegistry,
            addRegistry=True,
            commentName=commentName,
            bakeTransform=bakeTransforms,
        )
    elif solid.type == "Union":
        # build both solids to regions
        # take zones from 2 and add as zones to 1

        bsrot = solid.tra2[0].eval()
        bspos = solid.tra2[1].eval()

        bsmtra = _transformation.tbxyz2matrix(bsrot)
        bstra = bspos

        solid1 = solid.obj1
        solid2 = solid.obj2

        new_mtra = mtra @ bsmtra
        new_tra = mtra @ bstra + tra

        r1, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid1,
            mtra,
            tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )
        r2, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid2,
            new_mtra,
            new_tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )

        if 0:
            print("-------------------------")
            print("Union")
            print(solid.obj1.name, solid.obj2.name)
            print(solid.obj1.type, solid.obj2.type)
            print(type(r1), type(r2))
            print(r1.flukaFreeString())
            print(r2.flukaFreeString())

        fregion = _fluka.Region("R" + name)

        for zone in r1.zones:
            fregion.addZone(zone)

        for zone in r2.zones:
            fregion.addZone(zone)

    elif solid.type == "Subtraction":
        # build both solids to regions
        # take zones from 2 and distribute over zones of 1

        bsrot = solid.tra2[0].eval()
        bspos = solid.tra2[1].eval()

        bsmtra = _transformation.tbxyz2matrix(bsrot)
        bstra = bspos

        solid1 = solid.obj1
        solid2 = solid.obj2

        new_mtra = mtra @ bsmtra
        new_tra = mtra @ bstra + tra

        r1, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid1,
            mtra,
            tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )
        r2, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid2,
            new_mtra,
            new_tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )

        if 0:
            print("-------------------------")
            print("Subtraction")
            print(solid.obj1.name, solid.obj2.name)
            print(solid.obj1.type, solid.obj2.type)
            print(type(r1), type(r2))
            print(r1.flukaFreeString())
            print(r2.flukaFreeString())

        fregion = _fluka.Region("R" + name)

        for zone1 in r1.zones:
            for zone2 in r2.zones:
                zone1.addSubtraction(zone2)
            fregion.addZone(zone1)

    elif solid.type == "Intersection":
        # build both zones to regions
        # take zones from 2 and distribute over zones of 1

        # build both solids to regions
        # take zones from 2 and distribute over zones of 1

        bsrot = solid.tra2[0].eval()
        bspos = solid.tra2[1].eval()

        bsmtra = _transformation.tbxyz2matrix(bsrot)
        bstra = bspos

        solid1 = solid.obj1
        solid2 = solid.obj2

        new_mtra = mtra @ bsmtra
        new_tra = mtra @ bstra + tra

        r1, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid1,
            mtra,
            tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )
        r2, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid2,
            new_mtra,
            new_tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )

        if 0:
            print("-------------------------")
            print("Intersection")
            print(solid.obj1.name, solid.obj2.name)
            print(solid.obj1.type, solid.obj2.type)
            print(type(r1), type(r2))
            print(r1.flukaFreeString())
            print(r2.flukaFreeString())

        fregion = _fluka.Region("R" + name)

        for zone1 in r1.zones:
            for zone2 in r2.zones:
                zone1.addIntersection(zone2)
            fregion.addZone(zone1)

    elif solid.type == "MultiUnion":

        fregion = _fluka.Region("R" + name)

        r1, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid.objects[0],
            mtra,
            tra,
            flukaRegistry,
            bakeTransforms=bakeTransforms,
            commentName=commentName,
        )

        for zone in r1.zones:
            fregion.addZone(zone)

        for solid, trans in zip(solid.objects[1:], solid.transformations):

            bsrot = trans[0].eval()
            bspos = trans[1].eval()

            bsmtra = _transformation.tbxyz2matrix(bsrot)
            bstra = bspos

            new_mtra = mtra @ bsmtra
            new_tra = mtra @ bstra + tra

            r2, flukaNameCount = geant4Solid2FlukaRegion(
                flukaNameCount,
                solid,
                new_mtra,
                new_tra,
                flukaRegistry,
                bakeTransforms=bakeTransforms,
                commentName=commentName,
            )

            for zone in r2.zones:
                fregion.addZone(zone)

    elif solid.type == "extruder":
        fregion, flukaNameCount = geant4Solid2FlukaRegion(
            flukaNameCount,
            solid.g4_extrusions[solid.boundary],
            mtra=mtra,
            tra=tra,
            flukaRegistry=flukaRegistry,
            addRegistry=True,
            commentName=solid.name,
            bakeTransforms=bakeTransforms,
        )
        flukaNameCount += 1

        for sk in solid.g4_decomposed_extrusions:
            material = solid.getRegionMaterial(sk)
            for s in solid.g4_decomposed_extrusions[sk]:
                temp, flukaNameCount = geant4Solid2FlukaRegion(
                    flukaNameCount,
                    s,
                    mtra=mtra,
                    tra=tra,
                    flukaRegistry=flukaRegistry,
                    addRegistry=True,
                    commentName=solid.name + "_" + sk,
                    bakeTransforms=bakeTransforms,
                )
                # flukaNameCount += 1
                flukaRegistry.addRegion(temp)

                materialName = material.name
                materialNameShort = flukaRegistry.materialShortName[materialName]

                try:
                    flukaMaterial = flukaRegistry.materials[materialNameShort]
                    flukaRegistry.addMaterialAssignments(flukaMaterial, temp.name)
                except KeyError:
                    pass
    else:
        fregion = _fluka.Region("R" + name)
        print(solid.type)

    return fregion, flukaNameCount


def geant4MaterialDict2Fluka(matr, freg):
    for material in matr.items():
        if isinstance(material[1], _geant4.Material):
            materialNameShort = "M" + format(freg.iMaterials, "03")
            # print(material[1].name, materialNameShort)
            geant4Material2Fluka(material[1], freg, materialNameShort=materialNameShort)
            freg.materialShortName[material[1].name] = materialNameShort
            freg.iMaterials += 1

    return freg


def geant4Material2Fluka(
    material, freg, suggestedDensity=None, elementSuffix=False, materialNameShort=None
):
    materialName = material.name
    materialInstance = material

    # materialNameStrip = makeStripName(materialName)

    # ensure this name is unique
    # i = 0
    # while materialNameStrip in freg.materials:
    #    if i == 0:
    #        materialNameStrip += str(i)
    #    else:
    #        materialNameStrip[-1] = str(i)
    # materialNameShort = makeShortName(materialNameStrip)

    # protect against multiply defining the same material
    if materialName in freg.materialShortName:
        return freg.materials[freg.materialShortName[materialName]]

    # Only want to use materials (FLUKA COMPOUND or MATERIAL)
    if isinstance(materialInstance, _geant4.Material):
        # none, nist, arbitrary, simple, composite
        if materialInstance.type == "none":
            msg = "Cannot have material with none type"
            raise Exception(msg)

        elif materialInstance.type == "nist":
            # make material object from dictionary of information
            nistMatInstance = _geant4.nist_material_2geant4Material(materialInstance.name)
            nistMatInstance.type = "composite"  # prevent recursion - Material internally decides if it's a nist material or not
            return geant4Material2Fluka(nistMatInstance, freg, materialNameShort=materialNameShort)

        elif materialInstance.type == "arbitrary":
            msg = "Cannot have material with arbitrary type"
            raise Exception(msg)

        elif materialInstance.type == "simple":
            fe = _fluka.Material(
                materialNameShort,
                materialInstance.atomic_number,
                materialInstance.density,
                flukaregistry=freg,
                comment="material-simple: " + materialName,
            )
            return fe

        elif materialInstance.type == "composite":
            flukaComposition = []
            flukaFractionType = "atomic"

            iComp = 0
            for comp in materialInstance.components:
                fm = geant4Material2Fluka(
                    comp[0],
                    freg,
                    materialInstance.density,
                    elementSuffix=True,
                    materialNameShort=materialNameShort + format(iComp, "02"),
                )

                compFraction = float(comp[1])
                compFractionType = comp[2]

                if compFractionType == "natoms":
                    flukaFractionType = "atomic"
                elif compFractionType == "massfraction":
                    flukaFractionType = "mass"

                flukaComposition.append((fm, compFraction))
                iComp += 1

            mat = _fluka.Compound(
                materialNameShort,
                materialInstance.density,
                flukaComposition,
                fractionType=flukaFractionType,
                flukaregistry=freg,
                comment="material-composite: " + materialName,
            )
            return mat

    elif isinstance(materialInstance, _geant4.Element):
        # if elementSuffix:
        #    if len(materialNameShort) >= 6:
        #        materialNameShort = materialNameShort[:6] + "EL"
        #    else:
        #        materialNameShort += "EL"
        # check again as we've just changed our short name
        # if materialNameShort in freg.materials:
        #    return freg.materials[materialNameShort]

        if materialInstance.type == "element-simple":
            mat = _fluka.Material(
                materialNameShort,
                materialInstance.Z,
                suggestedDensity,
                materialInstance.A,
                flukaregistry=freg,
                comment="element-simple: " + materialName,
            )
            return mat

        elif materialInstance.type == "element-composite":
            flukaComponentNames = []
            flukaComponents = []
            flukaComponentFractions = []

            iComp = 0
            for iso in materialInstance.components:
                fi = geant4Material2Fluka(
                    iso[0],
                    freg,
                    materialNameShort=materialNameShort + format(iComp, "02"),
                )

                compFlukaName = makeShortName(iso[0].name)
                compFraction = iso[1]

                flukaComponentNames.append(compFlukaName)
                flukaComponents.append(fi)
                flukaComponentFractions.append(compFraction)
                iComp += 1

            flukaComposition = list(zip(flukaComponents, flukaComponentFractions))

            mat = _fluka.Compound(
                materialNameShort,
                0.123456789,
                flukaComposition,
                fractionType="atomic",
                flukaregistry=freg,
                comment="element-composite: " + materialName,
            )
            return mat

    elif isinstance(materialInstance, _geant4.Isotope):
        fi = _fluka.Material(
            materialNameShort,
            materialInstance.Z,
            10,  # this density won't be used finally but needs to be there
            flukaregistry=freg,
            atomicMass=materialInstance.a,
            massNumber=materialInstance.N,
            comment="isotope: " + materialName,
        )
        return fi
    else:
        raise TypeError('Unknown material.type "' + str(material.type) + '"')


def geant4Box2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    fregion = None
    fbodies = []

    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10.0
    pX = solid.evaluateParameter(solid.pX) * uval / 2.0
    pY = solid.evaluateParameter(solid.pY) * uval / 2.0
    pZ = solid.evaluateParameter(solid.pZ) * uval / 2.0

    fbody = None

    if not bakeTransform:
        fbody = _fluka.RPP(
            "B" + name + "01",
            -pX,
            pX,
            -pY,
            pY,
            -pZ,
            pZ,
            transform=transform,
            flukaregistry=flukaRegistry,
            addRegistry=True,
            comment=commentName,
        )
    else:
        # build a BOX without a rot-defi
        v = mtra @ _np.array([-pX, -pY, -pZ]) + tra / 10
        h1 = mtra @ _np.array([2 * pX, 0, 0])
        h2 = mtra @ _np.array([0, 2 * pY, 0])
        h3 = mtra @ _np.array([0, 0, 2 * pZ])

        fbody = _fluka.BOX(
            "B" + name + "01",
            v,
            h1,
            h2,
            h3,
            transform=None,
            flukaregistry=flukaRegistry,
            addRegistry=True,
            comment=commentName,
        )

    # store all bodies
    fbodies.append(fbody)

    # create zones
    fzone = _fluka.Zone()
    fzone.addIntersection(fbody)

    # create region
    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Tubs2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    fregion = None
    fbodies = []

    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10.0
    aval = _Units.unit(solid.aunit)

    pRMin = solid.evaluateParameter(solid.pRMin) * uval
    pSPhi = solid.evaluateParameter(solid.pSPhi) * aval
    pDPhi = solid.evaluateParameter(solid.pDPhi) * aval
    pDz = solid.evaluateParameter(solid.pDz) * uval
    pRMax = solid.evaluateParameter(solid.pRMax) * uval

    if pRMin == 0 and pSPhi == 0 and pDPhi == 2 * _np.pi:
        if not bakeTransform:
            fzone = _fluka.Zone()

            fbody1 = flukaRegistry.makeBody(
                RCC,
                "B" + name + "01",
                [0, 0, -pDz / 2],
                [0, 0, pDz],
                pRMax,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
            fzone.addIntersection(fbody1)
        else:
            fzone = _fluka.Zone()

            v = mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10
            h = mtra @ _np.array([0, 0, pDz])

            fbody1 = flukaRegistry.makeBody(
                RCC,
                "B" + name + "01",
                v,
                h,
                pRMax,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
            fzone.addIntersection(fbody1)
    else:
        if not bakeTransform:
            fzone = _fluka.Zone()

            # main cylinder
            fbody1 = flukaRegistry.makeBody(
                ZCC,
                "B" + name + "01",
                0,
                0,
                pRMax,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            # low z cut
            fbody2 = flukaRegistry.makeBody(
                XYP,
                "B" + name + "02",
                -pDz / 2,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            # high z cut
            fbody3 = flukaRegistry.makeBody(
                XYP,
                "B" + name + "03",
                pDz / 2,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            # inner cylinder
            if pRMin != 0:
                fbody4 = flukaRegistry.makeBody(
                    ZCC,
                    "B" + name + "04",
                    0,
                    0,
                    pRMin,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            # phi cuts
            if pDPhi != 2 * _np.pi:
                fbody5 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "05",
                    [-_np.sin(pSPhi), _np.cos(pSPhi), 0],
                    [0, 0, 0],
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

                fbody6 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "06",
                    [-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0],
                    [0, 0, 0],
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            fzone = _fluka.Zone()
            fzone.addIntersection(fbody1)
            fzone.addSubtraction(fbody2)
            fzone.addIntersection(fbody3)

            if pRMin != 0:
                fzone.addSubtraction(fbody4)

            if pDPhi != 2 * _np.pi:
                if pDPhi < _np.pi:
                    fzone.addSubtraction(fbody5)
                    fzone.addIntersection(fbody6)
                elif pDPhi == _np.pi:
                    fzone.addSubtraction(fbody5)
                else:
                    fzone1 = _fluka.Zone()
                    fzone1.addIntersection(fbody5)
                    fzone1.addSubtraction(fbody6)
                    fzone.addSubtraction(fzone1)
        else:
            fzone = _fluka.Zone()

            v = mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10
            h = mtra @ _np.array([0, 0, pDz])

            # main cylinder
            fbody1 = flukaRegistry.makeBody(
                RCC,
                "B" + name + "01",
                v,
                h,
                pRMax,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            # inner cylinder
            if pRMin != 0:
                fbody4 = flukaRegistry.makeBody(
                    RCC,
                    "B" + name + "04",
                    v,
                    h,
                    pRMin,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            # phi cuts
            if pDPhi != 2 * _np.pi:
                fbody5 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "05",
                    mtra @ _np.array([-_np.sin(pSPhi), _np.cos(pSPhi), 0]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

                fbody6 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "06",
                    mtra @ _np.array([-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            fzone = _fluka.Zone()
            fzone.addIntersection(fbody1)

            if pRMin != 0:
                fzone.addSubtraction(fbody4)

            if pDPhi != 2 * _np.pi:
                if pDPhi < _np.pi:
                    fzone.addSubtraction(fbody5)
                    fzone.addIntersection(fbody6)
                elif pDPhi == _np.pi:
                    fzone.addSubtraction(fbody5)
                else:
                    fzone1 = _fluka.Zone()
                    fzone1.addIntersection(fbody5)
                    fzone1.addSubtraction(fbody6)
                    fzone.addSubtraction(fzone1)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4CutTubs2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    fregion = None
    fbodies = []

    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10
    aval = _Units.unit(solid.aunit)

    pRMin = solid.evaluateParameter(solid.pRMin) * uval
    pSPhi = solid.evaluateParameter(solid.pSPhi) * aval
    pDPhi = solid.evaluateParameter(solid.pDPhi) * aval
    pDz = solid.evaluateParameter(solid.pDz) * uval
    pRMax = solid.evaluateParameter(solid.pRMax) * uval
    pLowNorm0 = solid.evaluateParameter(solid.pLowNorm[0])
    pLowNorm1 = solid.evaluateParameter(solid.pLowNorm[1])
    pLowNorm2 = solid.evaluateParameter(solid.pLowNorm[2])
    pHighNorm0 = solid.evaluateParameter(solid.pHighNorm[0])
    pHighNorm1 = solid.evaluateParameter(solid.pHighNorm[1])
    pHighNorm2 = solid.evaluateParameter(solid.pHighNorm[2])

    if not bakeTransform:
        # main cylinder
        fbody1 = flukaRegistry.makeBody(
            ZCC,
            "B" + name + "01",
            0,
            0,
            pRMax,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        # low z cut
        fbody2 = flukaRegistry.makeBody(
            PLA,
            "B" + name + "02",
            [-pLowNorm0, -pLowNorm1, -pLowNorm2],
            [0, 0, -pDz / 2],
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        # high z cut
        fbody3 = flukaRegistry.makeBody(
            PLA,
            "B" + name + "03",
            [pHighNorm0, pHighNorm1, pHighNorm2],
            [0, 0, pDz / 2.0],
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        if pRMin != 0:
            # inner cylinder
            fbody4 = flukaRegistry.makeBody(
                ZCC,
                "B" + name + "04",
                0,
                0,
                pRMin,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

        # phi cuts
        if pDPhi != 2 * _np.pi:
            fbody5 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "05",
                [-_np.sin(pSPhi), _np.cos(pSPhi), 0],
                [0, 0, 0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            fbody6 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "06",
                [-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0],
                [0, 0, 0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
    else:
        v = mtra @ _np.array([0, 0, -10 * pDz / 2]) + tra / 10
        h = mtra @ _np.array([0, 0, 10 * pDz])
        # main cylinder
        fbody1 = flukaRegistry.makeBody(
            RCC,
            "B" + name + "01",
            v,
            h,
            pRMax,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        # low z cut
        fbody2 = flukaRegistry.makeBody(
            PLA,
            "B" + name + "02",
            mtra @ _np.array([-pLowNorm0, -pLowNorm1, -pLowNorm2]),
            mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        # high z cut
        fbody3 = flukaRegistry.makeBody(
            PLA,
            "B" + name + "03",
            mtra @ _np.array([pHighNorm0, pHighNorm1, pHighNorm2]),
            mtra @ _np.array([0, 0, pDz / 2.0]) + tra / 10,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        if pRMin != 0:
            # inner cylinder
            fbody4 = flukaRegistry.makeBody(
                RCC,
                "B" + name + "04",
                v,
                h,
                pRMin,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

        # phi cuts
        if pDPhi != 2 * _np.pi:
            fbody5 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "05",
                mtra @ _np.array([-_np.sin(pSPhi), _np.cos(pSPhi), 0]),
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            fbody6 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "06",
                mtra @ _np.array([-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0]),
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)
    fzone.addSubtraction(fbody2)
    fzone.addIntersection(fbody3)

    if pRMin != 0:
        fzone.addSubtraction(fbody4)

    if pDPhi != 2 * _np.pi:
        if pDPhi < _np.pi:
            fzone.addSubtraction(fbody5)
            fzone.addIntersection(fbody6)
        elif pDPhi == _np.pi:
            fzone.addSubtraction(fbody5)
        else:
            fzone1 = _fluka.Zone()
            fzone1.addIntersection(fbody5)
            fzone1.addSubtraction(fbody6)
            fzone.addSubtraction(fzone1)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Cons2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    fregion = None
    fbodies = []

    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit) / 10.0
    auval = _Units.unit(solid.aunit)

    pRmin1 = solid.evaluateParameter(solid.pRmin1) * luval
    pRmax1 = solid.evaluateParameter(solid.pRmax1) * luval
    pRmin2 = solid.evaluateParameter(solid.pRmin2) * luval
    pRmax2 = solid.evaluateParameter(solid.pRmax2) * luval
    pDz = solid.evaluateParameter(solid.pDz) * luval
    pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
    pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

    if not bakeTransform:
        if pRmin1 == 0 and pRmin2 == 0 and pSPhi == 0 and pDPhi == 2 * _np.pi:
            fzone = _fluka.Zone()

            fbody1 = flukaRegistry.makeBody(
                TRC,
                name="B" + name + "01",
                major_centre=[0, 0, -pDz / 2],
                direction=[0, 0, pDz],
                major_radius=pRmax1,
                minor_radius=pRmax2,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
            fzone.addIntersection(fbody1)
        else:
            fbody1 = _fluka.TRC(
                "B" + name + "01",
                major_centre=[0, 0, -pDz / 2],
                direction=[0, 0, pDz],
                major_radius=pRmax1,
                minor_radius=pRmax2,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            if pRmin1 != 0 and pRmin2 != 0:
                fbody2 = _fluka.TRC(
                    "B" + name + "02",
                    major_centre=[0, 0, -pDz / 2],
                    direction=[0, 0, pDz],
                    major_radius=pRmin1,
                    minor_radius=pRmin2,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                )

            # phi cuts
            if pDPhi != 2 * _np.pi:
                fbody3 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "03",
                    [-_np.sin(pSPhi), _np.cos(pSPhi), 0],
                    [0, 0, 0],
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

                fbody4 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "04",
                    [-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0],
                    [0, 0, 0],
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            fzone = _fluka.Zone()
            fzone.addIntersection(fbody1)

            if pRmin1 != 0 and pRmin2 != 0:
                fzone.addSubtraction(fbody2)

            if pDPhi != 2 * _np.pi:
                if pDPhi < _np.pi:
                    fzone.addSubtraction(fbody3)
                    fzone.addIntersection(fbody4)
                elif pDPhi == _np.pi:
                    fzone.addSubtraction(fbody3)
                else:
                    fzone1 = _fluka.Zone()
                    fzone1.addIntersection(fbody3)
                    fzone1.addSubtraction(fbody4)
                    fzone.addSubtraction(fzone1)
    else:
        if pRmin1 == 0 and pRmin2 == 0 and pSPhi == 0 and pDPhi == 2 * _np.pi:
            fzone = _fluka.Zone()

            fbody1 = flukaRegistry.makeBody(
                TRC,
                name="B" + name + "01",
                major_centre=mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10,
                direction=mtra @ _np.array([0, 0, pDz]),
                major_radius=pRmax1,
                minor_radius=pRmax2,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
            fzone.addIntersection(fbody1)
        else:
            fbody1 = _fluka.TRC(
                "B" + name + "01",
                major_centre=mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10,
                direction=mtra @ _np.array([0, 0, pDz]),
                major_radius=pRmax1,
                minor_radius=pRmax2,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            if pRmin1 != 0 and pRmin2 != 0:
                fbody2 = _fluka.TRC(
                    "B" + name + "02",
                    major_centre=mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10,
                    direction=mtra @ _np.array([0, 0, pDz]),
                    major_radius=pRmin1,
                    minor_radius=pRmin2,
                    transform=None,
                    flukaregistry=flukaRegistry,
                )

            # phi cuts
            if pDPhi != 2 * _np.pi:
                fbody3 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "03",
                    mtra @ _np.array([-_np.sin(pSPhi), _np.cos(pSPhi), 0]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

                fbody4 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "04",
                    mtra @ _np.array([-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            fzone = _fluka.Zone()
            fzone.addIntersection(fbody1)

            if pRmin1 != 0 and pRmin2 != 0:
                fzone.addSubtraction(fbody2)

            if pDPhi != 2 * _np.pi:
                if pDPhi < _np.pi:
                    fzone.addSubtraction(fbody3)
                    fzone.addIntersection(fbody4)
                elif pDPhi == _np.pi:
                    fzone.addSubtraction(fbody3)
                else:
                    fzone1 = _fluka.Zone()
                    fzone1.addIntersection(fbody3)
                    fzone1.addSubtraction(fbody4)
                    fzone.addSubtraction(fzone1)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def pycsgmesh2FlukaRegion(
    mesh,
    name,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    commentName="",
    bakeTransform=False,
):
    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    polyhedron = _pycgal.Polyhedron_3.Polyhedron_3_EPECK()
    _pycgal.CGAL.copy_face_graph(mesh.sm, polyhedron)
    nef = _pycgal.Nef_polyhedron_3.Nef_polyhedron_3_EPECK(polyhedron)
    convex_polyhedra = _pycgal.PolyhedronProcessing.nefPolyhedron_to_convexPolyhedra(nef)

    fregion = _fluka.Region("R" + name)

    ibody = 0

    if not bakeTransform:
        for convex_polyhedron in convex_polyhedra:
            planes = _pycgal.PolyhedronProcessing.polyhedron_to_numpyArrayPlanes(convex_polyhedron)

            fzone = _fluka.Zone()

            for plane in planes:
                fbody = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + format(ibody, "02"),
                    -plane[3:] / _np.sqrt((plane[3:] ** 2).sum()),
                    plane[0:3] / 10.0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
                fzone.addSubtraction(fbody)
                ibody += 1

            fregion.addZone(fzone)
    else:
        for convex_polyhedron in convex_polyhedra:
            planes = _pycgal.PolyhedronProcessing.polyhedron_to_numpyArrayPlanes(convex_polyhedron)

            fzone = _fluka.Zone()

            for plane in planes:
                fbody = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + format(ibody, "02"),
                    mtra @ -plane[3:] / _np.sqrt((plane[3:] ** 2).sum()),
                    mtra @ plane[0:3] / 10 + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
                fzone.addSubtraction(fbody)
                ibody += 1

            fregion.addZone(fzone)
    return fregion


def geant4Sphere2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit) / 10.0
    auval = _Units.unit(solid.aunit)

    pRmin = solid.evaluateParameter(solid.pRmin) * luval
    pRmax = solid.evaluateParameter(solid.pRmax) * luval
    pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
    pDPhi = solid.evaluateParameter(solid.pDPhi) * auval
    pSTheta = solid.evaluateParameter(solid.pSTheta) * auval
    pDTheta = solid.evaluateParameter(solid.pDTheta) * auval

    if not bakeTransform:
        fbody1 = _fluka.SPH(
            "B" + name + "01",
            [0, 0, 0],
            pRmax,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        if pRmin != 0:
            fbody2 = _fluka.SPH(
                "B" + name + "02",
                [0, 0, 0],
                pRmin,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

        # phi cuts
        if pDPhi != 2 * _np.pi:
            fbody3 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "03",
                [-_np.sin(pSPhi), _np.cos(pSPhi), 0],
                [0, 0, 0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            fbody4 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "04",
                [-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0],
                [0, 0, 0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        pTheta1 = pSTheta
        pTheta2 = pSTheta + pDTheta

        if pTheta1 != 0:
            if pTheta1 < _np.pi / 2.0:
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC(
                    "B" + name + "05",
                    [0, 0, pRmax],
                    [0, 0, -pRmax],
                    r,
                    0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            elif pTheta1 > _np.pi / 2.0:
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC(
                    "B" + name + "05",
                    [0, 0, -pRmax],
                    [0, 0, pRmax],
                    r,
                    0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            else:
                fbody5 = flukaRegistry.makeBody(
                    XYP,
                    "B" + name + "05",
                    0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

        if pTheta2 != _np.pi:
            if pTheta2 < _np.pi / 2.0:
                r = abs(_np.tan(pTheta2) * pRmax)

                fbody6 = _fluka.TRC(
                    "B" + name + "06",
                    [0, 0, pRmax],
                    [0, 0, -pRmax],
                    r,
                    0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            elif pTheta2 > _np.pi / 2.0:
                r = abs(_np.tan(pTheta2) * pRmax)
                fbody6 = _fluka.TRC(
                    "B" + name + "06",
                    [0, 0, -pRmax],
                    [0, 0, pRmax],
                    r,
                    0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            else:
                fbody6 = flukaRegistry.makeBody(
                    XYP,
                    "B" + name + "06",
                    0,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
    else:
        fbody1 = _fluka.SPH(
            "B" + name + "01",
            mtra @ _np.array([0, 0, 0]) + tra / 10,
            pRmax,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

        if pRmin != 0:
            fbody2 = _fluka.SPH(
                "B" + name + "02",
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                pRmin,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

        # phi cuts
        if pDPhi != 2 * _np.pi:
            fbody3 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "03",
                mtra @ _np.array([-_np.sin(pSPhi), _np.cos(pSPhi), 0]),
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            fbody4 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "04",
                mtra @ _np.array([-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0]),
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        pTheta1 = pSTheta
        pTheta2 = pSTheta + pDTheta

        if pTheta1 != 0:
            if pTheta1 < _np.pi / 2.0:
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC(
                    "B" + name + "05",
                    mtra @ _np.array([0, 0, pRmax]) + tra / 10,
                    mtra @ _np.array([0, 0, -pRmax]) + tra / 10,
                    r,
                    0,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            elif pTheta1 > _np.pi / 2.0:
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC(
                    "B" + name + "05",
                    mtra @ _np.array([0, 0, -pRmax]) + tra / 10,
                    mtra @ _np.array([0, 0, pRmax]) + tra / 10,
                    r,
                    0,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            else:
                fbody5 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "05",
                    mtra @ _np.array([0, 0, 1]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

        if pTheta2 != _np.pi:
            if pTheta2 < _np.pi / 2.0:
                r = abs(_np.tan(pTheta2) * pRmax)

                fbody6 = _fluka.TRC(
                    "B" + name + "06",
                    mtra @ _np.array([0, 0, pRmax]) + tra / 10,
                    mtra @ _np.array([0, 0, -pRmax]) + tra / 10,
                    r,
                    0,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

            elif pTheta2 > _np.pi / 2.0:
                r = abs(_np.tan(pTheta2) * pRmax)
                fbody6 = _fluka.TRC(
                    "B" + name + "06",
                    mtra @ _np.array([0, 0, -pRmax]) + tra / 10,
                    mtra @ _np.array([0, 0, pRmax]) + tra / 10,
                    r,
                    0,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            else:
                fbody6 = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + "06",
                    mtra @ _np.array([0, 0, 1]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)

    if pRmin != 0:
        fzone.addSubtraction(fbody2)

    if pDPhi != 2 * _np.pi:
        if pDPhi < _np.pi:
            fzone.addSubtraction(fbody3)
            fzone.addIntersection(fbody4)
        elif pDPhi == _np.pi:
            fzone.addSubtraction(fbody3)
        else:
            fzone1 = _fluka.Zone()
            fzone1.addIntersection(fbody3)
            fzone1.addSubtraction(fbody4)
            fzone.addSubtraction(fzone1)

    if pTheta1 != 0:
        if pTheta1 < _np.pi / 2.0:
            fzone.addSubtraction(fbody5)
        elif pTheta1 > _np.pi / 2.0:
            fzone.addIntersection(fbody5)
        else:
            fzone.addIntersection(fbody5)

    if pTheta2 != _np.pi:
        if pTheta2 > _np.pi / 2.0:
            fzone.addSubtraction(fbody6)
        elif pTheta2 < _np.pi / 2.0:
            fzone.addIntersection(fbody6)
        else:
            fzone.addIntersection(fbody6)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Orb2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit)

    pRmax = solid.evaluateParameter(solid.pRMax) * luval / 10.0

    if not bakeTransform:
        fbody1 = _fluka.SPH(
            "B" + name + "01",
            [0, 0, 0],
            pRmax,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody1 = _fluka.SPH(
            "B" + name + "01",
            mtra @ _np.array([0, 0, 0]) + tra / 10,
            pRmax,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Torus2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit)
    auval = _Units.unit(solid.aunit)

    pRmin = solid.evaluateParameter(solid.pRmin) * luval / 10.0
    pRmax = solid.evaluateParameter(solid.pRmax) * luval / 10.0
    pRtor = solid.evaluateParameter(solid.pRtor) * luval / 10.0
    pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
    pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

    dPhi = pDPhi / solid.nstack

    # create region
    fregion = _fluka.Region("R" + name)

    d = pDPhi * pRtor / solid.nstack / 2 * 1.35

    luval = _Units.unit(solid.lunit)
    auval = _Units.unit(solid.aunit)

    pRmin = solid.evaluateParameter(solid.pRmin) * luval / 10.0
    pRmax = solid.evaluateParameter(solid.pRmax) * luval / 10.0
    pRtor = solid.evaluateParameter(solid.pRtor) * luval / 10.0
    pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
    pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

    dPhi = pDPhi / solid.nstack

    # create region
    fregion = _fluka.Region("R" + name)

    d = pDPhi * pRtor / solid.nstack / 2 * 1.35

    for i in range(0, solid.nstack, 1):
        x0 = pRtor * _np.cos(i * dPhi + pSPhi)
        y0 = pRtor * _np.sin(i * dPhi + pSPhi)
        z0 = 0

        nx0 = d * _np.cos(i * dPhi + pSPhi + _np.pi / 2.0)
        ny0 = d * _np.sin(i * dPhi + pSPhi + _np.pi / 2.0)
        nz0 = 0

        # _np.cos(dPhi/2) factor is due chord vs point on perimeter
        x1 = pRtor * _np.cos(dPhi / 2) * _np.cos((i + 0.5) * dPhi + pSPhi)
        y1 = pRtor * _np.cos(dPhi / 2) * _np.sin((i + 0.5) * dPhi + pSPhi)
        z1 = 0

        nx1 = d * _np.cos((i + 0.5) * dPhi + pSPhi + _np.pi / 2.0)
        ny1 = d * _np.sin((i + 0.5) * dPhi + pSPhi + _np.pi / 2.0)
        nz1 = 0

        x1 = x1 - nx1
        y1 = y1 - ny1

        x2 = pRtor * _np.cos((i + 1) * dPhi + pSPhi)
        y2 = pRtor * _np.sin((i + 1) * dPhi + pSPhi)
        z2 = 0

        nx2 = d * _np.cos((i + 1) * dPhi + pSPhi + _np.pi / 2.0)
        ny2 = d * _np.sin((i + 1) * dPhi + pSPhi + _np.pi / 2.0)
        nz2 = 0

        if not bakeTransform:
            body1 = _fluka.RCC(
                "B" + name + "" + format(4 * i, "02"),
                [x1, y1, z1],
                [2 * nx1, 2 * ny1, 2 * nz1],
                pRmax,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
            body2 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "" + format(4 * i + 1, "02"),
                [nx0, ny0, nz0],
                [x0, y0, z0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            body3 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "" + format(4 * i + 2, "02"),
                [nx2, ny2, nz2],
                [x2, y2, z2],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            if pRmin != 0:
                body4 = _fluka.RCC(
                    "B" + name + format(4 * i + 3, "02"),
                    [x1, y1, z1],
                    [2 * nx1, 2 * ny1, 2 * nz1],
                    pRmin,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
        else:
            body1 = _fluka.RCC(
                "B" + name + "" + format(4 * i, "02"),
                mtra @ _np.array([x1, y1, z1]) + tra / 10,
                mtra @ [2 * nx1, 2 * ny1, 2 * nz1],
                pRmax,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
            body2 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "" + format(4 * i + 1, "02"),
                mtra @ _np.array([nx0, ny0, nz0]),
                mtra @ _np.array([x0, y0, z0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            body3 = flukaRegistry.makeBody(
                PLA,
                "B" + name + "" + format(4 * i + 2, "02"),
                mtra @ _np.array([nx2, ny2, nz2]),
                mtra @ _np.array([x2, y2, z2]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )

            if pRmin != 0:
                body4 = _fluka.RCC(
                    "B" + name + format(4 * i + 3, "02"),
                    mtra @ _np.array([x1, y1, z1]) + tra / 10,
                    mtra @ _np.array([2 * nx1, 2 * ny1, 2 * nz1]),
                    pRmin,
                    transform=None,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )

        fzone = _fluka.Zone()
        fzone.addIntersection(body1)
        fzone.addSubtraction(body2)
        fzone.addIntersection(body3)
        if pRmin != 0:
            fzone.addSubtraction(body4)

        fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Polycone2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit) / 10
    auval = _Units.unit(solid.aunit)

    if solid.type == "GenericPolycone":
        pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
        pDPhi = solid.evaluateParameter(solid.pDPhi) * auval
        pR = [val * luval for val in solid.evaluateParameter(solid.pR)]
        pZ = [val * luval for val in solid.evaluateParameter(solid.pZ)]

    elif solid.type == "Polycone":
        pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
        pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

        pZpl = [val * luval for val in solid.evaluateParameter(solid.pZpl)]
        pRMin = [val * luval for val in solid.evaluateParameter(solid.pRMin)]
        pRMax = [val * luval for val in solid.evaluateParameter(solid.pRMax)]

        pZ = []
        pR = []

        # first point or rInner
        pZ.append(pZpl[0])
        pR.append(pRMin[0])

        # rest of outer
        pZ.extend(pZpl)
        pR.extend(pRMax)

        # reversed inner
        pZ.extend(pZpl[-1:0:-1])
        pR.extend(pRMin[-1:0:-1])

    zrList = [[z, r] for z, r in zip(pZ, pR)]
    zrList.reverse()
    zrArray = _np.array(zrList)

    zrListConvex = _PolygonProcessing.decomposePolygon2d(zrArray)

    # _plt.figure()
    # _plt.plot(pZ,pR,"*-")

    # loop over zr convex polygons
    ibody = 0

    fregion = _fluka.Region("R" + name)

    # phi cuts
    if pDPhi != 2 * _np.pi:
        if not bakeTransform:
            fbody1 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                [-_np.sin(pSPhi), _np.cos(pSPhi), 0],
                [0, 0, 0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        else:
            fbody1 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                mtra @ _np.array([-_np.sin(pSPhi), _np.cos(pSPhi), 0]),
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        ibody += 1
        if not bakeTransform:
            fbody2 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                [-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0],
                [0, 0, 0],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        else:
            fbody2 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                mtra @ _np.array([-_np.sin(pSPhi + pDPhi), _np.cos(pSPhi + pDPhi), 0]),
                mtra @ _np.array([0, 0, 0]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        ibody += 1

    for i in range(0, len(zrListConvex), 1):
        # zConv = [zr[0] for zr in zrListConvex[i]]
        # rConv = [zr[1] for zr in zrListConvex[i]]
        # _plt.plot(zConv,rConv)

        posBodies = []
        negBodies = []

        for j in range(0, len(zrListConvex[i]), 1):
            j1 = j
            j2 = (j + 1) % len(zrListConvex[i])

            z1 = zrListConvex[i][j1][0]
            r1 = zrListConvex[i][j1][1]

            z2 = zrListConvex[i][j2][0]
            r2 = zrListConvex[i][j2][1]

            dz = z2 - z1
            dr = r2 - r1

            if dz == 0:
                pass

            elif dz > 0 and r1 != 0 and r2 != 0:
                if not bakeTransform:
                    body = _fluka.TRC(
                        "B" + name + format(ibody, "02"),
                        [0, 0, z1],
                        [0, 0, dz],
                        r1,
                        r2,
                        transform=transform,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                else:
                    body = _fluka.TRC(
                        "B" + name + format(ibody, "02"),
                        mtra @ _np.array([0, 0, z1]) + tra / 10,
                        mtra @ _np.array([0, 0, dz]),
                        r1,
                        r2,
                        transform=None,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                negBodies.append(body)
                ibody += 1

            elif dz < 0 and r1 != 0 and r2 != 0:
                if not bakeTransform:
                    body = _fluka.TRC(
                        "B" + name + format(ibody, "02"),
                        [0, 0, z1],
                        [0, 0, dz],
                        r1,
                        r2,
                        transform=transform,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                else:
                    body = _fluka.TRC(
                        "B" + name + format(ibody, "02"),
                        mtra @ _np.array([0, 0, z1]) + tra / 10,
                        mtra @ _np.array([0, 0, dz]),
                        r1,
                        r2,
                        transform=None,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                posBodies.append(body)
                ibody += 1

        for pb in posBodies:
            fzone = _fluka.Zone()
            fzone.addIntersection(pb)

            for nb in negBodies:
                fzone.addSubtraction(nb)

            if pDPhi != 2 * _np.pi:
                if pDPhi < _np.pi:
                    fzone.addSubtraction(fbody1)
                    fzone.addIntersection(fbody2)
                elif pDPhi == _np.pi:
                    fzone.addSubtraction(fbody2)
                else:
                    fzone1 = _fluka.Zone()
                    fzone1.addIntersection(fbody1)
                    fzone1.addSubtraction(fbody2)
                    fzone.addSubtraction(fzone1)

            fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Extruded2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit) / 10

    pZslices = solid.evaluateParameter(solid.pZslices)
    pPolygon = solid.evaluateParameter(solid.pPolygon)

    zpos = [zslice[0] * luval for zslice in pZslices]
    x_offs = [zslice[1][0] * luval for zslice in pZslices]
    y_offs = [zslice[1][1] * luval for zslice in pZslices]
    scale = [zslice[2] for zslice in pZslices]
    vertices = [[pPolygon[0] * luval, pPolygon[1] * luval] for pPolygon in pPolygon]
    nslices = len(pZslices)

    vertices = list(reversed(vertices))
    polyListConvex = _PolygonProcessing.decomposePolygon2d(vertices)

    fregion = _fluka.Region("R" + name)

    ibody = 0
    # loop over planes
    for i in range(0, nslices - 1, 1):
        i1 = i
        i2 = i + 1

        zi1 = zpos[i1]
        zi2 = zpos[i2]

        # build i'th and i+1'th layers
        i1PolyListConvex = []
        i2PolyListConvex = []

        for j in range(0, len(polyListConvex), 1):
            i1PolyListConvex.append(
                [
                    [
                        scale[i1] * vert[0] + x_offs[i1],
                        scale[i1] * vert[1] + y_offs[i1],
                    ]
                    for vert in polyListConvex[j]
                ]
            )

            i2PolyListConvex.append(
                [
                    [
                        scale[i2] * vert[0] + x_offs[i2],
                        scale[i2] * vert[1] + y_offs[i2],
                    ]
                    for vert in polyListConvex[j]
                ]
            )

        # end planes
        if not bakeTransform:
            fbody1 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                [0, 0, -1],
                [0, 0, zi1],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        else:
            fbody1 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                mtra @ _np.array([0, 0, -1]),
                mtra @ _np.array([0, 0, zi1]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        ibody += 1

        if not bakeTransform:
            fbody2 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                [0, 0, 1],
                [0, 0, zi2],
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        else:
            fbody2 = flukaRegistry.makeBody(
                PLA,
                "B" + name + format(ibody, "02"),
                mtra @ _np.array([0, 0, 1]),
                mtra @ _np.array([0, 0, zi2]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        ibody += 1

        for j in range(0, len(i1PolyListConvex), 1):
            fzone = _fluka.Zone()

            fzone.addIntersection(fbody1)
            fzone.addIntersection(fbody2)

            for k in range(0, len(i1PolyListConvex[j]), 1):
                k1 = k
                k2 = (k + 1) % len(i1PolyListConvex[j])

                x0 = i1PolyListConvex[j][k1][0]
                y0 = i1PolyListConvex[j][k1][1]
                z0 = zi1

                x1 = i2PolyListConvex[j][k1][0]
                y1 = i2PolyListConvex[j][k1][1]
                z1 = zi2

                x2 = i1PolyListConvex[j][k2][0]
                y2 = i1PolyListConvex[j][k2][1]
                z2 = zi1

                dx1 = x1 - x0
                dy1 = y1 - y0
                dz1 = z1 - z0

                ld1 = _np.sqrt(dx1**2 + dy1**2 + dz1**2)

                dx1 = dx1 / ld1
                dy1 = dy1 / ld1
                dz1 = dz1 / ld1

                dx2 = x2 - x0
                dy2 = y2 - y0
                dz2 = z2 - z0

                ld2 = _np.sqrt(dx2**2 + dy2**2 + dz2**2)

                dx2 = dx2 / ld2
                dy2 = dy2 / ld2
                dz2 = dz2 / ld2

                nx = dy1 * dz2 - dz1 * dy2
                ny = dx2 * dz1 - dx1 * dz2
                nz = dx1 * dy2 - dy1 * dx2

                if not bakeTransform:
                    fbody = flukaRegistry.makeBody(
                        PLA,
                        "B" + name + format(ibody, "02"),
                        [
                            -nx,
                            -ny,
                            -nz,
                        ],
                        [
                            x0,
                            y0,
                            z0,
                        ],
                        transform=transform,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                else:
                    fbody = flukaRegistry.makeBody(
                        PLA,
                        "B" + name + format(ibody, "02"),
                        mtra
                        @ _np.array(
                            [
                                -nx,
                                -ny,
                                -nz,
                            ]
                        ),
                        mtra
                        @ _np.array(
                            [
                                x0,
                                y0,
                                z0,
                            ]
                        )
                        + tra / 10,
                        transform=None,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                ibody += 1
                fzone.addIntersection(fbody)
            fregion.addZone(fzone)

    # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Polyhedra2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    luval = _Units.unit(solid.lunit) / 10
    auval = _Units.unit(solid.aunit)

    if solid.type == "GenericPolyhedra":
        pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
        pDPhi = solid.evaluateParameter(solid.pDPhi) * auval
        numSide = int(solid.evaluateParameter(solid.numSide))
        pR = [val * luval / 10.0 for val in solid.evaluateParameter(solid.pR)]
        pZ = [val * luval / 10.0 for val in solid.evaluateParameter(solid.pZ)]
    elif solid.type == "Polyhedra":
        pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
        pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

        numSide = int(solid.evaluateParameter(solid.numSide))
        numZPlanes = int(solid.numZPlanes)
        zPlane = [val * luval for val in solid.evaluateParameter(solid.zPlane)]
        rInner = [val * luval for val in solid.evaluateParameter(solid.rInner)]
        rOuter = [val * luval for val in solid.evaluateParameter(solid.rOuter)]

        pZ = []
        pR = []

        # first point or rInner
        pZ.append(zPlane[0])
        pR.append(rInner[0])

        # rest of outer
        pZ.extend(zPlane)
        pR.extend(rOuter)

        # reversed inner
        pZ.extend(zPlane[-1:0:-1])
        pR.extend(rInner[-1:0:-1])

    dPhi = pDPhi / numSide

    zrList = [[z, r] for z, r in zip(pZ, pR)]
    zrList.reverse()
    zrArray = _np.array(zrList)

    zrListConvex = _PolygonProcessing.decomposePolygon2d(zrArray)

    fregion = _fluka.Region("R" + name)

    # loop over zr convex polygons
    ibody = 0

    for i in range(0, len(zrListConvex), 1):
        for j in range(0, numSide, 1):
            j1 = j
            j2 = j + 1

            phi1 = dPhi * j1 + pSPhi
            phi2 = dPhi * j2 + pSPhi

            fzone = _fluka.Zone()

            for k in range(0, len(zrListConvex[i]), 1):
                k1 = k
                k2 = (k + 1) % len(zrListConvex[i])  # cyclic index as polygon is closed

                z1 = zrListConvex[i][k1][0]
                r1 = zrListConvex[i][k1][1]

                x1p1 = r1 * _np.cos(phi1)
                y1p1 = r1 * _np.sin(phi1)

                x1p2 = r1 * _np.cos(phi2)
                y1p2 = r1 * _np.sin(phi2)

                z2 = zrListConvex[i][k2][0]
                r2 = zrListConvex[i][k2][1]

                x2p1 = r2 * _np.cos(phi1)
                y2p1 = r2 * _np.sin(phi1)

                x2p2 = r2 * _np.cos(phi2)
                x2p2 = r2 * _np.sin(phi2)

                dx1 = x2p1 - x1p1
                dy1 = y2p1 - y1p1
                dz1 = z2 - z1

                l1 = _np.sqrt(dx1**2 + dy1**2 + dz1**2)

                dx1 = dx1 / l1
                dy1 = dy1 / l1
                dz1 = dz1 / l1

                dx2 = x1p2 - x1p1
                dy2 = y1p2 - y1p1
                dz2 = 0

                l2 = _np.sqrt(dx2**2 + dy2**2 + dz2**2)

                dx2 = dx2 / l2
                dy2 = dy2 / l2
                dz2 = dz2 / l2

                nx = dy1 * dz2 - dz1 * dy2
                ny = dz1 * dx2 - dx1 * dz2
                nz = dx1 * dy2 - dy1 * dx2

                if not bakeTransform:
                    fbody = flukaRegistry.makeBody(
                        PLA,
                        "B" + name + format(ibody, "02"),
                        [nx, ny, nz],
                        [x1p1, y1p1, z1],
                        transform=transform,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                else:
                    fbody = flukaRegistry.makeBody(
                        PLA,
                        "B" + name + format(ibody, "02"),
                        mtra @ _np.array([nx, ny, nz]),
                        mtra @ _np.array([x1p1, y1p1, z1]) + tra / 10,
                        transform=transform,
                        flukaregistry=flukaRegistry,
                        comment=commentName,
                    )
                fzone.addIntersection(fbody)
                ibody += 1

            if not bakeTransform:
                fbody = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + format(ibody, "02"),
                    [_np.cos(phi1 - _np.pi / 2.0), _np.sin(phi1 - _np.pi / 2.0), 0],
                    [0, 0, 0],
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            else:
                fbody = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + format(ibody, "02"),
                    mtra
                    @ _np.array([_np.cos(phi1 - _np.pi / 2.0), _np.sin(phi1 - _np.pi / 2.0), 0]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            fzone.addIntersection(fbody)
            ibody += 1

            if not bakeTransform:
                fbody = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + format(ibody, "02"),
                    [_np.cos(phi2 + _np.pi / 2.0), _np.sin(phi2 + _np.pi / 2.0), 0],
                    [0, 0, 0],
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            else:
                fbody = flukaRegistry.makeBody(
                    PLA,
                    "B" + name + format(ibody, "02"),
                    mtra
                    @ _np.array([_np.cos(phi2 + _np.pi / 2.0), _np.sin(phi2 + _np.pi / 2.0), 0]),
                    mtra @ _np.array([0, 0, 0]) + tra / 10,
                    transform=transform,
                    flukaregistry=flukaRegistry,
                    comment=commentName,
                )
            fzone.addIntersection(fbody)
            ibody += 1

            fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4EllipticalTube2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10

    pDx = solid.evaluateParameter(solid.pDx) * uval
    pDy = solid.evaluateParameter(solid.pDy) * uval
    pDz = solid.evaluateParameter(solid.pDz) * uval

    # main elliptical cylinder
    if not bakeTransform:
        fbody1 = _fluka.REC(
            "B" + name + "01",
            [0, 0, -pDz / 2],
            [0, 0, pDz],
            [pDx / 2, 0, 0],
            [0, pDy / 2, 0],
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody1 = _fluka.REC(
            "B" + name + "01",
            mtra @ _np.array([0, 0, -pDz / 2]) + tra / 10,
            mtra @ _np.array([0, 0, pDz]),
            mtra @ _np.array([pDx / 2, 0, 0]),
            mtra @ _np.array([0, pDy / 2, 0]),
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Ellipsoid2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10.0

    xsemi = solid.evaluateParameter(solid.pxSemiAxis) * uval
    ysemi = solid.evaluateParameter(solid.pySemiAxis) * uval
    zsemi = solid.evaluateParameter(solid.pzSemiAxis) * uval
    zlow = solid.evaluateParameter(solid.pzBottomCut) * uval
    zhigh = solid.evaluateParameter(solid.pzTopCut) * uval

    cxx = xsemi**-2
    cyy = ysemi**-2
    czz = zsemi**-2
    cxy = 0
    cxz = 0
    cyz = 0
    cx = 0
    cy = 0
    cz = 0
    c = -1

    if bakeTransform:
        print(cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c)
        cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c = transformQuadricFluka(
            cxx, cyy, czz, 0, 0, 0, 0, 0, 0, -1, mtra, tra / 10
        )
        print(cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c)
        transform = None

    # Main ellipsoid.  ELL can't be used as ELL is an ellipsoid of rotation.
    fbody1 = _fluka.QUA(
        f"B{name}_01",
        cxx,
        cyy,
        czz,
        cxy,
        cxz,
        cyz,
        cx,
        cy,
        cz,
        c,
        transform=transform,
        flukaregistry=flukaRegistry,
        comment=commentName,
    )

    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)

    # Optional cuts in z to the ellipsoid.
    ellcuti = 2
    if zhigh < zsemi:
        if not bakeTransform:
            fbody2 = flukaRegistry.makeBody(
                XYP,
                f"B{name}_0{ellcuti}",
                zhigh,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        else:
            fbody2 = flukaRegistry.makeBody(
                PLA,
                f"B{name}_0{ellcuti}",
                mtra @ _np.array([0, 0, 1]),
                mtra @ _np.array([0, 0, zhigh]) + tra / 10,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        fzone.addIntersection(fbody2)
        ellcuti += 1

    if zlow > -zsemi:
        if not bakeTransform:
            fbody3 = flukaRegistry.makeBody(
                XYP,
                f"B{name}_0{ellcuti}",
                zlow,
                transform=transform,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        else:
            fbody3 = flukaRegistry.makeBody(
                PLA,
                f"B{name}_0{ellcuti}",
                mtra @ _np.array([0, 0, 1]),
                mtra @ _np.array([0, 0, zlow]) + tra / 10.0,
                transform=None,
                flukaregistry=flukaRegistry,
                comment=commentName,
            )
        fzone.addSubtraction(fbody3)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4EllipticalCone2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10.0

    # xsemi and ysemi are unitless
    xsemi = solid.evaluateParameter(solid.pxSemiAxis)
    ysemi = solid.evaluateParameter(solid.pySemiAxis)
    zheight = solid.evaluateParameter(solid.zMax) * uval
    zcut = solid.evaluateParameter(solid.pzTopCut) * uval

    # (x/xSemiAxis)^2 + (y/ySemiAxis)^2 = (zheight - z)^2
    cxx = xsemi**-2
    cyy = ysemi**-2
    czz = -1
    cxy = 0
    cxz = 0
    cyz = 0
    cx = 0
    cy = 0
    cz = 2 * zheight
    c = -(zheight**2)

    print(cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c)

    if bakeTransform:
        cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c = transformQuadricFluka(
            cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c, mtra, tra / 10
        )
        print(cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c)
        transform = None

    fzone = _fluka.Zone()
    # Cone from general quadric
    fbody1 = _fluka.QUA(
        f"B{name}_01",
        cxx,
        cyy,
        czz,
        cxy,
        cxz,
        cyz,
        cx,
        cy,
        cz,
        c,
        transform=transform,
        flukaregistry=flukaRegistry,
        comment=commentName,
    )
    fzone.addIntersection(fbody1)

    # Do the cuts on the infinite cone to make it finite
    zcut = min(zcut, zheight)
    if not bakeTransform:
        fbody2 = flukaRegistry.makeBody(
            XYP,
            f"B{name}_02",
            zcut,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody2 = flukaRegistry.makeBody(
            PLA,
            f"B{name}_02",
            mtra @ _np.array([0, 0, 1]),
            mtra @ _np.array([0, 0, zcut]) + tra / 10,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    fzone.addIntersection(fbody2)

    if not bakeTransform:
        fbody3 = flukaRegistry.makeBody(
            XYP,
            f"B{name}_03",
            -zcut,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody3 = flukaRegistry.makeBody(
            PLA,
            f"B{name}_03",
            mtra @ _np.array([0, 0, 1]),
            mtra @ _np.array([0, 0, -zcut]) + tra / 10,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

    fzone.addSubtraction(fbody3)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Paraboloid2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10.0

    halflength = solid.evaluateParameter(solid.pDz) * uval / 2
    rlow = solid.evaluateParameter(solid.pR1) * uval
    rhigh = solid.evaluateParameter(solid.pR2) * uval

    # Equation:
    # x^2 + y^2 + bz + c = 0;

    cxx = 1
    cyy = 1
    czz = 0
    cxy = 0
    cxz = 0
    cyz = 0
    cx = 0
    cy = 0
    cz = (rlow**2 - rhigh**2) / (2 * halflength)
    c = (-(rhigh**2) - rlow**2) / 2

    if bakeTransform:
        cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c = transformQuadricFluka(
            cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c, mtra, tra / 10
        )
        print(cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c)
        transform = None

    fzone = _fluka.Zone()
    # Tip points in -ve z direction.  larger face is +ve z.
    fbody1 = _fluka.QUA(
        f"B{name}_01",
        cxx,
        cyy,
        czz,
        cxy,
        cxz,
        cyz,
        cx,
        cy,
        cz,
        c,
        transform=transform,
        flukaregistry=flukaRegistry,
        comment=commentName,
    )
    fzone.addIntersection(fbody1)

    # cut at positive z.
    if not bakeTransform:
        fbody2 = flukaRegistry.makeBody(
            XYP,
            f"B{name}_02",
            halflength,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody2 = flukaRegistry.makeBody(
            PLA,
            f"B{name}_02",
            mtra @ _np.array([0, 0, 1]),
            mtra @ _np.array([0, 0, halflength]) + tra / 10,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    fzone.addIntersection(fbody2)
    # cut at negative z
    if not bakeTransform:
        fbody3 = flukaRegistry.makeBody(
            XYP,
            f"B{name}_03",
            -halflength,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody3 = flukaRegistry.makeBody(
            PLA,
            f"B{name}_03",
            mtra @ _np.array([0, 0, 1]),
            mtra @ _np.array([0, 0, -halflength]) + tra / 10,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

    fzone.addSubtraction(fbody3)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Hype2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uvalL = _Units.unit(solid.lunit) / 10
    uvalA = _Units.unit(solid.aunit)

    outerRadius = solid.evaluateParameter(solid.outerRadius) * uvalL
    innerRadius = solid.evaluateParameter(solid.innerRadius) * uvalL
    outerStereo = solid.evaluateParameter(solid.outerStereo) * uvalA
    innerStereo = solid.evaluateParameter(solid.innerStereo) * uvalA
    lenZ = solid.evaluateParameter(solid.lenZ) * uvalL
    # x^2 + y^2 - b^2z^2 + c = 0; r^2 = x^2+y^2.
    cOuter = -(outerRadius**2)
    cInner = -(innerRadius**2)
    czzOuter = -_np.tan(outerStereo) ** 2
    czzInner = -_np.tan(innerStereo) ** 2

    cxx = 1
    cyy = 1
    czz = czzOuter
    cxy = 0
    cxz = 0
    cyz = 0
    cx = 0
    cy = 0
    cz = 0
    c = cOuter

    if bakeTransform:
        cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c = transformQuadricFluka(
            cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c, mtra, tra / 10
        )
        transform = None

    fzone = _fluka.Zone()
    # Outer QUA
    fbody1 = _fluka.QUA(
        f"B{name}_01",
        cxx,
        cyy,
        czz,
        cxy,
        cxz,
        cyz,
        cx,
        cy,
        cz,
        c,
        transform=transform,
        flukaregistry=flukaRegistry,
        comment=commentName,
    )
    fzone.addIntersection(fbody1)

    cxx = 1
    cyy = 1
    czz = czzInner
    cxy = 0
    cxz = 0
    cyz = 0
    cx = 0
    cy = 0
    cz = 0
    c = cInner

    if bakeTransform:
        cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c = transformQuadricFluka(
            cxx, cyy, czz, cxy, cxz, cyz, cx, cy, cz, c, mtra, tra / 10
        )
        transform = None

    ihype = 2
    # Only build if it is not null
    if innerRadius != 0 or innerStereo != 0:
        # Inner QUA
        fbody2 = _fluka.QUA(
            f"B{name}_0{ihype}",
            cxx,
            cyy,
            czz,
            cxy,
            cxz,
            cyz,
            cx,
            cy,
            cz,
            c,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
        fzone.addSubtraction(fbody2)
        ihype += 1

    if not bakeTransform:
        fbody3 = flukaRegistry.makeBody(
            XYP,
            f"B{name}_0{ihype}",
            lenZ / 2.0,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody3 = flukaRegistry.makeBody(
            PLA,
            f"B{name}_0{ihype}",
            mtra @ _np.array([0, 0, 1]),
            mtra @ _np.array([0, 0, lenZ / 2.0]) + tra / 10,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

    fzone.addIntersection(fbody3)
    ihype += 1

    if not bakeTransform:
        fbody4 = flukaRegistry.makeBody(
            XYP,
            f"B{name}_0{ihype}",
            -lenZ / 2.0,
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    else:
        fbody4 = flukaRegistry.makeBody(
            PLA,
            f"B{name}_0{ihype}",
            mtra @ _np.array([0, 0, 1]),
            mtra @ _np.array([0, 0, -lenZ / 2.0]) + tra / 10,
            transform=None,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    fzone.addSubtraction(fbody4)

    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4Tet2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit)

    verts = []
    if not bakeTransform:
        verts.append([x / 10 for x in solid.anchor.eval()])
        verts.append([x / 10 for x in solid.p2.eval()])
        verts.append([x / 10 for x in solid.p3.eval()])
        verts.append([x / 10 for x in solid.p4.eval()])
        verts.append([0, 0, 0])
        verts.append([0, 0, 0])
        verts.append([0, 0, 0])
        verts.append([0, 0, 0])
    else:
        verts.append(mtra @ _np.array(solid.anchor.eval()) / 10 + tra / 10)
        verts.append(mtra @ _np.array(solid.p2.eval()) / 10 + tra / 10)
        verts.append(mtra @ _np.array(solid.p3.eval()) / 10 + tra / 10)
        verts.append(mtra @ _np.array(solid.p4.eval()) / 10 + tra / 10)
        verts.append([0, 0, 0] + tra / 10)
        verts.append([0, 0, 0] + tra / 10)
        verts.append([0, 0, 0] + tra / 10)
        verts.append([0, 0, 0] + tra / 10)
        transform = None

    fbody1 = _fluka.ARB(
        "B" + name + "01",
        verts,
        [123.0, 134.0, 243.0, 142.0, 0.0, 0.0],
        transform=transform,
        flukaregistry=flukaRegistry,
        comment=commentName,
    )

    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)
    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    # fregion = pycsgmesh2FlukaRegion(solid.mesh(), name, transform, flukaRegistry, commentName)
    flukaNameCount += 1

    return fregion, flukaNameCount


def geant4GenericTrap2Fluka(
    flukaNameCount,
    solid,
    mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    tra=_np.array([0, 0, 0]),
    flukaRegistry=None,
    addRegistry=True,
    commentName="",
    bakeTransform=False,
):
    pseudoVector = _np.linalg.det(mtra)
    name = format(flukaNameCount, "04")

    from ..gdml import Units as _Units  # TODO move circular import

    rotation = _transformation.matrix2tbxyz(mtra)
    transform = _rotoTranslationFromTra2("T" + name, [rotation, tra], flukaregistry=flukaRegistry)

    uval = _Units.unit(solid.lunit) / 10

    verts = []
    for i in range(1, 9):
        if not bakeTransform:
            vert = [x * uval for x in list(solid.get_vertex(i))]
        else:
            vert = mtra @ _np.array(list(solid.get_vertex(i))) * uval + tra / 10

        verts.append(vert)

    if bakeTransform:
        transform = _rotoTranslationFromTra2(
            "IDENT", [[0.0, 0, 0], [0, 0, 0]], flukaregistry=flukaRegistry, allowZero=True
        )

    verts_tuple = tuple(tuple(vert) for vert in verts)
    verts_set = set(verts_tuple)

    if len(verts_set) == 8:
        fbody1 = _fluka.ARB(
            "B" + name + "01",
            verts,
            [4321.0, 5678.0, 2651.0, 3762.0, 7843.0, 5841.0],
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    elif len(verts_set) == 6:
        fbody1 = _fluka.WED(
            "B" + name + "01",
            verts[0],
            [v1 - v2 for v1, v2 in zip(verts[1], verts[0])],
            [v1 - v2 for v1, v2 in zip(verts[3], verts[0])],
            [v1 - v2 for v1, v2 in zip(verts[4], verts[0])],
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )
    elif len(verts_set) == 4:
        fbody1 = _fluka.ARB(
            "B" + name + "01",
            verts,
            [123.0, 134.0, 243.0, 142.0, 0.0, 0.0],
            transform=transform,
            flukaregistry=flukaRegistry,
            comment=commentName,
        )

    fzone = _fluka.Zone()
    fzone.addIntersection(fbody1)
    fregion = _fluka.Region("R" + name)
    fregion.addZone(fzone)

    flukaNameCount += 1

    return fregion, flukaNameCount


def makeStripName(mn):
    if mn.find("0x") != -1:
        mnStrip = mn[0 : mn.find("0x")]
        # mnStrip = mn[mn.find("0x")+2:]
    else:
        mnStrip = mn
    return mnStrip


def makeShortName(mn):
    mn = makeStripName(mn)
    if len(mn) > 8:
        mn = mn.replace("_", "")  # first, remove '_'
        if len(mn) > 8:
            return mn[:8]
        else:
            return mn
    else:
        return mn


def transformQuadricFluka(axx, ayy, azz, axy, axz, ayz, ax, ay, az, a, M, T):
    Q = _np.array([[axx, axy / 2, axz / 2], [axy / 2, ayy, ayz / 2], [axz / 2, ayz / 2, azz]])
    P = _np.array([ax, ay, az])
    R = a

    Qprime, Pprime, Rprime = transformQuadricMatrix(Q, P, R, M, T)

    return (
        Qprime[0, 0],
        Qprime[1, 1],
        Qprime[2, 2],
        Qprime[0, 1] * 2,
        Qprime[0, 2] * 2,
        Qprime[1, 2] * 2,
        Pprime[0],
        Pprime[1],
        Pprime[2],
        Rprime,
    )


def transformQuadricMatrix(Q, P, R, M, T):
    M = _np.linalg.inv(M)
    T = -M @ T
    Qprime = M.T @ Q @ M
    Pprime = M.T @ Q @ T + M.T @ Q.T @ T + M.T @ P
    Rprime = R + T @ Q @ T + P @ T

    return Qprime, Pprime, Rprime
