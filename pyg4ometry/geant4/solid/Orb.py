from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

import logging as _log
import numpy as _np

class Orb(_SolidBase):
    """
    Constructs a solid sphere.
    
    :param name: of the sold
    :type name: str
    :param pRMax: outer radius
    :type pRMax: float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    :param nstack: number of theta elements for meshing
    :type nstack: int     
    """
    def __init__(self, name, pRMax, registry, lunit="mm",
                 nslice=None, nstack=None, addRegistry=True):
        super(Orb, self).__init__(name, 'Orb', registry)

        self.pRMax = pRMax
        self.lunit = lunit
        self.nslice = nslice if nslice else _config.SolidDefaults.Orb.nslice
        self.nstack = nstack if nslice else _config.SolidDefaults.Orb.nstack

        self.dependents = []

        self.varNames = ["pRMax"]
        self.varUnits = ["lunit"]

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Orb : {} {}".format(self.name, self.pRMax)

    ''''
    def pycsgmeshOld(self):
        _log.info("orb.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pRMax = self.evaluateParameter(self.pRMax)*luval

        _log.info("orb.pycsgmesh>")
        mesh = _CSG.sphere(center=[0,0,0], radius=pRMax,
                           slices=self.nslice, stacks=self.nstack)
        return mesh
    '''
    def mesh(self):

        _log.info("orb.antlr>")

        import pyg4ometry.gdml.Units as _Units  # TODO move circular import 
        luval = _Units.unit(self.lunit)

        pRMax = self.evaluateParameter(self.pRMax) * luval

        polygons = []

        _log.info("orb.pycsgmesh>")


        dPhi = 2 * _np.pi / self.nslice
        dTheta = _np.pi / self.nstack
        
        for i in range(0, self.nslice, 1):

            i1 = i
            i2 = i+1

            p1 = dPhi*i1
            p2 = dPhi*i2

            for j in range(0, self.nstack, 1) :
                j1 = j
                j2 = j+1

                t1 = dTheta * j1
                t2 = dTheta * j2


                xRMaxP1T1 = pRMax * _np.sin(t1) * _np.cos(p1)
                yRMaxP1T1 = pRMax * _np.sin(t1) * _np.sin(p1)
                zRMaxP1T1 = pRMax * _np.cos(t1)

                xRMaxP2T1 = pRMax * _np.sin(t1) * _np.cos(p2)
                yRMaxP2T1 = pRMax * _np.sin(t1) * _np.sin(p2)
                zRMaxP2T1 = pRMax * _np.cos(t1)

                xRMaxP1T2 = pRMax * _np.sin(t2) * _np.cos(p1)
                yRMaxP1T2 = pRMax * _np.sin(t2) * _np.sin(p1)
                zRMaxP1T2 = pRMax * _np.cos(t2)

                xRMaxP2T2 = pRMax * _np.sin(t2) * _np.cos(p2)
                yRMaxP2T2 = pRMax * _np.sin(t2) * _np.sin(p2)
                zRMaxP2T2 = pRMax * _np.cos(t2)

                if t1 == 0 :                 # if north pole (triangles)
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                    vCurv.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                    polygons.append(_Polygon(vCurv))
                elif t2 == _np.pi :   # if south pole (triangleS)
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                    vCurv.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                    polygons.append(_Polygon(vCurv))
                else :                      # normal curved quad
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                    vCurv.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                    vCurv.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                    polygons.append(_Polygon(vCurv))

        mesh = _CSG.fromPolygons(polygons)
        return mesh
