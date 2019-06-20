from ReplicaVolume import ReplicaVolume as _ReplicaVolume
from pyg4ometry.visualisation import Mesh as _Mesh

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
        def __init__(self, pX, pY, pZ, lunit = "mm"):
            self.pX = pX
            self.pY = pY
            self.pZ = pZ
            self.lunit = lunit

    class TubeDimensions:
        def __init__(self, pRMin, pRMax, pDz, pSPhi, pDPhi, lunit ="mm", aunit="rad"):
            self.pRMin = pRMin
            self.pRMax = pRMax
            self.pDz   = pDz
            self.pSPhi = pSPhi
            self.pDPhi = pDPhi
            self.lunit = lunit
            self.aunit = aunit

    class ConeDimensions:
        def __init__(self, pRMin1, pRMax1, pRMin2, pRMax2, pDz, pSPhi, pDPhi, lunit="mm", aunit="rad"):
            self.pRMin1 = pRMin1
            self.pRMax1 = pRMax1
            self.pRMin2 = pRMin2
            self.pRMax2 = pRMax2
            self.pDz    = pDz
            self.pSPhi  = pSPhi
            self.pDPhi  = pDPhi
            self.lunit  = lunit
            self.aunit  = aunit

    class OrbDimensions:
        def __init__(self, pRMax, lunit="mm"):
            self.pRMax  = pRMax
            self.lunit  = lunit

    class SphereDimensions:
        def __init__(self, pRMin, pRMax, pSPhi, pDPhi, pSTheta, pDTheta, lunit="mm", aunit="rad"):
            self.pRMin = pRMin
            self.pRMax = pRMax
            self.pSPhi = pSPhi
            self.pDPhi = pDPhi
            self.pSTheta = pSTheta
            self.pDTheta = pDTheta
            self.lunit = lunit
            self.aunit = aunit

    class TorusDimensions:
        def __init__(self, pRMin, pRMax, pRTor, pSPhi, pDPhi, lunit="mm", aunit="rad"):
            self.pRMin = pRMin
            self.pRMax = pRMax
            self.pRTor = pRTor
            self.pSPhi = pSPhi
            self.pDPhi = pDPhi
            self.lunit = lunit
            self.aunit = aunit

    class HypeDimensions:
        def __init__(self, innerRadius, outerRadius, innerStereo, outerStereo, lenZ, lunit="mm", aunit="rad"):
            self.innerRadius = innerRadius
            self.outerRadius = outerRadius
            self.innerStereo = innerStereo
            self.outerStereo = outerStereo
            self.lenZ        = lenZ
            self.lunit       = lunit
            self.aunit       = aunit

    class ParaDimensions:
        def __init__(self, pX, pY, pZ, pAlpha, pTheta, pPhi, lunit="mm", aunit="rad"):
            self.pX = pX
            self.pY = pY
            self.pZ = pZ
            self.pAlpha = pAlpha
            self.pTheta = pTheta
            self.pPhi   = pPhi
            self.lunit  = lunit
            self.aunit  = aunit

    class TrdDimensions:
        def __init__(self, pX1, pX2, pY1, pY2, pZ, lunit="mm"):
            self.pX1 = pX1
            self.pX2 = pX2
            self.pY1 = pY1
            self.pY2 = pY2
            self.pZ  = pZ
            self.lunit = lunit

    class TrapDimensions:
        def __init__(self, pDz, pTheta, pDPhi, pDy1, pDx1, pDx2, pAlp1, pDy2, pDx3, pDx4,
                     pAlp2, lunit="mm", aunit="rad"):
            self.pDz = pDz
            self.pTheta = pTheta
            self.pDPhi = pDPhi
            self.pDy1 = pDy1
            self.pDx1 = pDx1
            self.pDx2 = pDx2
            self.pAlp1 = pAlp1
            self.pDy2 = pDy2
            self.pDx3 = pDx3
            self.pDx4 = pDx4
            self.pAlp2 = pAlp2
            self.lunit = lunit
            self.aunit = aunit

    class PolyconeDimensions:
        def __init__(self, pSPhi, pDPhi, pZpl, pRMin, pRMax, lunit="mm", aunit="rad"):
            self.pSPhi = pSPhi
            self.pDPhi = pDPhi
            self.pZpl  = pZpl
            self.pRMin = pRMin
            self.pRMax = pRMax
            self.lunit = lunit
            self.aunit = aunit

    class PolyhedraDimensions:
        def __init__(self):
            pass

    class EllipsoidDimensions:
        def __init__(self, pxSemiAxis, pySemiAxis, pzSemiAxis, pzBottomCut, pzTopCut,
                     lunit="mm", aunit="rad"):
            self.pxSemiAxis = pxSemiAxis
            self.pySemiAxis = pySemiAxis
            self.pzSemiAxis = pzSemiAxis
            self.pzBottomCut = pzBottomCut
            self.pzTopCut = pzTopCut
            self.lunit = lunit
            self.aunit = aunit

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

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pX = paramData.pX
                solid.pY = paramData.pY
                solid.pZ = paramData.pZ

                mesh   = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Tubs" and isinstance(paramData,self.TubeDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pRMin = paramData.pRMin
                solid.pRMax = paramData.pRMax
                solid.pDz   = paramData.pDz
                solid.pSPhi = paramData.pSPhi
                solid.pDPhi = paramData.pDPhi
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Cons" and isinstance(paramData,self.ConeDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pRmin1 = paramData.pRMin1
                solid.pRmax1 = paramData.pRMax1
                solid.pRmin2 = paramData.pRMin2
                solid.pRmax2 = paramData.pRMax2
                solid.pDZ    = paramData.pDz
                solid.pSPhi  = paramData.pSPhi
                solid.pDPhi  = paramData.pDPhi
                solid.lunit  = paramData.lunit
                solid.aunit  = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Orb" and isinstance(paramData,self.OrbDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pRMax = paramData.pRMax
                solid.lunit = paramData.lunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Sphere" and isinstance(paramData,self.SphereDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pRMin = paramData.pRMin
                solid.pRMax = paramData.pRMax
                solid.pSPhi = paramData.pSPhi
                solid.pDPhi = paramData.pDPhi
                solid.pSTheta = paramData.pSTheta
                solid.pDTheta = paramData.pDTheta
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Torus" and isinstance(paramData,self.TorusDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pRmin = paramData.pRMin
                solid.pRmax = paramData.pRMax
                solid.pRtor = paramData.pRTor
                solid.pSPhi = paramData.pSPhi
                solid.pDPhi = paramData.pDPhi
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Hype" and isinstance(paramData,self.HypeDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.innerRadius = paramData.innerRadius
                solid.outerRadius = paramData.outerRadius
                solid.innerStereo = paramData.innerStereo
                solid.outerStereo = paramData.outerStereo
                solid.lenZ = paramData.lenZ
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Para" and isinstance(paramData,self.ParaDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pDx = paramData.pX
                solid.pDy = paramData.pY
                solid.pDz = paramData.pZ
                solid.pAlpha = paramData.pAlpha
                solid.pTheta = paramData.pTheta
                solid.pPhi = paramData.pPhi
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Trd" and isinstance(paramData,self.TrdDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pX1 = paramData.pX1
                solid.pX2 = paramData.pX2
                solid.pY1 = paramData.pY1
                solid.pY2 = paramData.pY2
                solid.pZ = paramData.pZ
                solid.lunit = paramData.lunit

                mesh = _Mesh(solid)
                meshes.append(mesh)
            elif self.logicalVolume.solid.type == "Trap" and isinstance(paramData,self.TrapDimensions):
                solid = _copy.deepcopy(self.logicalVolume.solid)

                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)

                solid.pDz = paramData.pDz
                solid.pTheta = paramData.pTheta
                solid.pDPhi = paramData.pDPhi
                solid.pDy1 = paramData.pDy1
                solid.pDx1 = paramData.pDx1
                solid.pDx2 = paramData.pDx2
                solid.pAlp1 = paramData.pAlp1
                solid.pDy2 = paramData.pDy2
                solid.pDx3 = paramData.pDx3
                solid.pDx4 = paramData.pDx4
                solid.pAlp2 = paramData.pAlp2
                solid.lunit = paramData.lunit
                solid.aunit = paramData.aunit

                mesh = _Mesh(solid)
                meshes.append(mesh)

            else:
                pass

        return meshes

    def __repr__(self) :
        return ""