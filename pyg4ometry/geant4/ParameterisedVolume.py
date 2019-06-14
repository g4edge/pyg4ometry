from ReplicaVolume import ReplicaVolume as _ReplicaVolume
from pyg4ometry.visualisation import Mesh     as _Mesh

import copy as _copy

class ParameterisedVolume(_ReplicaVolume):
    """ParametrisedVolume
    :param name: of parametrised volume
    :type name: str
    :param logical:  volume to be placed
    :type logical: logicalVolume
    :param mother: volume logical volume
    :type mother: logicalVolume
    :param ncopies: number of parametrised volumes
    :type ncopies: int
    """

    class BoxDimensions:

        def __init__(self, pX, pY, pZ):
            self.pX = pX
            self.pY = pY
            self.pZ = pZ

    class TubeDimensions:
        def __init__(self):
            self.pRMin = None
            self.pRMax = None
            self.pDz   = None
            self.pSPhi = None
            self.pDPhi = None
            self.lunit = None
            self.aunit = None

    class ConeDimensions:
        def __init__(self):
            self.pRmin1 = None
            self.pRmax1 = None
            self.pRmin2 = None
            self.pRmax2 = None
            self.pDZ    = None
            self.pDPhi  = None
            self.lunit  = None
            self.aunit  = None

    class OrbDimensions:
        def __init__(self):
            self.pRMax  = None

    class SphereDimensions:
        def __init__(self):
            pass

    def __init__(self, name, logicalVolume, motherVolume, ncopies, paramData, transforms, registry=None, addRegistry=True) :

        self.type                = "parametrised"
        self.name                = name
        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.motherVolume.add(self)
        self.ncopies             = ncopies

        self.transforms = transforms
        self.paramData  = paramData

        if addRegistry:
            registry.addPhysicalVolume(self)

        # Create parameterised meshes
        self.meshes = self.createParameterisedMeshes()
                    
    def createParameterisedMeshes(self):

        meshes = []

        for paramData,i in zip(self.paramData,range(0,int(self.ncopies.eval()),1)):
            # box
            if self.logicalVolume.solid.type == "Box" and isinstance(paramData,self.BoxDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                solid.pX = paramData.pX
                solid.pY = paramData.pY
                solid.pZ = paramData.pZ

                mesh   = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Tubs" and isinstance(paramData,self.TubeDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                solid.pRMin = paramData.pRMin
                solid.pRMax = paramData.pRMax
                solid.pDz   = paramData.pDz
                solid.pSPhi = paramData.pSPhi
                solid.pDPhi = paramData.pDPhi
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            else :
                pass

        return meshes

    def __repr__(self) :
        return ""
    

