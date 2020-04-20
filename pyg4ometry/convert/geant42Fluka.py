import pyg4ometry.transformation as _transformation
import pyg4ometry.fluka as _fluka
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
import numpy as _np
import copy as _copy

def geant4Logical2Fluka(logicalVolume) :
    mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]])
    tra  = _np.array([0,0,0])

    flukaRegistry = _fluka.FlukaRegistry()

    flukaNameCount = 0

    # find extent of logical
    extent = logicalVolume.extent(includeBoundingSolid = True)

    #position = [(extent[1][0] - extent[0][0])/2,
    #              (extent[1][1] - extent[0][1])/2,
    #              (extent[1][2] - extent[0][2])/2]
    # create black body body

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
    flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,logicalVolume.solid,mtra,tra,
                                                                     flukaRegistry, commentName=logicalVolume.name)
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


    # create black body region
    fregion = _fluka.Region("BLKHOLE")
    fregion.addZone(fzone)
    flukaRegistry.addRegion(fregion)

    flukaRegistry.addRegion(flukaMotherRegion)

    return flukaRegistry

def geant4PhysicalVolume2Fluka(physicalVolume,
                               mtra=_np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                               tra=_np.array([0, 0, 0]),
                               flukaRegistry=None,flukaNameCount=0) :

    # logical volume (outer and complete)
    geant4LvOuterSolid = physicalVolume.logicalVolume.solid
    # print 'g2fPhysicalVolume',physicalVolume.name, flukaName, flukaNameCount, rotation, position, scale
    flukaMotherOuterRegion, flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,
                                                                     geant4LvOuterSolid,
                                                                     mtra,tra,
                                                                     flukaRegistry,
                                                                     commentName=physicalVolume.name)

    flukaMotherRegion      = _copy.deepcopy(flukaMotherOuterRegion)
    flukaMotherRegion.comment = physicalVolume.name

    # loop over daughers and remove from mother region
    for dv in physicalVolume.logicalVolume.daughterVolumes :

        # placement information for daughter
        pvmrot = _transformation.tbzyx2matrix(-_np.array(dv.rotation.eval()))
        pvtra  = _np.array(dv.position.eval())

        new_mtra = mtra * pvmrot
        new_tra  = (_np.array(mtra.dot(pvtra)) + tra)[0]

        flukaDaughterOuterRegion, flukaNameCount = geant4PhysicalVolume2Fluka(dv,new_mtra,new_tra,
                                                                              flukaRegistry=flukaRegistry,
                                                                              flukaNameCount=flukaNameCount)

        for motherZones in flukaMotherRegion.zones:
            for daughterZones in flukaDaughterOuterRegion.zones:
                motherZones.addSubtraction(daughterZones)

    flukaRegistry.addRegion(flukaMotherRegion)

    return flukaMotherOuterRegion, flukaNameCount

