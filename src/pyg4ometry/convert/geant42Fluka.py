import pyg4ometry.transformation as _transformation
import pyg4ometry.geant4 as _geant4
import pyg4ometry.fluka as _fluka
import pyg4ometry.pycgal as _pycgal
from pyg4ometry.pycgal.core import PolygonProcessing as _PolygonProcessing
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
import numpy as _np
import copy as _copy

# this should be refactored to rename namespaced (privately)
from pyg4ometry.fluka.body import *

# import matplotlib.pyplot as _plt

def geant4Reg2FlukaReg(greg, logicalVolumeName = '') :

    freg = _fluka.FlukaRegistry()

    if logicalVolumeName == '':
        logi = greg.getWorldVolume()
    else :
        logi = greg.logicalVolumeDict[logicalVolumeName]
    freg = geant4MaterialDict2Fluka(greg.materialDict, freg)
    freg = geant4Logical2Fluka(logi, freg)

    return freg

def geant4Logical2Fluka(logicalVolume, flukaRegistry = None) :
    mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]])
    tra  = _np.array([0,0,0])

    if not flukaRegistry :
        flukaRegistry = _fluka.FlukaRegistry()

    flukaNameCount = 0

    # find extent of logical
    extent = logicalVolume.extent(includeBoundingSolid = True)

    rotation = _transformation.matrix2tbxyz(mtra)
    position = tra

    blackBody = _fluka.RPP("BLKBODY",
                           2*extent[0][0]/10,2*extent[1][0]/10,
                           2*extent[0][1]/10,2*extent[1][1]/10,
                           2*extent[0][2]/10,2*extent[1][2]/10,
                           transform=_rotoTranslationFromTra2("BBROTDEF",[rotation,position],
                                                              flukaregistry=flukaRegistry),
                           flukaregistry=flukaRegistry)

    fzone = _fluka.Zone()
    fzone.addIntersection(blackBody)

    # create top logical volume
    if logicalVolume.type == "logical" :
        flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,logicalVolume.solid,mtra,tra,
                                                                         flukaRegistry, commentName=logicalVolume.name)
    elif logicalVolume.type == "assembly" :
        e = logicalVolume.extent()
        b = _geant4.solid.Box("ra",1.1*(e[1][0]-e[0][0]), 1.1*(e[1][1]-e[0][1]), 1.1*(e[1][2]-e[0][2]),logicalVolume.registry,"mm", False)
        flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,b,mtra,tra,
                                                                         flukaRegistry, commentName=logicalVolume.name)
    else:
        # avoid warning about flukaMotherOuterRegion being used without assignment
        print("Type (",logicalVolume.type,") cannot be converted - skipping: ",logicalVolume.name)
        return

    flukaMotherRegion      = _copy.deepcopy(flukaMotherOuterRegion)
    flukaNameCount += 1

    for zone in flukaMotherOuterRegion.zones :
        fzone.addSubtraction(zone)

    for dv in logicalVolume.daughterVolumes :

        pvmrot = _transformation.tbzyx2matrix(-_np.array(dv.rotation.eval()))
        pvtra =  _np.array(dv.position.eval())

        new_mtra = mtra * pvmrot
        new_tra  = (_np.array(mtra.dot(pvtra)) + tra)[0]

        flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(dv,new_mtra,new_tra,flukaRegistry,
                                                                              flukaNameCount)

        # subtract daughters from black body
        for motherZones in flukaMotherRegion.zones :
            for daughterZones in flukaDaughterOuterRegion.zones :
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
    flukaRegistry.addMaterialAssignments("BLCKHOLE",
                                         "BLKHOLE")

    ###########################################
    # assign material to region
    ###########################################
    if logicalVolume.type == "logical" :
        materialName = logicalVolume.material.name
        materialNameShort = makeShortName(materialName)

        try :
            flukaMaterial = flukaRegistry.materials[materialNameShort]
            flukaRegistry.addMaterialAssignments(flukaMaterial,
                                             flukaMotherRegion)
        except KeyError :
            pass
    elif logicalVolume.type == "assembly" :
        flukaRegistry.addMaterialAssignments("AIR",
                                             flukaMotherRegion)

    return flukaRegistry

def geant4PhysicalVolume2Fluka(physicalVolume,
                               mtra=_np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                               tra=_np.array([0, 0, 0]),
                               flukaRegistry=None,flukaNameCount=0) :

    # logical volume (outer and complete)
    if physicalVolume.logicalVolume.type == "logical" :
        geant4LvOuterSolid = physicalVolume.logicalVolume.solid
        flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,
                                                                     geant4LvOuterSolid,
                                                                     mtra,tra,
                                                                     flukaRegistry,
                                                                     commentName=physicalVolume.name)
    elif physicalVolume.logicalVolume.type == "assembly" :
        name = "R"+format(flukaNameCount, '04')
        flukaMotherOuterRegion = _fluka.Region(name)
        flukaNameCount += 1
    else:
        # avoid warning about flukaMotherOuterRegion being used without assignment
        print("Type (",physicalVolume.logicalVolume.type,") cannot be converted - skipping: ",physicalVolume.name)
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
    if replicaCondition1: # can only do this if len > 0
        replicaCondition2 = type(physicalVolume.logicalVolume.daughterVolumes[0]) is _geant4.ReplicaVolume
    itsAReplica = replicaCondition1 and replicaCondition2
    if itsAReplica:
        replica = physicalVolume.logicalVolume.daughterVolumes[0]
        # this unintentionally adds the PVs to the mother LV
        daughterVolumes, transforms = replica.getPhysicalVolumes()
        for dv in daughterVolumes:
            pvmrot = _transformation.tbzyx2matrix(-_np.array(dv.rotation.eval()))
            pvtra = _np.array(dv.position.eval())
            new_mtra = mtra * pvmrot
            new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]
            flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(dv, new_mtra, new_tra,
                                                                                  flukaRegistry=flukaRegistry,
                                                                                  flukaNameCount=flukaNameCount)

        materialName = daughterVolumes[0].logicalVolume.material.name
        materialNameShort = makeShortName(materialName)

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
            pvtra  = _np.array(dv.position.eval())

            new_mtra = mtra * pvmrot
            new_tra  = (_np.array(mtra.dot(pvtra)) + tra)[0]

            flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(dv,new_mtra,new_tra,
                                                                                  flukaRegistry=flukaRegistry,
                                                                                  flukaNameCount=flukaNameCount)
            if physicalVolume.logicalVolume.type == "logical" :
                for motherZones in flukaMotherRegion.zones:
                    for daughterZones in flukaDaughterOuterRegion.zones:
                        motherZones.addSubtraction(daughterZones)
            elif physicalVolume.logicalVolume.type == "assembly" :
                # If assembly the daughters form the outer
                for daughterZones in flukaDaughterOuterRegion.zones :
                    flukaMotherOuterRegion.addZone(daughterZones)

        if physicalVolume.logicalVolume.type == "logical" :
            flukaRegistry.addRegion(flukaMotherRegion)
            materialName = physicalVolume.logicalVolume.material.name
            materialNameShort = makeShortName(materialName)

            try:
                flukaMaterial = flukaRegistry.materials[materialNameShort]
                flukaRegistry.addMaterialAssignments(flukaMaterial, flukaMotherRegion)
            except KeyError :
                pass

    return flukaMotherOuterRegion, flukaNameCount

