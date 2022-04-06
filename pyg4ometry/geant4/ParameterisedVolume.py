from .ReplicaVolume import ReplicaVolume as _ReplicaVolume
import pyg4ometry.geant4.solid as _solid
from pyg4ometry.visualisation import Mesh as _Mesh
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
import pyg4ometry.transformation as _trans

import copy as _copy
import numpy as _np
import logging as _log

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
        def __init__(self, pSPhi, pDPhi, numSide, pZpl, pRMin, pRMax, lunit="mm", aunit="rad"):
            self.pSPhi = pSPhi
            self.pDPhi = pDPhi
            self.numSide = numSide
            self.pZpl = pZpl
            self.pRMin = pRMin
            self.pRMax = pRMax
            self.lunit = lunit
            self.aunit = aunit

    class EllipsoidDimensions:
        def __init__(self, pxSemiAxis, pySemiAxis, pzSemiAxis, pzBottomCut, pzTopCut, lunit="mm"):
            self.pxSemiAxis = pxSemiAxis
            self.pySemiAxis = pySemiAxis
            self.pzSemiAxis = pzSemiAxis
            self.pzBottomCut = pzBottomCut
            self.pzTopCut = pzTopCut
            self.lunit = lunit

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
        self.registry = registry

        # physical visualisation options
        self.visOptions    = _VisOptions()

        # Create parameterised meshes
        self.meshes = self.createParameterisedMeshes()

    def createParameterisedMeshes(self):

        meshes = []

        for paramData, i in zip(self.paramData, range(0, int(self.ncopies), 1)):
            # box
            if self.logicalVolume.solid.type == "Box" and isinstance(paramData,self.BoxDimensions):
                solid = _solid.Box(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                   paramData.pX,
                                   paramData.pY,
                                   paramData.pZ,
                                   self.logicalVolume.registry,
                                   paramData.lunit,
                                   False)

                mesh   = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Tubs" and isinstance(paramData,self.TubeDimensions):
                solid = _solid.Tubs(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                    paramData.pRMin,
                                    paramData.pRMax,
                                    paramData.pDz,
                                    paramData.pSPhi,
                                    paramData.pDPhi,
                                    self.logicalVolume.registry,
                                    paramData.lunit,
                                    paramData.aunit,
                                    self.logicalVolume.solid.nslice,
                                    False)

                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Cons" and isinstance(paramData,self.ConeDimensions):
                solid = _solid.Cons(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                    paramData.pRMin1,
                                    paramData.pRMax1,
                                    paramData.pRMin2,
                                    paramData.pRMax2,
                                    paramData.pDz,
                                    paramData.pSPhi,
                                    paramData.pDPhi,
                                    self.logicalVolume.registry,
                                    paramData.lunit,
                                    paramData.aunit,
                                    self.logicalVolume.solid.nslice,
                                    False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Orb" and isinstance(paramData,self.OrbDimensions):
                solid =_solid.Orb(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                  paramData.pRMax,
                                  self.logicalVolume.registry,
                                  paramData.lunit,
                                  self.logicalVolume.solid.nslice,
                                  self.logicalVolume.solid.nstack,
                                  False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Sphere" and isinstance(paramData,self.SphereDimensions):
                solid = _solid.Sphere(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                      paramData.pRMin,
                                      paramData.pRMax,
                                      paramData.pSPhi,
                                      paramData.pDPhi,
                                      paramData.pSTheta,
                                      paramData.pDTheta,
                                      self.logicalVolume.registry,
                                      paramData.lunit,
                                      paramData.aunit,
                                      self.logicalVolume.solid.nslice,
                                      self.logicalVolume.solid.nstack,
                                      False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Torus" and isinstance(paramData,self.TorusDimensions):
                solid = _solid.Torus(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                     paramData.pRMin,
                                     paramData.pRMax,
                                     paramData.pRTor,
                                     paramData.pSPhi,
                                     paramData.pDPhi,
                                     self.logicalVolume.registry,
                                     paramData.lunit,
                                     paramData.aunit,
                                     self.logicalVolume.solid.nslice,
                                     self.logicalVolume.solid.nstack,
                                     False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Hype" and isinstance(paramData,self.HypeDimensions):
                solid = _solid.Hype(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                    paramData.innerRadius,
                                    paramData.outerRadius,
                                    paramData.innerStereo,
                                    paramData.outerStereo,
                                    paramData.lenZ,
                                    self.logicalVolume.registry,
                                    paramData.lunit,
                                    paramData.aunit,
                                    self.logicalVolume.solid.nslice,
                                    self.logicalVolume.solid.nstack,
                                    False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Para" and isinstance(paramData,self.ParaDimensions):
                solid = _solid.Para(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                    paramData.pX,
                                    paramData.pY,
                                    paramData.pZ,
                                    paramData.pAlpha,
                                    paramData.pTheta,
                                    paramData.pPhi,
                                    self.logicalVolume.registry,
                                    paramData.lunit,
                                    paramData.aunit,
                                    False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Trd" and isinstance(paramData,self.TrdDimensions):
                solid = _solid.Trd(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                   paramData.pX1,
                                   paramData.pX2,
                                   paramData.pY1,
                                   paramData.pY2,
                                   paramData.pZ,
                                   self.logicalVolume.registry,
                                   paramData.lunit,
                                   False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Trap" and isinstance(paramData,self.TrapDimensions):
                solid = _solid.Trap(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                    paramData.pDz,
                                    paramData.pTheta,
                                    paramData.pDPhi,
                                    paramData.pDy1,
                                    paramData.pDx1,
                                    paramData.pDx2,
                                    paramData.pAlp1,
                                    paramData.pDy2,
                                    paramData.pDx3,
                                    paramData.pDx4,
                                    paramData.pAlp2,
                                    self.logicalVolume.registry,
                                    paramData.lunit,
                                    paramData.aunit,
                                    False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Polycone" and isinstance(paramData,self.PolyconeDimensions):

                solid = _solid.Polycone(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                        paramData.pSPhi,
                                        paramData.pDPhi,
                                        paramData.pZpl,
                                        paramData.pRMin,
                                        paramData.pRMax,
                                        self.logicalVolume.registry,
                                        paramData.lunit,
                                        paramData.aunit,
                                        self.logicalVolume.solid.nslice,
                                        False)

                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Polyhedra" and isinstance(paramData,self.PolyhedraDimensions):
                solid = _solid.Polyhedra(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                         paramData.pSPhi,
                                         paramData.pDPhi,
                                         paramData.numSide,
                                         len(paramData.pZpl),
                                         paramData.pZpl,
                                         paramData.pRMin,
                                         paramData.pRMax,
                                         self.logicalVolume.registry,
                                         paramData.lunit,
                                         paramData.aunit,
                                         False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            elif self.logicalVolume.solid.type == "Ellipsoid" and isinstance(paramData,self.EllipsoidDimensions):
                solid = _solid.Ellipsoid(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                         paramData.pxSemiAxis,
                                         paramData.pySemiAxis,
                                         paramData.pzSemiAxis,
                                         paramData.pzBottomCut,
                                         paramData.pzTopCut,
                                         self.logicalVolume.registry,
                                         paramData.lunit,
                                         self.logicalVolume.solid.nslice,
                                         self.logicalVolume.solid.nstack,
                                         False)
                mesh = _Mesh(solid)
                meshes.append(mesh)

            else:
                pass

        return meshes

    def __repr__(self) :
        return ""

    def extent(self, includeBoundingSolid = True):
        _log.info('ParametrisedVolume.extent> %s' % (self.name))

        vMin = [1e99, 1e99, 1e99]
        vMax = [-1e99, -1e99, -1e99]

        for trans, mesh in zip(self.transforms, self.meshes) :
            # transform daughter meshes to parent coordinates
            dvmrot = _trans.tbxyz2matrix(trans[0].eval())
            dvtra = _np.array(trans[1].eval())

            [vMinDaughter, vMaxDaughter] = mesh.getBoundingBox()

            # TODO do we need scale here?
            vMinDaughter = _np.array((dvmrot.dot(vMinDaughter) + dvtra)).flatten()
            vMaxDaughter = _np.array((dvmrot.dot(vMaxDaughter) + dvtra)).flatten()


            if vMaxDaughter[0] > vMax[0] :
                vMax[0] = vMaxDaughter[0]
            if vMaxDaughter[1] > vMax[1] :
                vMax[1] = vMaxDaughter[1]
            if vMaxDaughter[2] > vMax[2] :
                vMax[2] = vMaxDaughter[2]

            if vMinDaughter[0] < vMin[0] :
                vMin[0] = vMinDaughter[0]
            if vMinDaughter[1] < vMin[1] :
                vMin[1] = vMinDaughter[1]
            if vMinDaughter[2] < vMin[2] :
                vMin[2] = vMinDaughter[2]

        return [vMin,vMax]