def geant4Solid2FlukaRegion(flukaNameCount,solid, mtra=_np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                            tra=_np.array([0, 0, 0]), flukaRegistry = None, addRegistry = True, commentName = "") :

    import pyg4ometry.gdml.Units as _Units  # TODO move circular import

    name = format(flukaNameCount,'04')

    fregion = None
    fbodies = []

    rotation = _transformation.matrix2tbxyz(mtra)
    position = tra

    transform= _rotoTranslationFromTra2("T"+name,[rotation,tra],flukaregistry=flukaRegistry)

    commentName = commentName + " " + solid.name

    # print 'geant4Solid2FlukaRegion',flukaNameCount,name,solid.type, rotation,position,transform

    if solid.type == 'Box' :
        uval = _Units.unit(solid.lunit)/10.
        pX = solid.evaluateParameter(solid.pX)*uval/2.0
        pY = solid.evaluateParameter(solid.pY)*uval/2.0
        pZ = solid.evaluateParameter(solid.pZ)*uval/2.0

        fbody = _fluka.RPP("B"+name+'_01', -pX, pX, -pY, pY, -pZ, pZ,
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
        fbody1 = _fluka.ZCC("B"+name+"_01",0,0,pRMax,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # low z cut
        fbody2 = _fluka.XYP("B"+name+"_02",-pDz/2,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # high z cut
        fbody3 = _fluka.XYP("B"+name+"_03", pDz/2,transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # inner cylinder
        if pRMin != 0 :
            fbody4 = _fluka.ZCC("B"+name+"_04",0,0,pRMin,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody5 = _fluka.PLA("B"+name+"_05",
                                [_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody6 = _fluka.PLA("B"+name+"_06",
                                [_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
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
            fzone1 = _fluka.Zone()
            fzone1.addIntersection(fbody5)
            fzone1.addIntersection(fbody6)
            fzone.addSubtraction(fzone1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

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
        fbody1 = _fluka.ZCC("B"+name+"_01",0,0,pRMax,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # low z cut
        fbody2 = _fluka.PLA("B"+name+"_02",
                            [-pLowNorm0,-pLowNorm1,-pLowNorm2],
                            [0, 0, -pDz/2],
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # high z cut
        fbody3 = _fluka.PLA("B"+name+"_03",
                            [pHighNorm0,pHighNorm1,pHighNorm2],
                            [0, 0, pDz/2.],
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        if pRMin != 0 :
            # inner cylinder
            fbody4 = _fluka.ZCC("B"+name+"_04",0,0,pRMin,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody5 = _fluka.PLA("B"+name+"_05",
                                [_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody6 = _fluka.PLA("B"+name+"_06",
                                [_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
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
            fzone1 = _fluka.Zone()
            fzone1.addIntersection(fbody5)
            fzone1.addIntersection(fbody6)
            fzone.addSubtraction(fzone1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

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
        base   = _np.array(position)-dir/2.0

        fbody1 = _fluka.TRC("B"+name+"_01",base,dir,pRmax1,pRmax2,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        if pRmin1 != 0 and pRmin2 != 0 :
            fbody2 = _fluka.TRC("B" + name + "_02",
                                base, dir, pRmin1, pRmin2,
                                transform=transform,
                                flukaregistry=flukaRegistry)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody3 = _fluka.PLA("B"+name+"_05",
                                [_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody4 = _fluka.PLA("B"+name+"_06",
                                [_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)


        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        if pRmin1 != 0 and pRmin2 != 0 :
            fzone.addSubtraction(fbody2)

        if pDPhi != 2*_np.pi :
            fzone1 = _fluka.Zone()
            fzone1.addIntersection(fbody3)
            fzone1.addIntersection(fbody4)
            fzone.addSubtraction(fzone1)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Para" :
        luval = _Units.unit(solid.lunit)/10.0
        auval = _Units.unit(solid.aunit)

        pX     = solid.evaluateParameter(solid.pX)*luval
        pY     = solid.evaluateParameter(solid.pY)*luval
        pZ     = solid.evaluateParameter(solid.pZ)*luval
        pAlpha = solid.evaluateParameter(solid.pAlpha)*auval
        pTheta = solid.evaluateParameter(solid.pTheta)*auval
        pPhi   = solid.evaluateParameter(solid.pPhi)*auval

        mTheta = _transformation.tbxyz2matrix([0,-pTheta,0])
        mAlpha = _transformation.tbxyz2matrix([0,0,-pAlpha])
        n1     = mAlpha.dot(mTheta).dot(_np.array([-1,0,0]))
        n2     = mAlpha.dot(mTheta).dot(_np.array([1,0,0]))
        fbody1 = _fluka.PLA("B"+name+"_01",n1,[-pX,0,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody2 = _fluka.PLA("B"+name+"_02",n2,[pX,0,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody3 = _fluka.PLA("B"+name+"_03",[0,-_np.cos(pPhi),_np.sin(pPhi)],[0,-pY,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody4 = _fluka.PLA("B"+name+"_04",[0,_np.cos(pPhi),-_np.sin(pPhi)],[0,pY,0],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody5 = _fluka.PLA("B"+name+"_05",[0,0,-1],[0,0,-pZ],
                            transform=transform,flukaregistry=flukaRegistry,
                            comment=commentName)
        fbody6 = _fluka.PLA("B"+name+"_06",[0,0,1],[0,0,pZ],
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

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Trd" :
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Trap" :
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

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

        fbody1  = _fluka.SPH("B"+name+"_01", position, pRmax,
                             transform=transform,
                             flukaregistry=flukaRegistry,
                             comment=commentName)

        if pRmin != 0 :
            fbody2 = _fluka.SPH("B"+name+"_02", position, pRmin,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody3 = _fluka.PLA("B"+name+"_03",
                                [_np.cos(pSPhi+3./2*_np.pi),_np.sin(pSPhi+3./2*_np.pi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            fbody4 = _fluka.PLA("B"+name+"_04",
                                [_np.cos(pSPhi+pDPhi+3./2*_np.pi),_np.sin(pSPhi+pDPhi+3./2*_np.pi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
        pTheta1 = pSTheta
        pTheta2 = pSTheta+pDTheta

        if pTheta1 != 0 :
            if pTheta1 < _np.pi/2.0 :
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC("B"+name+"_05",
                                    [0,0,pRmax],
                                    [0,0,-pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

            elif pTheta1 > _np.pi/2.0 :
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC("B"+name+"_05",
                                    [0,0,-pRmax],
                                    [0,0,pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)
            else :
                fbody5 = _fluka.XYP("B"+name+"_05",0,
                                    transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

        if pTheta2 != _np.pi:
            if pTheta2 < _np.pi/2.0 :
                r = abs(_np.tan(pTheta2) * pRmax)

                fbody6 = _fluka.TRC("B"+name+"_06",
                                    [0,0,pRmax],
                                    [0,0,-pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

            elif pTheta2 > _np.pi/2.0 :
                r = abs(_np.tan(pTheta2) * pRmax)
                fbody6 = _fluka.TRC("B"+name+"_06",
                                    [0,0,-pRmax],
                                    [0,0,pRmax],
                                    r,0,transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)
            else :
                fbody6 = _fluka.XYP("B"+name+"_06",0,
                                    transform=transform,
                                    flukaregistry=flukaRegistry,
                                    comment=commentName)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        if pRmin != 0 :
            fzone.addSubtraction(fbody2)

        if pDPhi != 2*_np.pi :
            fzone1 = _fluka.Zone()
            fzone1.addSubtraction(fbody3)
            fzone1.addIntersection(fbody4)
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

        fbody1  = _fluka.SPH("B"+name+"_01", position, pRmax,
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

            body1 = _fluka.RCC("B"+name+"_"+format(4*i,'02'),
                               [x1,y1,z1],
                               [2*nx1,2*ny1,2*nz1],
                               pRmax,
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)
            body2 = _fluka.PLA("B"+name+"_"+format(4*i+1,'02'),
                               [nx0, ny0, nz0],
                               [x0,y0,z0],
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)

            body3 = _fluka.PLA("B"+name+"_"+format(4*i+2,'02'),
                               [nx2, ny2, nz2],
                               [x2,y2,z2],
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)

            if pRmin != 0 :
                body4 = _fluka.RCC("B" + name + "_" + format(4 * i + 3, '02'),
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

    elif solid.type == "Polycone":
        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        luval = _Units.unit(solid.lunit)
        auval = _Units.unit(solid.aunit)

        pSPhi = solid.evaluateParameter(solid.pSPhi) * auval
        pDPhi = solid.evaluateParameter(solid.pDPhi) * auval

        print pSPhi, pDPhi
        pZpl = [val * luval/10. for val in solid.evaluateParameter(solid.pZpl)]
        pRMin = [val * luval/10. for val in solid.evaluateParameter(solid.pRMin)]
        pRMax = [val * luval/10. for val in solid.evaluateParameter(solid.pRMax)]

        # create region
        fregion = _fluka.Region("R" + name)

        # number of z planes
        nslices = len(pZpl)

        ibody = 1

        if pDPhi != 2*_np.pi :
            fbody1 = _fluka.PLA("B"+name+"_"+format(ibody,'02'),
                                [_np.cos(pSPhi-_np.pi/2),_np.sin(pSPhi-_np.pi/2),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            ibody += 1

            fbody2 = _fluka.PLA("B"+name+"_"+format(ibody,'02'),
                                [_np.cos(pSPhi+pDPhi+_np.pi/2),_np.sin(pSPhi+pDPhi+_np.pi/2),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)

            ibody += 1


        for islice1 in range(0,nslices-1,1) :
            islice2 = islice1+1

            base = [0,0,pZpl[islice1]]
            dir  = [0,0,pZpl[islice2]-pZpl[islice1]]

            pRMax1 = pRMax[islice1]
            pRMax2 = pRMax[islice2]

            pRMin1 = pRMin[islice1]
            pRMin2 = pRMin[islice2]

            trc1 = _fluka.TRC("B"+name+"_"+format(ibody,'02'),
                              base,dir,pRMax1,pRMax2,
                              transform=transform,
                              flukaregistry=flukaRegistry,
                              comment=commentName)
            ibody += 1

            trc2 = _fluka.TRC("B"+name+"_"+format(ibody,'02'),
                              base,dir,pRMin1,pRMin2,
                              transform=transform,
                              flukaregistry=flukaRegistry,
                              comment=commentName)
            ibody += 1

            # phi cuts planes

            fzone1 = _fluka.Zone()
            fzone1.addIntersection(trc1)
            fzone1.addSubtraction(trc2)

            # cut phi
            if pDPhi != 2 * _np.pi:
                fzone2 = _fluka.Zone()
                if pDPhi < _np.pi :
                    fzone2.addIntersection(fbody1)
                    fzone2.addIntersection(fbody2)
                    fzone1.addIntersection(fzone2)
                else :
                    fzone2.addSubtraction(fbody1)
                    fzone2.addSubtraction(fbody2)
                    fzone1.addSubtraction(fzone2)

            fregion.addZone(fzone1)

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        # increment name count
        flukaNameCount += 1

    elif solid.type == "GenericPolycone" :

        # fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "Polyhedra" :

        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "GenericPolyhedra" :

        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)

        flukaNameCount += 1

    elif solid.type == "EllipticalTube":
        uval = _Units.unit(solid.lunit)/10.

        pDx = solid.evaluateParameter(solid.pDx)*uval
        pDy = solid.evaluateParameter(solid.pDy)*uval
        pDz = solid.evaluateParameter(solid.pDz)*uval

        # main elliptical cylinder
        fbody1 = _fluka.ZEC("B"+name+"_01",
                            0,0,
                            pDx,
                            pDy,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # low z cut
        fbody2 = _fluka.XYP("B"+name+"_02",-pDz/2,transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)

        # high z cut
        fbody3 = _fluka.XYP("B"+name+"_03", pDz/2,transform=transform,
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
            fbody2 = _fluka.XYP("B{}_0{}".format(name, ellcuti),
                                zhigh,
                                transform=transform,
                                flukaregistry=flukaRegistry,
                                comment=commentName)
            fzone.addIntersection(fbody2)
            ellcuti += 1

        if zlow > -zsemi:
            fbody3 = _fluka.XYP("B{}_0{}".format(name, ellcuti),
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
        fbody2 = _fluka.XYP("B{}_02".format(name),
                            zcut,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody2)

        fbody3 = _fluka.XYP("B{}_03".format(name),
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
        fbody2 = _fluka.XYP("B{}_02".format(name),
                            halflength,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addIntersection(fbody2)
        # cut at negative z
        fbody3 = _fluka.XYP("B{}_03".format(name),
                            -halflength,
                            transform=transform,
                            flukaregistry=flukaRegistry,
                            comment=commentName)
        fzone.addSubtraction(fbody3)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    elif solid.type == "Hype" :
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "Tet" :
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "ExtrudedSolid":
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedBox":
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedTrap":
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedTrd":
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "TwistedTubs":
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
        flukaNameCount += 1

    elif solid.type == "GenericTrap":
        fregion = pycsgmesh2FlukaRegion(solid.pycsgmesh(), name,transform, flukaRegistry,commentName)
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
            print "-------------------------"
            print "Union"
            print solid.obj1.name, solid.obj2.name
            print solid.obj1.type, solid.obj2.type
            print type(r1), type(r2)
            print r1.flukaFreeString()
            print r2.flukaFreeString()

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
            print "-------------------------"
            print "Subtraction"
            print solid.obj1.name, solid.obj2.name
            print solid.obj1.type, solid.obj2.type
            print type(r1), type(r2)
            print r1.flukaFreeString()
            print r2.flukaFreeString()

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
            print "-------------------------"
            print "Intersection"
            print solid.obj1.name, solid.obj2.name
            print solid.obj1.type, solid.obj2.type
            print type(r1), type(r2)
            print r1.flukaFreeString()
            print r2.flukaFreeString()

        fregion = _fluka.Region("R"+name)

        for zone1 in r1.zones:
            for zone2 in r2.zones:
                zone1.addIntersection(zone2)
            fregion.addZone(zone1)

    else :
        print solid.type

    return fregion, flukaNameCount


def geant4Material2FlukaMaterial(g4registry = None) :
    for material in g4registry.materialDict.items() :
        materialName      = material[0]
        if materialName.find("0x") != -1 :
            materialNameStrip = materialName[0:materialName.find("0x")]
        else :
            materialNameStrip = materialName
        materialInstance  = material[1]

        print materialName, materialNameStrip, materialInstance,\
            materialInstance.density,materialInstance.atomic_number, \
            materialInstance.atomic_weight,materialInstance.number_of_components

        if materialInstance.number_of_components == 0 :
            pass
        else :
            pass

def pycsgmesh2FlukaRegion(mesh, name, transform, flukaRegistry, commentName) :
    import pyg4ometry.pycgal as pycgal
    import ctypes as ctypes

    nef = pycgal.pycsgmesh2NefPolyhedron(mesh)

    nconvex = ctypes.c_int(0)
    vpArray = ctypes.c_void_p*10000;
    polyhedra = vpArray()

    pycgal.nefpolyhedron_to_convexpolyhedra(nef,polyhedra,ctypes.byref(nconvex))

    print 'pycsgmesh2FlukaRegion> nconvex=',nconvex.value

    fregion = _fluka.Region("R" + name)

    ibody = 0

    for i in range(0,nconvex.value,1) :

        nplanes = ctypes.c_int(0)

        planes = _np.zeros((1000, 6))
        planespp = (planes.__array_interface__['data'][0] +
                   _np.arange(planes.shape[0]) * planes.strides[0]).astype(_np.uintp)

        pycgal.convexpolyhedron_to_planes(polyhedra[i], ctypes.byref(nplanes), planespp)

        print 'pycsgmesh2FlukaRegion> iconvex=',i,polyhedra[i],nplanes.value

        fzone = _fluka.Zone()

        for j in range(0,nplanes.value) :
            fbody = _fluka.PLA("B" + name + "_"+str(ibody),
                              -planes[j][3:],
                               planes[j][0:3]/10.0,
                               transform=transform,
                               flukaregistry=flukaRegistry,
                               comment=commentName)
            fzone.addSubtraction(fbody)
            ibody += 1

        fregion.addZone(fzone)

    return fregion