def geant4Solid2FlukaRegion(flukaNameCount,solid,
                            mtra=_np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                            tra=_np.array([0, 0, 0]),
                            flukaRegistry = None,
                            addRegistry = True,
                            commentName = "") :

    import pyg4ometry.gdml.Units as _Units  # TODO move circular import

    name = format(flukaNameCount,'04')

    fregion = None
    fbodies = []

    rotation = _transformation.matrix2tbxyz(mtra)
    position = tra

    transform= _rotoTranslationFromTra2("T"+name,[rotation,tra],
                                        flukaregistry=flukaRegistry)

    commentName = commentName + " " + solid.name

    # print 'geant4Solid2FlukaRegion',flukaNameCount,name,solid.type, rotation,position,transform

    if solid.type == 'Box' :
        uval = _Units.unit(solid.lunit)/10.
        pX = solid.evaluateParameter(solid.pX)*uval/2.0
        pY = solid.evaluateParameter(solid.pY)*uval/2.0
        pZ = solid.evaluateParameter(solid.pZ)*uval/2.0

        fbody = _fluka.RPP("B"+name+'01', -pX, pX, -pY, pY, -pZ, pZ,
                           transform=transform,
                           flukaregistry=flukaRegistry,
                           addRegistry=True,
                           comment=commentName)

        # store all bodies
        fbodies.append(fbody)

        # create zones and region
        fzone = _fluka.Zone()
        fzone.addIntersection(fbody)
        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Tubs":

        uval = _Units.unit(solid.lunit)/10.
        aval = _Units.unit(solid.aunit)

        pRMin = solid.evaluateParameter(solid.pRMin)*uval
        pSPhi = solid.evaluateParameter(solid.pSPhi)*aval
        pDPhi = solid.evaluateParameter(solid.pDPhi)*aval
        pDz   = solid.evaluateParameter(solid.pDz)*uval
        pRMax = solid.evaluateParameter(solid.pRMax)*uval

        # main cylinder
        fbody1 = flukaRegistry.makeBody(ZCC, "B"+name+"01",0,0,pRMax,
                                        transform=transform,
                                        flukaregistry=flukaRegistry,
                                        comment=commentName)

        # low z cut
        fbody2 = flukaRegistry.makeBody(XYP, "B"+name+"02",-pDz/2,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # high z cut
        fbody3 = flukaRegistry.makeBody(XYP, "B"+name+"03", pDz/2,
                                        transform=transform,
                                        flukaregistry=flukaRegistry,
                                        comment=commentName)

        # inner cylinder
        if pRMin != 0 :
            fbody4 = flukaRegistry.makeBody(ZCC, "B"+name+"04",0,0,pRMin,
                                            transform=transform,
                                            flukaregistry=flukaRegistry,
                                            comment=commentName)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody5 = flukaRegistry.makeBody(PLA, "B"+name+"05",
                                [-_np.sin(pSPhi),  _np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody6 = flukaRegistry.makeBody(PLA, "B"+name+"06",
                                [-_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)


        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)
        fzone.addSubtraction(fbody2)
        fzone.addIntersection(fbody3)

        if pRMin != 0 :
            fzone.addSubtraction(fbody4)


        if pDPhi != 2*_np.pi :
            if pDPhi < _np.pi :
                fzone.addSubtraction(fbody5)
                fzone.addIntersection(fbody6)
            elif pDPhi == _np.pi :
                fzone.addSubtraction(fbody5)
            else :
                fzone1 = _fluka.Zone()
                fzone1.addIntersection(fbody5)
                fzone1.addSubtraction(fbody6)
                fzone.addSubtraction(fzone1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "CutTubs" :

        uval = _Units.unit(solid.lunit)/10
        aval = _Units.unit(solid.aunit)

        pRMin = solid.evaluateParameter(solid.pRMin)*uval
        pSPhi = solid.evaluateParameter(solid.pSPhi)*aval
        pDPhi = solid.evaluateParameter(solid.pDPhi)*aval
        pDz   = solid.evaluateParameter(solid.pDz)*uval
        pRMax = solid.evaluateParameter(solid.pRMax)*uval
        pLowNorm0  = solid.evaluateParameter(solid.pLowNorm[0])
        pLowNorm1  = solid.evaluateParameter(solid.pLowNorm[1])
        pLowNorm2  = solid.evaluateParameter(solid.pLowNorm[2])
        pHighNorm0 = solid.evaluateParameter(solid.pHighNorm[0])
        pHighNorm1 = solid.evaluateParameter(solid.pHighNorm[1])
        pHighNorm2 = solid.evaluateParameter(solid.pHighNorm[2])

        # main cylinder
        fbody1 = flukaRegistry.makeBody(ZCC, "B"+name+"01",0,0,pRMax,
                                        transform=transform,
                                        flukaregistry=flukaRegistry,
                                        comment=commentName)

        # low z cut
        fbody2 = flukaRegistry.makeBody(PLA, "B"+name+"02",
                            [-pLowNorm0,-pLowNorm1,-pLowNorm2],
                            [0, 0, -pDz/2],
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # high z cut
        fbody3 = flukaRegistry.makeBody(PLA, "B"+name+"03",
                            [pHighNorm0,pHighNorm1,pHighNorm2],
                            [0, 0, pDz/2.],
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        if pRMin != 0 :
            # inner cylinder
            fbody4 = flukaRegistry.makeBody(ZCC, "B"+name+"04",0,0,pRMin,
                                            transform=transform,
                                            flukaregistry=flukaRegistry,
                                            comment=commentName)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody5 = flukaRegistry.makeBody(PLA, "B"+name+"05",
                                [-_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody6 = flukaRegistry.makeBody(PLA, "B"+name+"06",
                                [-_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)
        fzone.addSubtraction(fbody2)
        fzone.addIntersection(fbody3)

        if pRMin != 0 :
            fzone.addSubtraction(fbody4)

        if pDPhi != 2*_np.pi :
            if pDPhi < _np.pi :
                fzone.addSubtraction(fbody5)
                fzone.addIntersection(fbody6)
            elif pDPhi == _np.pi :
                fzone.addSubtraction(fbody5)
            else :
                fzone1 = _fluka.Zone()
                fzone1.addIntersection(fbody5)
                fzone1.addSubtraction(fbody6)
                fzone.addSubtraction(fzone1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Cons" :
        luval = _Units.unit(solid.lunit)/10.0
        auval = _Units.unit(solid.aunit)

        pRmin1 = solid.evaluateParameter(solid.pRmin1)*luval
        pRmax1 = solid.evaluateParameter(solid.pRmax1)*luval
        pRmin2 = solid.evaluateParameter(solid.pRmin2)*luval
        pRmax2 = solid.evaluateParameter(solid.pRmax2)*luval
        pDz    = solid.evaluateParameter(solid.pDz)*luval
        pSPhi  = solid.evaluateParameter(solid.pSPhi)*auval
        pDPhi  = solid.evaluateParameter(solid.pDPhi)*auval

        dir    = pDz*_transformation.tbxyz2matrix(rotation).dot(_np.array([0, 0, 1]))
        base   = -dir/2.0

        fbody1 = _fluka.TRC("B"+name+"01",base,dir,pRmax1,pRmax2,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        if pRmin1 != 0 and pRmin2 != 0 :
            fbody2 = _fluka.TRC("B" + name + "02",
                                base, dir, pRmin1, pRmin2,
                                transform=transform,
                                flukaregistry=flukaRegistry)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody3 = flukaRegistry.makeBody(PLA, "B"+name+"03",
                                [-_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody4 = flukaRegistry.makeBody(PLA, "B"+name+"04",
                                [-_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)


        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        if pRmin1 != 0 and pRmin2 != 0 :
            fzone.addSubtraction(fbody2)

        if pDPhi != 2*_np.pi :
            if pDPhi < _np.pi :
                fzone.addSubtraction(fbody3)
                fzone.addIntersection(fbody4)
            elif pDPhi == _np.pi :
                fzone.addSubtraction(fbody3)
            else :
                fzone1 = _fluka.Zone()
                fzone1.addIntersection(fbody3)
                fzone1.addSubtraction(fbody4)
                fzone.addSubtraction(fzone1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Para" :

        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1
        ''' 

        luval = _Units.unit(solid.lunit)/10.0/2.0
        auval = _Units.unit(solid.aunit)

        pX     = solid.evaluateParameter(solid.pX)*luval
        pY     = solid.evaluateParameter(solid.pY)*luval
        pZ     = solid.evaluateParameter(solid.pZ)*luval
        pAlpha = solid.evaluateParameter(solid.pAlpha)*auval
        pTheta = solid.evaluateParameter(solid.pTheta)*auval
        pPhi   = solid.evaluateParameter(solid.pPhi)*auval

        mTheta = _transformation.tbxyz2matrix([0,pTheta,0])
        mAlpha = _transformation.tbxyz2matrix([0,0,pAlpha])
        n1     = mAlpha.dot(mTheta).dot(_np.array([-1,0,0]))
        n2     = mAlpha.dot(mTheta).dot(_np.array([1,0,0]))
        fbody1 = flukaRegistry.makeBody(PLA, "B"+name+"_01",n1,[-pX,0,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody2 = flukaRegistry.makeBody(PLA, "B"+name+"_02",n2,[pX,0,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody3 = flukaRegistry.makeBody(PLA, "B"+name+"_03",[0,-_np.cos(pPhi),_np.sin(pPhi)],[0,-pY,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody4 = flukaRegistry.makeBody(PLA, "B"+name+"_04",[0,_np.cos(pPhi),-_np.sin(pPhi)],[0,pY,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody5 = flukaRegistry.makeBody(PLA, "B"+name+"_05",[0,0,-1],[0,0,-pZ],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody6 = flukaRegistry.makeBody(PLA, "B"+name+"_06",[0,0,1],[0,0,pZ],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)
        fzone.addIntersection(fbody2)
        fzone.addIntersection(fbody3)
        fzone.addIntersection(fbody4)
        fzone.addIntersection(fbody5)
        fzone.addIntersection(fbody6)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1
        '''

    elif solid.type == "Trd" :
        print('calling pycsgmesh2FlakaRegion trd')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Trap" :
        print('calling pycsgmesh2FlakaRegion trap')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Sphere" :

        luval = _Units.unit(solid.lunit)/10.0
        auval = _Units.unit(solid.aunit)

        pRmin   = solid.evaluateParameter(solid.pRmin)*luval
        pRmax   = solid.evaluateParameter(solid.pRmax)*luval
        pSPhi   = solid.evaluateParameter(solid.pSPhi)*auval
        pDPhi   = solid.evaluateParameter(solid.pDPhi)*auval
        pSTheta = solid.evaluateParameter(solid.pSTheta)*auval
        pDTheta = solid.evaluateParameter(solid.pDTheta)*auval

        fbody1  = _fluka.SPH("B"+name+"01", [0,0,0], pRmax,
                             transform=transform,
                             flukaregistry=flukaRegistry,
                             comment=commentName)

        if pRmin != 0 :
            fbody2 = _fluka.SPH("B"+name+"02", [0,0,0], pRmin,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody3 = flukaRegistry.makeBody(PLA, "B"+name+"03",
                                [-_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody4 = flukaRegistry.makeBody(PLA, "B"+name+"04",
                                [-_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
        pTheta1 = pSTheta
        pTheta2 = pSTheta+pDTheta

        if pTheta1 != 0 :
            if pTheta1 < _np.pi/2.0 :
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC("B"+name+"05",
                                    [0,0,pRmax],
                                    [0,0,-pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

            elif pTheta1 > _np.pi/2.0 :
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC("B"+name+"05",
                                    [0,0,-pRmax],
                                    [0,0,pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)
            else :
                fbody5 = flukaRegistry.makeBody(XYP, "B"+name+"05",0,
                                    transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

        if pTheta2 != _np.pi:
            if pTheta2 < _np.pi/2.0 :
                r = abs(_np.tan(pTheta2) * pRmax)

                fbody6 = _fluka.TRC("B"+name+"06",
                                    [0,0,pRmax],
                                    [0,0,-pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

            elif pTheta2 > _np.pi/2.0 :
                r = abs(_np.tan(pTheta2) * pRmax)
                fbody6 = _fluka.TRC("B"+name+"06",
                                    [0,0,-pRmax],
                                    [0,0,pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)
            else :
                fbody6 = flukaRegistry.makeBody(XYP, "B"+name+"06",0,
                                    transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        if pRmin != 0 :
            fzone.addSubtraction(fbody2)

        if pDPhi != 2*_np.pi :
            if pDPhi < _np.pi :
                fzone.addSubtraction(fbody3)
                fzone.addIntersection(fbody4)
            elif pDPhi == _np.pi :
                fzone.addSubtraction(fbody3)
            else :
                fzone1 = _fluka.Zone()
                fzone1.addIntersection(fbody3)
                fzone1.addSubtraction(fbody4)
                fzone.addSubtraction(fzone1)

        if pTheta1 != 0 :
            if pTheta1 < _np.pi/2.0 :
                fzone.addSubtraction(fbody5)
            elif pTheta1 > _np.pi/2.0 :
                fzone.addIntersection(fbody5)
            else  :
                fzone.addIntersection(fbody5)

        if pTheta2 != _np.pi :
            if pTheta2 > _np.pi/2.0 :
                fzone.addSubtraction(fbody6)
            elif pTheta2 < _np.pi/2.0 :
                fzone.addIntersection(fbody6)
            else :
                fzone.addIntersection(fbody6)


        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Orb" :
        luval = _Units.unit(solid.lunit)

        pRmax   = solid.evaluateParameter(solid.pRMax)*luval/10.0

        fbody1  = _fluka.SPH("B"+name+"01", [0,0,0], pRmax,
                             transform=transform,
                             flukaregistry=flukaRegistry,
                             comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Torus" :
        luval = _Units.unit(solid.lunit)
        auval = _Units.unit(solid.aunit)

        pRmin = solid.evaluateParameter(solid.pRmin)*luval/10.0
        pRmax = solid.evaluateParameter(solid.pRmax)*luval/10.0
        pRtor = solid.evaluateParameter(solid.pRtor)*luval/10.0
        pSPhi = solid.evaluateParameter(solid.pSPhi)*auval
        pDPhi = solid.evaluateParameter(solid.pDPhi)*auval

        dPhi = pDPhi/solid.nstack

        # create region
        fregion = _fluka.Region("R" + name)

        d =  pDPhi*pRtor/solid.nstack/2*1.35

        for i in range(0,solid.nstack,1):

            x0 = pRtor * _np.cos(i*dPhi + pSPhi)
            y0 = pRtor * _np.sin(i*dPhi + pSPhi)
            z0 = 0

            nx0 =  d * _np.cos(i*dPhi + pSPhi + _np.pi/2.0)
            ny0 =  d * _np.sin(i*dPhi + pSPhi + _np.pi/2.0)
            nz0 = 0

            x1 = pRtor * _np.cos((i+0.5)*dPhi + pSPhi)
            y1 = pRtor * _np.sin((i+0.5)*dPhi + pSPhi)
            z1 = 0

            nx1 =  d * _np.cos((i+0.5)*dPhi + pSPhi + _np.pi/2.0)
            ny1 =  d * _np.sin((i+0.5)*dPhi + pSPhi + _np.pi/2.0)
            nz1 = 0

            x1 = x1 - nx1
            y1 = y1 - ny1


            x2 = pRtor * _np.cos((i+1)*dPhi + pSPhi)
            y2 = pRtor * _np.sin((i+1)*dPhi + pSPhi)
            z2 = 0

            nx2 =  d * _np.cos((i+1)*dPhi + pSPhi + _np.pi/2.0)
            ny2 =  d * _np.sin((i+1)*dPhi + pSPhi + _np.pi/2.0)
            nz2 = 0

            body1 = _fluka.RCC("B"+name+""+format(4*i,'02'),
                               [x1,y1,z1],
                               [2*nx1,2*ny1,2*nz1],
                               pRmax,
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)
            body2 = flukaRegistry.makeBody(PLA, "B"+name+""+format(4*i+1,'02'),
                               [nx0, ny0, nz0],
                               [x0,y0,z0],
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)

            body3 = flukaRegistry.makeBody(PLA, "B"+name+""+format(4*i+2,'02'),
                               [nx2, ny2, nz2],
                               [x2,y2,z2],
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)

            if pRmin != 0 :
                body4 = _fluka.RCC("B" + name + format(4 * i + 3, '02'),
                                   [x1, y1, z1],
                                   [2 * nx1, 2 * ny1, 2 * nz1],
                                   pRmin,
                                   transform=transform,
                                   flukaregistry=flukaRegistry,
                                   comment=commentName)

            fzone = _fluka.Zone()
            fzone.addIntersection(body1)
            fzone.addSubtraction(body2)
            fzone.addIntersection(body3)
            if pRmin != 0 :
                fzone.addSubtraction(body4)

            fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "GenericPolycone"  or solid.type == "Polycone":

        if solid.type == "GenericPolycone":

            import pyg4ometry.gdml.Units as _Units  # TODO move circular import
            luval = _Units.unit(solid.lunit)/10.0
            auval = _Units.unit(solid.aunit)

            pSPhi = solid.evaluateParameter(solid.pSPhi)*auval
            pDPhi = solid.evaluateParameter(solid.pDPhi)*auval
            pR = [val*luval for val in solid.evaluateParameter(solid.pR)]
            pZ = [val*luval for val in solid.evaluateParameter(solid.pZ)]

        elif solid.type == "Polycone":
            import pyg4ometry.gdml.Units as _Units  # TODO move circular import
            luval = _Units.unit(solid.lunit)/10.0
            auval = _Units.unit(solid.aunit)

            pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
            pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

            pZpl = [val * luval for val in solid.evaluateParameter(solid.pZpl)]
            pRMin = [val * luval  for val in solid.evaluateParameter(solid.pRMin)]
            pRMax = [val * luval  for val in solid.evaluateParameter(solid.pRMax)]

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

        zrList  = [[z,r] for z,r in zip(pZ,pR)]
        zrList.reverse()
        zrArray = _np.array(zrList)

        zrListConvex = _PolygonProcessing.decomposePolygon2d(zrArray)

        #_plt.figure()
        #_plt.plot(pZ,pR,"*-")

        # loop over zr convex polygons
        ibody = 0

        fregion = _fluka.Region("R"+name)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody1 = flukaRegistry.makeBody(PLA, "B"+name+format(ibody, '02'),
                                [-_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            ibody += 1
            fbody2 = flukaRegistry.makeBody(PLA, "B"+name+format(ibody, '02'),
                                [-_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            ibody += 1


        for i in range(0, len(zrListConvex), 1):

            #zConv = [zr[0] for zr in zrListConvex[i]]
            #rConv = [zr[1] for zr in zrListConvex[i]]
            #_plt.plot(zConv,rConv)

            posBodies = []
            negBodies = []

            for j in range(0,len(zrListConvex[i]),1) :

                j1 = j
                j2 = (j+1) % len(zrListConvex[i])

                z1 = zrListConvex[i][j1][0]
                r1 = zrListConvex[i][j1][1]

                z2 = zrListConvex[i][j2][0]
                r2 = zrListConvex[i][j2][1]

                dz = z2 - z1
                dr = r2 - r1

                if dz == 0:
                    pass

                elif dz > 0 and r1 != 0 and r2 != 0:
                    body = _fluka.TRC("B" + name + format(ibody, '02'),
                                      [0,0,z1],
                                      [0,0,dz],
                                      r1,r2,
                                      transform=transform,
                                      flukaregistry=flukaRegistry,
                                      comment=commentName)
                    negBodies.append(body)
                    ibody += 1

                elif  dz < 0 and r1 != 0 and r2 != 0:
                    body = _fluka.TRC("B" + name + format(ibody, '02'),
                                      [0,0,z1],
                                      [0,0,dz],
                                      r1,r2,
                                      transform=transform,
                                      flukaregistry=flukaRegistry,
                                      comment=commentName)
                    posBodies.append(body)
                    ibody += 1

            for pb in posBodies :
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

    elif solid.type == "GenericPolyhedra" or solid.type == "Polyhedra":

        if solid.type == "GenericPolyhedra" :
            import pyg4ometry.gdml.Units as _Units #TODO move circular import
            luval = _Units.unit(solid.lunit)
            auval = _Units.unit(solid.aunit)

            pSPhi = solid.evaluateParameter(solid.pSPhi)*auval
            pDPhi = solid.evaluateParameter(solid.pDPhi)*auval
            numSide = int(solid.evaluateParameter(solid.numSide))
            pR = [val*luval/10.0 for val in solid.evaluateParameter(solid.pR)]
            pZ = [val*luval/10.0 for val in solid.evaluateParameter(solid.pZ)]

        elif solid.type == "Polyhedra" :
            import pyg4ometry.gdml.Units as _Units  # TODO move circular import
            luval = _Units.unit(solid.lunit)
            auval = _Units.unit(solid.aunit)

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


        zrList  = [[z,r] for z,r in zip(pZ,pR)]
        zrList.reverse()
        zrArray = _np.array(zrList)

        zrListConvex = _PolygonProcessing.decomposePolygon2d(zrArray)

        fregion = _fluka.Region("R"+name)

        # loop over zr convex polygons
        ibody = 0

        for i in range(0, len(zrListConvex), 1):

            for j in range(0,numSide, 1) :

                j1 = j
                j2 = j + 1

                phi1 = dPhi * j1 + pSPhi
                phi2 = dPhi * j2 + pSPhi

                fzone = _fluka.Zone()

                for k in range(0,len(zrListConvex[i]),1) :

                    k1 = k
                    k2 = (k+1) % len(zrListConvex[i])                       # cyclic index as polygon is closed

                    z1 = zrListConvex[i][k1][0]
                    r1 = zrListConvex[i][k1][1]

                    x1p1 = r1*_np.cos(phi1)
                    y1p1 = r1*_np.sin(phi1)

                    x1p2 = r1*_np.cos(phi2)
                    y1p2 = r1*_np.sin(phi2)

                    z2 = zrListConvex[i][k2][0]
                    r2 = zrListConvex[i][k2][1]

                    x2p1 = r2 * _np.cos(phi1)
                    y2p1 = r2 * _np.sin(phi1)

                    x2p2 = r2 * _np.cos(phi2)
                    x2p2 = r2 * _np.sin(phi2)

                    dx1 = x2p1 - x1p1
                    dy1 = y2p1 - y1p1
                    dz1 = z2 - z1

                    l1  = _np.sqrt(dx1**2 + dy1**2 + dz1**2)

                    dx1 = dx1/l1
                    dy1 = dy1/l1
                    dz1 = dz1/l1

                    dx2 = x1p2 - x1p1
                    dy2 = y1p2 - y1p1
                    dz2 = 0

                    l2  = _np.sqrt(dx2**2 + dy2**2 + dz2**2)

                    dx2 = dx2/l2
                    dy2 = dy2/l2
                    dz2 = dz2/l2

                    nx = dy1 * dz2 - dz1 * dy2
                    ny = dz1 * dx2 - dx1 * dz2
                    nz = dx1 * dy2 - dy1 * dx2

                    fbody = flukaRegistry.makeBody(PLA, "B" + name + format(ibody, '02'),
                                       [nx,ny,nz],
                                       [x1p1,y1p1,z1],
                                       transform=transform,
                                       flukaregistry=flukaRegistry,
                                       comment=commentName)
                    fzone.addIntersection(fbody)
                    ibody += 1


                fbody = flukaRegistry.makeBody(PLA, "B" + name + format(ibody, '02'),
                                   [_np.cos(phi1-_np.pi/2.0), _np.sin(phi1-_np.pi/2.0), 0],
                                   [0, 0, 0],
                                   transform=transform,
                                   flukaregistry=flukaRegistry,
                                   comment=commentName)
                fzone.addIntersection(fbody)
                ibody += 1

                fbody = flukaRegistry.makeBody(PLA, "B" + name + format(ibody, '02'),
                                   [_np.cos(phi2+_np.pi/2.0), _np.sin(phi2+_np.pi/2.0), 0],
                                   [0, 0, 0],
                                   transform=transform,
                                   flukaregistry=flukaRegistry,
                                   comment=commentName)
                fzone.addIntersection(fbody)
                ibody += 1

                fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "EllipticalTube":
        uval = _Units.unit(solid.lunit)/10.

        pDx = solid.evaluateParameter(solid.pDx)*uval
        pDy = solid.evaluateParameter(solid.pDy)*uval
        pDz = solid.evaluateParameter(solid.pDz)*uval

        # main elliptical cylinder
        fbody1 = _fluka.ZEC("B"+name+"01",
                            0,0,
                            pDx,
                            pDy,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # low z cut
        fbody2 = flukaRegistry.makeBody(XYP, "B"+name+"02",-pDz/2,transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # high z cut
        fbody3 = flukaRegistry.makeBody(XYP, "B"+name+"03", pDz/2,transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)
        fzone.addSubtraction(fbody2)
        fzone.addIntersection(fbody3)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "Ellipsoid" :
        uval = _Units.unit(solid.lunit) / 10.

        xsemi = solid.evaluateParameter(solid.pxSemiAxis) * uval
        ysemi = solid.evaluateParameter(solid.pySemiAxis) * uval
        zsemi = solid.evaluateParameter(solid.pzSemiAxis) * uval
        zlow = solid.evaluateParameter(solid.pzBottomCut) * uval
        zhigh = solid.evaluateParameter(solid.pzTopCut) * uval

        cxx = xsemi**-2
        cyy = ysemi**-2
        czz = zsemi**-2

        # Main ellipsoid.  ELL can't be used as ELL is an ellipsoid of rotation.
        fbody1 = _fluka.QUA("B{}_01".format(name),
                            cxx, cyy, czz,
                            0, 0, 0, 0, 0, 0, -1,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        # Optional cuts in z to the ellipsoid.
        ellcuti = 2
        if zhigh < zsemi:
            fbody2 = flukaRegistry.makeBody(XYP, "B{}_0{}".format(name, ellcuti),
                                zhigh,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            fzone.addIntersection(fbody2)
            ellcuti += 1

        if zlow > -zsemi:
            fbody3 = flukaRegistry.makeBody(XYP, "B{}_0{}".format(name, ellcuti),
                                zlow,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            fzone.addSubtraction(fbody3)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "EllipticalCone" :

        uval = _Units.unit(solid.lunit) / 10.

        # xsemi and ysemi are unitless
        xsemi = solid.evaluateParameter(solid.pxSemiAxis)
        ysemi = solid.evaluateParameter(solid.pySemiAxis)
        zheight = solid.evaluateParameter(solid.zMax) * uval
        zcut = solid.evaluateParameter(solid.pzTopCut) * uval

        # (x/xSemiAxis)^2 + (y/ySemiAxis)^2 = (zheight - z)^2
        cxx = xsemi**-2
        cyy = ysemi**-2
        czz = -1
        cz = 2 * zheight
        c = -zheight**2

        fzone = _fluka.Zone()
        # Cone from general quadric
        fbody1 = _fluka.QUA("B{}_01".format(name),
                            cxx, cyy, czz,
                            0, 0, 0, 0, 0, cz, c,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody1)

        # Do the cuts on the infinite cone to make it finite
        zcut = min(zcut, zheight)
        fbody2 = flukaRegistry.makeBody(XYP, "B{}_02".format(name),
                            zcut,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody2)

        fbody3 = flukaRegistry.makeBody(XYP, "B{}_03".format(name),
                            -zcut,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addSubtraction(fbody3)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Paraboloid" :


        uval = _Units.unit(solid.lunit) / 10.

        halflength = solid.evaluateParameter(solid.pDz) * uval
        rlow = solid.evaluateParameter(solid.pR1) * uval
        rhigh = solid.evaluateParameter(solid.pR2) * uval

        # Equation:
        # x^2 + y^2 + bz + c = 0;

        cz = (rlow**2 - rhigh**2) / (2 * halflength)
        c = (-rhigh**2 - rlow**2) / 2

        fzone = _fluka.Zone()
        # Tip points in -ve z direction.  larger face is +ve z.
        fbody1 = _fluka.QUA("B{}_01".format(name),
                            1, 1, 0,
                            0, 0, 0, 0, 0, cz, c,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody1)
        # cut at positive z.
        fbody2 = flukaRegistry.makeBody(XYP, "B{}_02".format(name),
                            halflength,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody2)
        # cut at negative z
        fbody3 = flukaRegistry.makeBody(XYP, "B{}_03".format(name),
                            -halflength,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addSubtraction(fbody3)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Hype" :
        uvalL = _Units.unit(solid.lunit) / 10
        uvalA = _Units.unit(solid.aunit)

        outerRadius = solid.evaluateParameter(solid.outerRadius) * uvalL
        innerRadius = solid.evaluateParameter(solid.innerRadius) * uvalL
        outerStereo = solid.evaluateParameter(solid.outerStereo) * uvalA
        innerStereo = solid.evaluateParameter(solid.innerStereo) * uvalA
        lenZ =  solid.evaluateParameter(solid.lenZ) * uvalL
        # x^2 + y^2 - b^2z^2 + c = 0; r^2 = x^2+y^2.
        cOuter = -outerRadius**2
        cInner = -innerRadius**2
        czzOuter = -_np.tan(outerStereo)**2
        czzInner = -_np.tan(innerStereo)**2

        fzone = _fluka.Zone()
        # Outer QUA
        fbody1 = _fluka.QUA("B{}_01".format(name),
                            1, 1, czzOuter,
                            0, 0, 0, 0, 0, 0, cOuter,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody1)

        ihype = 2
        # Only build if it is not null
        if innerRadius != 0 or innerStereo != 0:
            # Inner QUA
            fbody2 = _fluka.QUA("B{}_0{}".format(name, ihype),
                                1, 1, czzInner,
                                0, 0, 0, 0, 0, 0, cInner,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            fzone.addSubtraction(fbody2)
            ihype += 1

        fbody3 = flukaRegistry.makeBody(XYP, "B{}_0{}".format(name, ihype),
                            lenZ / 2.0,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody3)
        ihype += 1

        fbody4 = flukaRegistry.makeBody(XYP, "B{}_0{}".format(name, ihype),
                            -lenZ / 2.0,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addSubtraction(fbody4)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Tet" :
        print('calling pycsgmesh2FlakaRegion tet')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "ExtrudedSolid":

        import pyg4ometry.gdml.Units as _Units

        luval = _Units.unit(solid.lunit)/10.0

        pZslices = solid.evaluateParameter(solid.pZslices)
        pPolygon = solid.evaluateParameter(solid.pPolygon)

        zpos     = [zslice[0]*luval for zslice in pZslices]
        x_offs   = [zslice[1][0]*luval for zslice in pZslices]
        y_offs   = [zslice[1][1]*luval for zslice in pZslices]
        scale    = [zslice[2] for zslice in pZslices]
        vertices = [[pPolygon[0]*luval, pPolygon[1]*luval] for pPolygon in pPolygon]
        nslices  = len(pZslices)

        vertices = list(reversed(vertices))
        polyListConvex = _PolygonProcessing.decomposePolygon2d(vertices)


        fregion = _fluka.Region("R"+name)

        ibody = 0
        # loop over planes
        for i in range(0,nslices-1,1):
            i1 = i
            i2 = i+1

            zi1 = zpos[i1]
            zi2 = zpos[i2]

            # build i'th and i+1'th layers
            i1PolyListConvex = []
            i2PolyListConvex = []

            for j in range(0, len(polyListConvex),1):
                i1PolyListConvex.append([[scale[i1]*vert[0]+x_offs[i1],
                                          scale[i1]*vert[1]+y_offs[i1]] for vert in polyListConvex[j]])

                i2PolyListConvex.append([[scale[i2]*vert[0]+x_offs[i2],
                                          scale[i2]*vert[1]+y_offs[i2]] for vert in polyListConvex[j]])


            # end planes
            fbody1 = flukaRegistry.makeBody(PLA, "B" + name + format(ibody, '02'),
                                [0, 0, -1],
                                [0, 0, zi1],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            ibody += 1
            fbody2 = flukaRegistry.makeBody(PLA, "B" + name + format(ibody, '02'),
                                [0, 0, 1],
                                [0, 0, zi2],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            ibody += 1

            for j in range(0,len(i1PolyListConvex),1):
                fzone = _fluka.Zone()


                fzone.addIntersection(fbody1)
                fzone.addIntersection(fbody2)

                for k in range(0,len(i1PolyListConvex[j]),1):
                    k1 = k
                    k2 = (k+1) % len(i1PolyListConvex[j])

                    x0 = i1PolyListConvex[j][k1][0]
                    y0 = i1PolyListConvex[j][k1][1]
                    z0 = zi1

                    x1 = i2PolyListConvex[j][k1][0]
                    y1 = i2PolyListConvex[j][k1][1]
                    z1 = zi2

                    x2 = i1PolyListConvex[j][k2][0]
                    y2 = i1PolyListConvex[j][k2][1]
                    z2 = zi1

                    dx1 = x1-x0
                    dy1 = y1-y0
                    dz1 = z1-z0

                    ld1 = _np.sqrt(dx1**2+dy1**2+dz1**2)

                    dx1 = dx1/ld1
                    dy1 = dy1/ld1
                    dz1 = dz1/ld1


                    dx2 = x2-x0
                    dy2 = y2-y0
                    dz2 = z2-z0

                    ld2 = _np.sqrt(dx2**2+dy2**2+dz2**2)

                    dx2 = dx2/ld2
                    dy2 = dy2/ld2
                    dz2 = dz2/ld2

                    nx = dy1*dz2 - dz1*dy2
                    ny = dx2*dz1 - dx1*dz2
                    nz = dx1*dy2 - dy1*dy2

                    fbody = flukaRegistry.makeBody(PLA, "B" + name + format(ibody, '02'),
                                       [-nx,-ny,-nz],
                                       [x0,y0,z0],
                                       transform=transform,
                                       flukaregistry=flukaRegistry,
                                       comment=commentName)
                    ibody += 1
                    fzone.addIntersection(fbody)
                fregion.addZone(fzone)


        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedBox":
        print('calling pycsgmesh2FlakaRegion TwistedBox')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedTrap":
        print('calling pycsgmesh2FlakaRegion TwistedTrap')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedTrd":
        print('calling pycsgmesh2FlakaRegion TwistedTrd')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedTubs":
        print('calling pycsgmesh2FlakaRegion TwistedTubs')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "GenericTrap":
        print('calling pycsgmesh2FlakaRegion GenericTrap')
        fregion = pycsgmesh2FlukaRegion(solid.mesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "Union":
        # build both solids to regions
        # take zones from 2 and add as zones to 1

        bsrot = solid.tra2[0].eval()
        bspos = solid.tra2[1].eval()

        bsmtra = _transformation.tbxyz2matrix(bsrot)
        bstra  = bspos

        solid1 = solid.obj1
        solid2 = solid.obj2

        new_mtra = mtra * bsmtra
        new_tra  = (_np.array(mtra.dot(bstra)) + tra)[0]

        r1,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid1,mtra , tra ,flukaRegistry,False,commentName=commentName)
        r2,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid2,new_mtra, new_tra,flukaRegistry,False,commentName=commentName)

        if 0 :
            print("-------------------------")
            print("Union")
            print(solid.obj1.name, solid.obj2.name)
            print(solid.obj1.type, solid.obj2.type)
            print(type(r1), type(r2))
            print(r1.flukaFreeString())
            print(r2.flukaFreeString())

        fregion = _fluka.Region("R"+name)

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
        bstra  = bspos

        solid1 = solid.obj1
        solid2 = solid.obj2

        new_mtra = mtra * bsmtra
        new_tra  = (_np.array(mtra.dot(bstra)) + tra)[0]

        r1,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid1,mtra , tra ,flukaRegistry,False,commentName=commentName)
        r2,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid2,new_mtra, new_tra,flukaRegistry,False,commentName=commentName)

        if 0 :
            print("-------------------------")
            print("Subtraction")
            print(solid.obj1.name, solid.obj2.name)
            print(solid.obj1.type, solid.obj2.type)
            print(type(r1), type(r2))
            print(r1.flukaFreeString())
            print(r2.flukaFreeString())

        fregion = _fluka.Region("R"+name)

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
        bstra  = bspos

        solid1 = solid.obj1
        solid2 = solid.obj2

        new_mtra = mtra * bsmtra
        new_tra  = (_np.array(mtra.dot(bstra)) + tra)[0]

        r1,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid1,mtra , tra ,flukaRegistry,False,commentName=commentName)
        r2,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid2,new_mtra, new_tra,flukaRegistry,False,commentName=commentName)

        if 0 :
            print("-------------------------")
            print("Intersection")
            print(solid.obj1.name, solid.obj2.name)
            print(solid.obj1.type, solid.obj2.type)
            print(type(r1), type(r2))
            print(r1.flukaFreeString())
            print(r2.flukaFreeString())

        fregion = _fluka.Region("R"+name)

        for zone1 in r1.zones:
            for zone2 in r2.zones:
                zone1.addIntersection(zone2)
            fregion.addZone(zone1)

    else :
        fregion = _fluka.Region("R"+name)
        print(solid.type)

    # print solid.name, name, solid.type, len(fregion.zones)

    return fregion, flukaNameCount


def geant4MaterialDict2Fluka(matr, freg):

    for material in matr.items() :
        if isinstance(material[1], _geant4.Material) :
            geant4Material2Fluka(material[1], freg)

    return freg

def geant4Material2Fluka(material, freg, suggestedDensity=None, elementSuffix=False) :
    materialName = material.name
    materialInstance = material

    materialNameStrip = makeStripName(materialName)

    # ensure this name is unique
    i = 0
    while materialNameStrip in freg.materials:
        if i == 0:
            materialNameStrip += str(i)
        else:
            materialNameStrip[-1] = str(i)
    materialNameShort = makeShortName(materialNameStrip)

    # protect against multiply defining the same material
    if materialNameShort in freg.materials:
        return freg.materials[materialNameShort]

    # Only want to use materials (FLUKA COMPOUND or MATERIAL)
    if isinstance(materialInstance, _geant4.Material):
        # none, nist, arbitrary, simple, composite
        if materialInstance.type == "none":
            raise Exception("Cannot have material with none type")

        elif materialInstance.type == "nist":
            # make material object from dictionary of information
            nistMatInstance = _geant4.nist_material_2geant4Material(materialInstance.name)
            nistMatInstance.type = "composite" # prevent recursion - Material internally decides if it's a nist material or not
            return geant4Material2Fluka(nistMatInstance, freg)

        elif materialInstance.type == "arbitrary":
            raise Exception("Cannot have material with arbitrary type")

        elif materialInstance.type == "simple":
            fe = _fluka.Material(materialNameShort,
                                 materialInstance.atomic_number,
                                 materialInstance.density,
                                 flukaregistry=freg)
            return fe

        elif materialInstance.type == "composite":
            flukaComposition = []
            flukaFractionType = "atomic"

            for comp in materialInstance.components:
                fm = geant4Material2Fluka(comp[0], freg, materialInstance.density, elementSuffix=True)

                compFraction     = comp[1]
                compFractionType = comp[2]

                if compFractionType == "natoms" :
                    flukaFractionType = "atomic"
                elif compFractionType == "massfraction" :
                    flukaFractionType = "mass"

                flukaComposition.append((fm,compFraction))

            mat = _fluka.Compound(materialNameShort,
                                  materialInstance.density,
                                  flukaComposition,
                                  fractionType=flukaFractionType,
                                  flukaregistry=freg)
            return mat

    elif isinstance(materialInstance, _geant4.Element) :
        if elementSuffix:
            if len(materialNameShort) >= 6:
                materialNameShort = materialNameShort[:6] + "EL"
            else:
                materialNameShort += "EL"
        # check again as we've just changed our short name
        if materialNameShort in freg.materials:
            return freg.materials[materialNameShort]
        if materialInstance.type == "element-simple" :
            mat = _fluka.Material(materialNameShort,
                                  materialInstance.Z,
                                  suggestedDensity,
                                  materialInstance.A,
                                  flukaregistry=freg)
            return mat

        elif materialInstance.type == "element-composite" :
            flukaComponentNames     = []
            flukaComponents         = []
            flukaComponentFractions = []

            for iso in materialInstance.components :
                fi = geant4Material2Fluka(iso[0], freg)

                compFlukaName = makeShortName(iso[0].name)
                compFraction  = iso[1]

                flukaComponentNames.append(compFlukaName)
                flukaComponents.append(fi)
                flukaComponentFractions.append(compFraction)

            flukaComposition = [(c,f) for c,f in zip(flukaComponents, flukaComponentFractions)]

            mat = _fluka.Compound(materialNameShort,
                                  0.1 ,
                                  flukaComposition,
                                  fractionType="atomic",
                                  flukaregistry=freg)
            return mat

    elif isinstance(materialInstance, _geant4.Isotope) :
        fi = _fluka.Material(materialNameShort, materialInstance.Z, 10, flukaregistry=freg,
                            atomicMass = materialInstance.a,
                            massNumber = materialInstance.N,)
        return fi
    else:
        raise TypeError("Unknown material.type \""+str(material.type)+"\"")

def pycsgmesh2FlukaRegion(mesh, name, transform, flukaRegistry, commentName) :

    polyhedron = _pycgal.Polyhedron_3.Polyhedron_3_EPECK()
    _pycgal.CGAL.copy_face_graph(mesh.sm, polyhedron)
    nef = _pycgal.Nef_polyhedron_3.Nef_polyhedron_3_EPECK(polyhedron)
    convex_polyhedra = _pycgal.PolyhedronProcessing.nefPolyhedron_to_convexPolyhedra(nef)

    fregion = _fluka.Region("R" + name)

    ibody = 0

    for convex_polyhedron in convex_polyhedra :

        planes = _pycgal.PolyhedronProcessing.polyhedron_to_numpyArrayPlanes(convex_polyhedron)

        fzone = _fluka.Zone()

        for plane in planes :
            fbody = flukaRegistry.makeBody(PLA, "B" + name +format(ibody,'02'),
                               -plane[3:]/_np.sqrt((plane[3:]**2).sum()),
                               plane[0:3]/10.0,
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)
            fzone.addSubtraction(fbody)
            ibody += 1

        fregion.addZone(fzone)

    return fregion

def makeStripName(mn) :
    if mn.find("0x") != -1:
        mnStrip = mn[0:mn.find("0x")]
    else:
        mnStrip = mn
    return mnStrip

def makeShortName(mn):
    mn = makeStripName(mn)
    if len(mn) > 8:
        mn = mn.replace('_','') # first, remove '_'
        if len(mn) > 8:
            return mn[:8]
        else:
            return mn
    else:
        return mn
