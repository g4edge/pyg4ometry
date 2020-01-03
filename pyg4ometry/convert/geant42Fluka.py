import pyg4ometry.fluka as _fluka
import numpy as _np

def geant42Fluka(logicalVolume, rotation = [0,0,0], position = [0,0,0], scale = [1,1,1], flukaRegistry = None,flukaRegionCount = 0) :

    # fluka registry
    if flukaRegistry == None :
        flukaRegistry = _fluka.FlukaRegistry()

    lvName      = logicalVolume.name
    lvSolid     = logicalVolume.solid
    lvMaterial  = logicalVolume.material

    # extent of outer solid (good for setting BLKHOLE)
    lvExtent    = logicalVolume.extent(includeBoundingSolid = True)


    # convert lv bounding solid
    frName = "F"+format(flukaRegionCount,'04')
    lvRegion = geant4Solid2FlukaZone(frName,lvSolid,rotation,position,scale,flukaRegistry)
    flukaRegionCount += 1

    for daughterVolume, dvI in zip(logicalVolume.daughterVolumes, range(1,len(logicalVolume.daughterVolumes)+1)):
        dvName     = daughterVolume.name
        dvLogical  = daughterVolume.logicalVolume
        dvSolid    = daughterVolume.logicalVolume.solid
        dvMaterial = daughterVolume.logicalVolume.material
        dvRotation = daughterVolume.rotation.eval()
        dvPosition = daughterVolume.position.eval()
        dvScale    = daughterVolume.scale
        # check the scale as can be none in Physical volume (TODO better interface?)
        if dvScale :
            dvScale = dvScale.eval()

        # compound transformation to be in world coords

        # convert daughterVolume
        frName = "F" + format(flukaRegionCount, '04')
        dvRegion     = geant4Solid2FlukaZone(frName,dvSolid,dvRotation,dvPosition,dvScale,flukaRegistry)
        flukaRegionCount +=1

        # substract daughters
        for z in dvRegion.zones:
            lvRegion.zones[-1].addSubtraction(z)

        # add daughters
        freg, flukaRegionCount = geant42Fluka(dvLogical,flukaRegistry=flukaRegistry, flukaRegionCount=flukaRegionCount)

    flukaRegistry.addRegion(lvRegion)

    return flukaRegistry, flukaRegionCount

# TODO should this be a zone of region
def geant4Solid2FlukaZone(name,solid, rotation = [0,0,0], position = [0,0,0], scale = [1,1,1], flukaRegistry = None) :

    fregion = None

    transform= [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]

    if solid.type == 'Box' :

        fbody = _fluka.RPP(name+'_01',
                           -float(solid.pX)/2, float(solid.pX)/2,
                           -float(solid.pY)/2, float(solid.pY)/2,
                           -float(solid.pZ)/2, float(solid.pZ)/2,
                           translation=position,transform=transform,
                           flukaregistry=flukaRegistry)
        fzone = _fluka.Zone()
        fzone.addIntersection(fbody)
        fregion = _fluka.Region(name)
        fregion.addZone(fzone)

    elif solid.type == "Tubs":
        # main cylinder
        fbody1 = _fluka.ZCC(name+"_01",0,0,float(solid.pRMax),
                            translation=position, transform=transform,
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.XYP(name+"_02",-float(solid.pDz)/2,translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.XYP(name+"_03", float(solid.pDz)/2,translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        # inner cylinder
        fbody4 = _fluka.ZCC(name+"_04",0,0,float(solid.pRMin),
                            translation=position, transform=transform,
                            flukaregistry=flukaRegistry)

        # phi cuts
        fbody5 = _fluka.PLA(name+"_05",
                            [_np.sin(float(solid.pSPhi)),_np.cos(float(solid.pSPhi)),0],
                            [0, 0, 0],
                            translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        fbody6 = _fluka.PLA(name+"_06",
                            [_np.sin(float(solid.pSPhi+solid.pDPhi)),_np.cos(float(solid.pSPhi+solid.pDPhi)),0],
                            [0, 0, 0],
                            translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

    elif solid.type == "CutTubs" :
        # main cylinder
        fbody1 = _fluka.ZCC(name+"_01",0,0,float(solid.pRMax),
                            translation=position, transform=transform,
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.PLA(name+"_02",
                            [-float(solid.pLowNorm[0]),-float(solid.pLowNorm[1]),-float(solid.pLowNorm[2])],
                            [0, 0, -float(solid.pDz)/2],
                            translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.PLA(name+"_03",
                            [float(solid.pHighNorm[0]),float(solid.pHighNorm[1]),float(solid.pHighNorm[2])],
                            [0, 0, float(solid.pDz)/2],
                            translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        # inner cylinder
        fbody4 = _fluka.ZCC(name+"_04",0,0,float(solid.pRMin),
                            translation=position, transform=transform,
                            flukaregistry=flukaRegistry)

        # phi cuts
        fbody5 = _fluka.PLA(name+"_05",
                            [_np.sin(float(solid.pSPhi)),_np.cos(float(solid.pSPhi)),0],
                            [0, 0, 0],
                            translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        fbody6 = _fluka.PLA(name+"_06",
                            [_np.sin(float(solid.pSPhi+solid.pDPhi)),_np.cos(float(solid.pSPhi+solid.pDPhi)),0],
                            [0, 0, 0],
                            translation=position,transform=transform,
                            flukaregistry=flukaRegistry)

        fzone = _fluka.Zone()
        fzone.addIntersection(fbody1)
        fzone.addSubtraction(fbody2)
        fzone.addIntersection(fbody3)

        fzone.addSubtraction(fbody4)

        fzone1 = _fluka.Zone()
        fzone1.addIntersection(fbody5)
        fzone1.addIntersection(fbody6)

        fzone.addSubtraction(fzone1)

        fregion = _fluka.Region(name)
        fregion.addZone(fzone)
        flukaRegistry.addRegion(fregion)

    elif solid.type == "Cons":
        pass


    return fregion

def materialMapper(g4Mat) :
    pass

