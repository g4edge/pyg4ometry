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
                                                                     flukaRegistry)
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
                                                                     flukaRegistry)

    flukaMotherRegion      = _copy.deepcopy(flukaMotherOuterRegion)

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
                            tra=_np.array([0, 0, 0]), flukaRegistry = None, addRegistry = True) :

    import pyg4ometry.gdml.Units as _Units  # TODO move circular import

    name = format(flukaNameCount,'04')

    fregion = None
    fbodies = []

    rotation = _transformation.matrix2tbxyz(mtra)
    position = tra

    transform= _rotoTranslationFromTra2("T"+name,[rotation,tra],flukaregistry=flukaRegistry)


    # print 'geant4Solid2FlukaRegion',flukaNameCount,name,solid.type, rotation,position,transform

    if solid.type == 'Box' :
        uval = _Units.unit(solid.lunit)/10.
        pX = solid.evaluateParameter(solid.pX)*uval/2
        pY = solid.evaluateParameter(solid.pY)*uval/2
        pZ = solid.evaluateParameter(solid.pZ)*uval/2.0

        fbody = _fluka.RPP("B"+name+'_01', -pX, pX, -pY, pY, -pZ, pZ,
                           transform=transform,
                           flukaregistry=flukaRegistry,
                           addRegistry=True)

        # store all bodies
        fbodies.append(fbody)

        # create zones and region
        fzone = _fluka.Zone()
        fzone.addIntersection(fbody)
        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

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
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.XYP("B"+name+"_02",-pDz/2,
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.XYP("B"+name+"_03", pDz/2,transform=transform,
                            flukaregistry=flukaRegistry)

        # inner cylinder
        if pRMin != 0 :
            fbody4 = _fluka.ZCC("B"+name+"_04",0,0,pRMin,
                                transform=transform,
                                flukaregistry=flukaRegistry)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody5 = _fluka.PLA("B"+name+"_05",
                                [_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)

            fbody6 = _fluka.PLA("B"+name+"_06",
                                [_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)


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
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.PLA("B"+name+"_02",
                            [-pLowNorm0,-pLowNorm1,-pLowNorm2],
                            [0, 0, -pDz/2],
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.PLA("B"+name+"_03",
                            [pHighNorm0,pHighNorm1,pHighNorm2],
                            [0, 0, pDz/2.],
                            transform=transform,
                            flukaregistry=flukaRegistry)

        if pRMin != 0 :
            # inner cylinder
            fbody4 = _fluka.ZCC("B"+name+"_04",0,0,pRMin,
                                transform=transform,
                                flukaregistry=flukaRegistry)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody5 = _fluka.PLA("B"+name+"_05",
                                [_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)

            fbody6 = _fluka.PLA("B"+name+"_06",
                                [_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)

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

        fbody1 = _fluka.TRC("B"+name+"_01",base,dir,pRmax1,pRmax2,transform=transform,flukaregistry=flukaRegistry)

        if pRmin1 != 0 and pRmin2 != 0 :
            fbody2 = _fluka.TRC("B" + name + "_02", base, dir, pRmin1, pRmin2, transform=transform,
                                flukaregistry=flukaRegistry)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody3 = _fluka.PLA("B"+name+"_05",
                                [_np.sin(pSPhi),_np.cos(pSPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)

            fbody4 = _fluka.PLA("B"+name+"_06",
                                [_np.sin(pSPhi+pDPhi),_np.cos(pSPhi+pDPhi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)


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
                            transform=transform,flukaregistry=flukaRegistry)
        fbody2 = _fluka.PLA("B"+name+"_02",n2,[pX,0,0],
                            transform=transform,flukaregistry=flukaRegistry)

        fbody3 = _fluka.PLA("B"+name+"_03",[0,-_np.cos(pPhi),_np.sin(pPhi)],[0,-pY,0],
                            transform=transform,flukaregistry=flukaRegistry)
        fbody4 = _fluka.PLA("B"+name+"_04",[0,_np.cos(pPhi),-_np.sin(pPhi)],[0,pY,0],
                            transform=transform,flukaregistry=flukaRegistry)

        fbody5 = _fluka.PLA("B"+name+"_05",[0,0,-1],[0,0,-pZ],
                            transform=transform,flukaregistry=flukaRegistry)
        fbody6 = _fluka.PLA("B"+name+"_06",[0,0,1],[0,0,pZ],
                            transform=transform,flukaregistry=flukaRegistry)

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


    elif solid.type == "Sphere" :

        luval = _Units.unit(solid.lunit)/10.0
        auval = _Units.unit(solid.aunit)

        pRmin   = solid.evaluateParameter(solid.pRmin)*luval
        pRmax   = solid.evaluateParameter(solid.pRmax)*luval
        pSPhi   = solid.evaluateParameter(solid.pSPhi)*auval
        pDPhi   = solid.evaluateParameter(solid.pDPhi)*auval
        pSTheta = solid.evaluateParameter(solid.pSTheta)*auval
        pDTheta = solid.evaluateParameter(solid.pDTheta)*auval

        fbody1  = _fluka.SPH("B"+name+"_01", position, pRmax,transform=transform,flukaregistry=flukaRegistry)

        if pRmin != 0 :
            fbody2 = _fluka.SPH("B"+name+"_02", position, pRmin,transform=transform,flukaregistry=flukaRegistry)

        # phi cuts
        if pDPhi != 2*_np.pi :
            fbody3 = _fluka.PLA("B"+name+"_03",
                                [_np.cos(pSPhi+3./2*_np.pi),_np.sin(pSPhi+3./2*_np.pi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)

            fbody4 = _fluka.PLA("B"+name+"_04",
                                [_np.cos(pSPhi+pDPhi+3./2*_np.pi),_np.sin(pSPhi+pDPhi+3./2*_np.pi),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)
        pTheta1 = pSTheta
        pTheta2 = pSTheta+pDTheta

        if pTheta1 != 0 :
            if pTheta1 < _np.pi/2.0 :
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC("B"+name+"_05",
                                    [0,0,pRmax],
                                    [0,0,-pRmax],
                                    r,0,transform=transform,flukaregistry=flukaRegistry)

            elif pTheta1 > _np.pi/2.0 :
                r = _np.tan(pTheta1) * pRmax

                fbody5 = _fluka.TRC("B"+name+"_05",
                                    [0,0,-pRmax],
                                    [0,0,pRmax],
                                    r,0,transform=transform,flukaregistry=flukaRegistry)
            else :
                fbody5 = _fluka.XYP("B"+name+"_05",0,
                                    transform=transform,
                                    flukaregistry=flukaRegistry)

        if pTheta2 != _np.pi:
            if pTheta2 < _np.pi/2.0 :
                r = abs(_np.tan(pTheta2) * pRmax)

                fbody6 = _fluka.TRC("B"+name+"_06",
                                    [0,0,pRmax],
                                    [0,0,-pRmax],
                                    r,0,transform=transform,flukaregistry=flukaRegistry)

            elif pTheta2 > _np.pi/2.0 :
                r = abs(_np.tan(pTheta2) * pRmax)
                fbody6 = _fluka.TRC("B"+name+"_06",
                                    [0,0,-pRmax],
                                    [0,0,pRmax],
                                    r,0,transform=transform,flukaregistry=flukaRegistry)
            else :
                fbody6 = _fluka.XYP("B"+name+"_06",0,
                                    transform=transform,
                                    flukaregistry=flukaRegistry)

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

        fbody1  = _fluka.SPH("B"+name+"_01", position, pRmax,transform=transform,flukaregistry=flukaRegistry)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)

        fregion = _fluka.Region("R"+name)
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
                                flukaregistry=flukaRegistry)

            ibody += 1

            fbody2 = _fluka.PLA("B"+name+"_"+format(ibody,'02'),
                                [_np.cos(pSPhi+pDPhi+_np.pi/2),_np.sin(pSPhi+pDPhi+_np.pi/2),0],
                                [0, 0, 0],
                                transform=transform,
                                flukaregistry=flukaRegistry)

            ibody += 1


        for islice1 in range(0,nslices-1,1) :
            islice2 = islice1+1

            base = [0,0,pZpl[islice1]]
            dir  = [0,0,pZpl[islice2]-pZpl[islice1]]

            pRMax1 = pRMax[islice1]
            pRMax2 = pRMax[islice2]

            pRMin1 = pRMin[islice1]
            pRMin2 = pRMin[islice2]

            trc1 = _fluka.TRC("B"+name+"_"+format(ibody,'02'),base,dir,pRMax1,pRMax2,
                              transform=transform,flukaregistry=flukaRegistry)
            ibody += 1

            trc2 = _fluka.TRC("B"+name+"_"+format(ibody,'02'),base,dir,pRMin1,pRMin2,
                              transform=transform,flukaregistry=flukaRegistry)
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

        # increment name count
        flukaNameCount += 1

    elif solid.type == "GenericPolycone" :
        pass
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
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.XYP("B"+name+"_02",-pDz/2,transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.XYP("B"+name+"_03", pDz/2,transform=transform,
                            flukaregistry=flukaRegistry)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)
        fzone.addSubtraction(fbody2)
        fzone.addIntersection(fbody3)

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)

        flukaNameCount += 1

    #elif solid.type == "EllipticalCone" :
    #    pass

    elif solid.type == "ExtrudedSolid":

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(solid.lunit)

        pZslices = solid.evaluateParameter(solid.pZslices)
        pPolygon = solid.evaluateParameter(solid.pPolygon)

        zpos     = [zslice[0]*luval/10. for zslice in pZslices]
        x_offs   = [zslice[1][0]*luval/10. for zslice in pZslices]
        y_offs   = [zslice[1][1]*luval/10. for zslice in pZslices]
        scale    = [zslice[2] for zslice in pZslices]
        vertices = [[pPolygon[0]*luval/10., pPolygon[1]*luval/10.] for pPolygon in pPolygon]
        nslices  = len(pZslices)

        avertices = _np.array(vertices)
        ax_offs   = _np.array(x_offs)
        ay_offs   = _np.array(y_offs)
        ascale    = _np.array(scale)

        #print "---------"
        #print avertices
        #print ax_offs
        #print ay_offs
        #print ascale
        #print "---------"

        # create region
        fregion = _fluka.Region("R" + name)

        ibody = 1

        # loop over slices
        for islice1 in range(0,nslices-1,1) :
            islice2 = islice1+1

            polygon1 = avertices*ascale[islice1] + _np.array([ax_offs[islice1],ay_offs[islice1]])
            polygon2 = avertices*ascale[islice2] + _np.array([ax_offs[islice2],ay_offs[islice2]])

            polygon1 = _np.insert(polygon1,2,values=zpos[islice1],axis=1)
            polygon2 = _np.insert(polygon2,2,values=zpos[islice2],axis=1)

            fzone = _fluka.Zone()

            pla1 = _fluka.PLA("B" + name + "_" + format(ibody, '02'), [0, 0, -1], [0, 0, zpos[islice1]],
                              transform=transform, flukaregistry=flukaRegistry)

            ibody += 1
            pla2 = _fluka.PLA("B" + name + "_" + format(ibody, '02'), [0, 0, 1], [0, 0, zpos[islice2]],
                              transform=transform, flukaregistry=flukaRegistry)
            ibody += 1

            fzone.addIntersection(pla1)
            fzone.addIntersection(pla2)

            # loop over planes
            for iplane1 in range(0,len(polygon1),1) :
                iplane2 = iplane1+1

                if iplane2 == len(polygon1) :
                    iplane2 = 0

                p11 = polygon1[iplane1]
                p12 = polygon1[iplane2]
                p21 = polygon2[iplane1]
                p22 = polygon2[iplane2]

                d21 = p21-p11
                d12 = p12-p11

                normal = _np.cross(d21,d12)
                normal = normal/_np.linalg.norm(normal)

                pla = _fluka.PLA("B"+name+"_"+format(ibody,'02'),normal,p11,
                                 transform=transform,flukaregistry=flukaRegistry)
                ibody += 1

                fzone.addIntersection(pla)

            fregion.addZone(fzone)

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

        r1,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid1,mtra , tra ,flukaRegistry,False)
        r2,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid2,new_mtra, new_tra,flukaRegistry,False)

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

        r1,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid1,mtra , tra ,flukaRegistry,False)
        r2,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid2,new_mtra, new_tra,flukaRegistry,False)

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

        r1,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid1,mtra , tra ,flukaRegistry,False)
        r2,flukaNameCount = geant4Solid2FlukaRegion(flukaNameCount,solid2,new_mtra, new_tra,flukaRegistry,False)

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
            materialInstance.density,materialInstance.atomic_number, materialInstance.atomic_weight,materialInstance.number_of_components

        if materialInstance.number_of_components == 0 :
            pass
        else :
            pass



