from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.core import PolygonProcessing as _PolygonProcessing
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

import pyg4ometry.pycgal as _pycgal

import logging as _log
import numpy as _np

class GenericPolyhedra(_SolidBase):
    """
    Constructs a solid of rotation using an arbitrary 2D surface defined by a series of (r,z) coordinates.
    
    :param name:    name
    :type name:     str
    :param pSPhi:   angle Phi at start of rotation
    :type pSPhi:    float, Constant, Quantity, Variable, Expression
    :param pDPhi:   angle Phi at end of rotation
    :type pDPhi:    float, Constant, Quantity, Variable, Expression
    :param numSide: number of polygon sides
    :type numSide:  float, Constant, Quantity, Variable, Expression
    :param pR:      r coordinate list
    :type pR:       list of float, Constant, Quantity, Variable, Expression
    :param pZ:      z coordinate list
    :type pZ:       list of float, Constant, Quantity, Variable, Expression
    """
    def __init__(self, name, pSPhi, pDPhi, numSide, pR, pZ,
                 registry, lunit="mm", aunit="rad", addRegistry=True):
        super(GenericPolyhedra, self).__init__(name, 'GenericPolyhedra', registry)

        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.numSide = numSide
        self.pR      = pR
        self.pZ      = pZ

        self.lunit   = lunit
        self.aunit   = aunit

        self.varNames = ["pSPhi", "pDPhi", "numSide", "pR", "pZ"]
        self.varUnits = ["aunit", "aunit", None, "lunit", "lunit"]

        self.dependents = []

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Generic Polyhedra : {} {} {} {}".format(self.name, self.pSPhi,
                                                        self.pDPhi, self.numSide)

    def checkParameters(self):
        if len(self.pR) < 3:
            raise ValueError("Generic Polyhedra must have at least 3 R-Z points defined")

    def mesh(self):
        _log.info("genericpolyhedra.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval
        numSide = int(self.evaluateParameter(self.numSide))
        pR = [val*luval for val in self.evaluateParameter(self.pR)]
        pZ = [val*luval for val in self.evaluateParameter(self.pZ)]

        dPhi = pDPhi / numSide

        zrList  = [[z,r] for z,r in zip(pZ,pR)]
        zrList.reverse()
        zrArray = _np.array(zrList)

        zrListConvex = _PolygonProcessing.decomposePolygon2d(zrArray)

        # def plotConvex() :
        #     import matplotlib.pyplot as _plt
        #     _plt.figure(1)
        #     _plt.plot(pZ,pR)
        #
        #     for cvPolygon in zrListConvex:
        #         _plt.plot(cvPolygon[:,0],cvPolygon[:,1])

        # plotConvex()

        polygons = []

        for i in range(0, len(pZ), 1):

            i1 = i
            i2 = (i + 1) % len(pZ)

            zMin = pZ[i1]
            zMax = pZ[i2]

            for j in range(0, numSide, 1):
                j1 = j
                j2 = j + 1

                phi1 = dPhi * j1 + pSPhi
                phi2 = dPhi * j2 + pSPhi

                xZMinP1 = pR[i1] * _np.cos(phi1)
                yZMinP1 = pR[i1] * _np.sin(phi1)

                xZMaxP1 = pR[i2] * _np.cos(phi1)
                yZMaxP1 = pR[i2] * _np.sin(phi1)

                xZMinP2 = pR[i1] * _np.cos(phi2)
                yZMinP2 = pR[i1] * _np.sin(phi2)

                xZMaxP2 = pR[i2] * _np.cos(phi2)
                yZMaxP2 = pR[i2] * _np.sin(phi2)

                vFace = []
                if pR[i1] != 0 :
                    vFace.append(_Vertex([xZMinP1, yZMinP1, zMin]))
                vFace.append(_Vertex([xZMaxP1, yZMaxP1, zMax]))
                if pR[i2] != 0 :
                    vFace.append(_Vertex([xZMaxP2, yZMaxP2, zMax]))
                vFace.append(_Vertex([xZMinP2, yZMinP2, zMin]))

                vFace.reverse()
                if pR[i1] == 0  and pR[i2] == 0 :
                    pass
                else :
                    polygons.append(_Polygon(vFace))

        if pDPhi != 2*_np.pi :
            for cvPolygon in zrListConvex:

                vPhi1 = []
                for cvPolygonPoint in cvPolygon:
                    z = cvPolygonPoint[0]
                    r = cvPolygonPoint[1]

                    xP1 = r * _np.cos(pSPhi)
                    yP1 = r * _np.sin(pSPhi)

                    vPhi1.append(_Vertex([xP1, yP1, z]))

                vPhi1.reverse()
                polygons.append(_Polygon(vPhi1))

                vPhi2 = []
                for cvPolygonPoint in reversed(cvPolygon):

                    z = cvPolygonPoint[0]
                    r = cvPolygonPoint[1]

                    xP2 = r * _np.cos(pSPhi+pDPhi)
                    yP2 = r * _np.sin(pSPhi+pDPhi)

                    vPhi2.append(_Vertex([xP2, yP2, z]))

                vPhi2.reverse()
                polygons.append(_Polygon(vPhi2))

        mesh = _CSG.fromPolygons(polygons)

        return mesh
