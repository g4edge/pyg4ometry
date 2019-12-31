import pyg4ometry.fluka as _fluka

def geant42Fluka(logicalVolume, rotation = [0,0,0], position = [0,0,0], scale = [1,1,1]) :

    # fluka registry
    freg = _fluka.FlukaRegistry()

    lvSolid     = logicalVolume.solid
    lvMaterial  = logicalVolume.material

    # extent of outer solid (good for setting BLKHOLE)
    lvExtent    = logicalVolume.extent(includeBoundingSolid = True)

    # convert lv bounding solid
    lvZone = geant4Solid2FlukaZone(lvSolid,rotation,position,scale,freg)


    for daughterVolume in logicalVolume.daughterVolumes:
        dvName     = daughterVolume.name
        dvSolid    = daughterVolume.logicalVolume.solid
        dvMaterial = daughterVolume.logicalVolume.material
        dvRotation = daughterVolume.rotation.eval()
        dvPosition = daughterVolume.position.eval()
        dvScale    = daughterVolume.scale
        # check the scale (as can be none in Physical volume (TODO better interface?)
        if dvScale :
            dvScale = dvScale.eval()

        # compound transformation to be in world coords


        # convert daughterVolume
        dvZone     = geant4Solid2FlukaZone(dvSolid,dvRotation,dvPosition,dvScale,freg)

        # substract daughers
        lvZone.addSubtraction(dvZone)

        print dvZone.flukaFreeString()

    print lvZone.flukaFreeString()

    return freg

# TODO should this be a zone of region
def geant4Solid2FlukaZone(solid, rotation = [0,0,0], position = [0,0,0], scale = [1,1,1], freg = None) :

    fzone = None

    if solid.type == 'Box' :
        fbody= _fluka.RPP(solid.name,
                          -float(solid.pX)/2, float(solid.pX)/2,
                          -float(solid.pY)/2, float(solid.pY)/2,
                          -float(solid.pZ)/2, float(solid.pZ)/2,
                          translation=position,flukaregistry=freg)
        fzone = _fluka.Zone()
        fzone.addIntersection(fbody)


    return fzone
