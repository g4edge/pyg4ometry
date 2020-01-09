import pyg4ometry.fluka as _fluka
from pyg4ometry.fluka.directive import rotoTranslationFromTra2 as _rotoTranslationFromTra2
import numpy as _np
import copy as _copy


def geant42FlukaLogical(logicalVolume) :
    rotation = _np.array([0,0,0])
    position = _np.array([0,0,0])
    scale    = _np.array([1,1,1])

    flukaRegistry = _fluka.FlukaRegistry()

    flukaNameCount = 0

    # find extent of logical
    extent = logicalVolume.extent()

    # create black body
    # blackBody = _fluka.RPP("BLKBODY",)



    for dv in logicalVolume.daughterVolumes :

        newposition = position + _np.array(dv.position.eval())
        newrotation = _np.array(dv.rotation.eval())
        # new rotation
        # new scale

        flukaDaughterOuterRegion, flukaNameCount = geant42FlukaPhysicalVolume(dv,newrotation,newposition,scale,flukaRegistry,flukaNameCount)

        # subtract daughters from black body

    return flukaRegistry

def geant42FlukaPhysicalVolume(physicalVolume,
                      rotation = [0,0,0],position = [0,0,0], scale = [1,1,1],
                      flukaRegistry=None,flukaNameCount=0) :

    # logical volume (outer and complete)
    geant4LvOuterSolid = physicalVolume.logicalVolume.solid
    flukaName = format(flukaNameCount,'04')
    # print 'g2fPhysicalVolume',physicalVolume.name, flukaName, flukaNameCount, rotation, position, scale
    flukaMotherOuterRegion = geant4Solid2FlukaRegion(flukaName,geant4LvOuterSolid,
                                                     rotation,position,scale,
                                                     flukaRegistry)
    flukaNameCount += 1
    flukaMotherRegion      = _copy.deepcopy(flukaMotherOuterRegion)


    # loop over daughers and remove from mother region
    for dv in physicalVolume.logicalVolume.daughterVolumes :

        # placement information for daughter
        newposition = position + _np.array(dv.position.eval())
        newrotation = _np.array(dv.rotation.eval())
        # new scale

        flukaDaughterOuterRegion, flukaNameCount = geant42FlukaPhysicalVolume(dv,rotation=newrotation,position=newposition,scale=scale,flukaRegistry=flukaRegistry, flukaNameCount=flukaNameCount)

        for motherZones in flukaMotherRegion.zones:
            for daughterZones in flukaDaughterOuterRegion.zones:
                motherZones.addSubtraction(daughterZones)

    flukaRegistry.addRegion(flukaMotherRegion)

    return flukaMotherOuterRegion, flukaNameCount

def geant4Solid2FlukaRegion(name,solid, rotation = [0,0,0], position = [0,0,0], scale = [1,1,1], flukaRegistry = None) :

    import pyg4ometry.gdml.Units as _Units  # TODO move circular import

    fregion = None
    fbodies = []

    transform=_rotoTranslationFromTra2("T"+name,[rotation,position], flukaregistry=flukaRegistry)

    if solid.type == 'Box' :

        uval = _Units.unit(solid.lunit)

        fbody = _fluka.RPP("B"+name+'_01',
                           -float(solid.pX)*uval/2/10., float(solid.pX)*uval/2/10.,
                           -float(solid.pY)*uval/2/10., float(solid.pY)*uval/2/10.,
                           -float(solid.pZ)*uval/2/10., float(solid.pZ)*uval/2/10.,
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

    elif solid.type == "Tubs":
        # main cylinder
        fbody1 = _fluka.ZCC("B"+name+"_01",0,0,float(solid.pRMax),
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.XYP("B"+name+"_02",-float(solid.pDz)/2,transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.XYP("B"+name+"_03", float(solid.pDz)/2,transform=transform,
                            flukaregistry=flukaRegistry)

        # inner cylinder
        fbody4 = _fluka.ZCC("B"+name+"_04",0,0,float(solid.pRMin),
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # phi cuts
        fbody5 = _fluka.PLA("B"+name+"_05",
                            [_np.sin(float(solid.pSPhi)),_np.cos(float(solid.pSPhi)),0],
                            [0, 0, 0],
                            transform=transform,
                            flukaregistry=flukaRegistry)

        fbody6 = _fluka.PLA("B"+name+"_06",
                            [_np.sin(float(solid.pSPhi+solid.pDPhi)),_np.cos(float(solid.pSPhi+solid.pDPhi)),0],
                            [0, 0, 0],
                            transform=transform,
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

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)
        flukaRegistry.addRegion(fregion)

    elif solid.type == "CutTubs" :
        # main cylinder
        fbody1 = _fluka.ZCC("B"+name+"_01",0,0,float(solid.pRMax),
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # low z cut
        fbody2 = _fluka.PLA("B"+name+"_02",
                            [-float(solid.pLowNorm[0]),-float(solid.pLowNorm[1]),-float(solid.pLowNorm[2])],
                            [0, 0, -float(solid.pDz)/2],
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # high z cut
        fbody3 = _fluka.PLA("B"+name+"_03",
                            [float(solid.pHighNorm[0]),float(solid.pHighNorm[1]),float(solid.pHighNorm[2])],
                            [0, 0, float(solid.pDz)/2],
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # inner cylinder
        fbody4 = _fluka.ZCC("B"+name+"_04",0,0,float(solid.pRMin),
                            transform=transform,
                            flukaregistry=flukaRegistry)

        # phi cuts
        fbody5 = _fluka.PLA("B"+name+"_05",
                            [_np.sin(float(solid.pSPhi)),_np.cos(float(solid.pSPhi)),0],
                            [0, 0, 0],
                            transform=transform,
                            flukaregistry=flukaRegistry)

        fbody6 = _fluka.PLA("B"+name+"_06",
                            [_np.sin(float(solid.pSPhi+solid.pDPhi)),_np.cos(float(solid.pSPhi+solid.pDPhi)),0],
                            [0, 0, 0],
                            transform=transform,
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

        fregion = _fluka.Region("R"+name)
        fregion.addZone(fzone)
        flukaRegistry.addRegion(fregion)

    elif solid.type == "Cons":
        pass


    return fregion

def materialMapper(g4Mat) :
    pass

