from ... import config as _config

from   .SolidBase import SolidBase as _SolidBase

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

import sys as _sys
from   copy import deepcopy as _dc

import numpy as _np
import logging as _log

import resource as _resource
import time as _time

class Sphere(_SolidBase):
    """
    Constructs a section of a spherical shell.

    :param name: of object in registry
    :type name: str
    :param pRmin: inner radius of the shell
    :type pRmin: float, Constant, Quantity, Variable
    :param pRmax: outer radius of the shell
    :type pRmax: float, Constant, Quantity, Variable
    :param pSPhi: starting phi angle in radians
    :type pSPhi: float, Constant, Quantity, Variable
    :param pSTheta: starting theta angle in radians
    :type pSTheta: float, Constant, Quantity, Variable
    :param pDPhi: delta phi angle in radians
    :type pDPhi: float, Constant, Quantity, Variable
    :param pDTheta: delta theta angle in radians
    :type pDTheta: float, Constant, Quantity, Variable
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    :param nstack: number of theta elements for meshing
    :type nstack: int 
    """
    def __init__(self, name, pRmin, pRmax, pSPhi, pDPhi, pSTheta,
                 pDTheta, registry, lunit="mm", aunit="rad",
                 nslice=None, nstack=None, addRegistry=True):
        super(Sphere, self).__init__(name, 'Sphere', registry)

        self.pRmin   = pRmin
        self.pRmax   = pRmax
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pSTheta = pSTheta
        self.pDTheta = pDTheta    
        self.nslice  = nslice if nslice else _config.SolidDefaults.Sphere.nslice
        self.nstack  = nstack if nstack else _config.SolidDefaults.Sphere.nslice
        self.lunit   = lunit
        self.aunit   = aunit

        self.dependents = []

        self.varNames = ["pRmin", "pRmax", "pSPhi", "pDPhi", "pSTheta", "pDTheta"]
        self.varUnits = ["lunit", "lunit", "aunit", "aunit", "aunit", "aunit"]

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def checkParameters(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        auval = _Units.unit(self.aunit)
        if self.evaluateParameter(self.pRmin) > self.evaluateParameter(self.pRmax):
            raise ValueError("Inner radius must be less than outer radius.")
        if self.evaluateParameter(self.pDTheta)*auval > _np.pi:
            raise ValueError("pDTheta must be less than pi")
        self._twoPiValueCheck("pDPhi", self.aunit)

    def __repr__(self):
        return "Sphere : {} {} {} {} {} {} {}".format(self.name, self.pRmin,
                                                      self.pRmax, self.pSPhi,
                                                      self.pDPhi, self.pSTheta,
                                                      self.pDTheta)

    def mesh(self):
        """
        working off
        0 < phi < 2pi
        0 < theta < pi
        """

        tBefore = _time.process_time()

        _log.info("sphere.antlr>")
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin   = self.evaluateParameter(self.pRmin)*luval
        pRmax   = self.evaluateParameter(self.pRmax)*luval
        pSPhi   = self.evaluateParameter(self.pSPhi)*auval
        pDPhi   = self.evaluateParameter(self.pDPhi)*auval
        pSTheta = self.evaluateParameter(self.pSTheta)*auval
        pDTheta = self.evaluateParameter(self.pDTheta)*auval

        _log.info('Sphere.pycsgmesh>')

        polygons = []

        # changed from d - s/ st

        dPhi   = (pDPhi)/self.nslice
        dTheta = (pDTheta)/self.nstack

        for i in range(0,self.nslice,1) :

            i1 = i
            i2 = i+1

            p1 = dPhi*i1 + pSPhi
            p2 = dPhi*i2 + pSPhi

            for j in range(0,self.nstack,1) :
                j1 = j
                j2 = j+1

                t1 = dTheta * j1 + pSTheta
                t2 = dTheta * j2 + pSTheta

                if pRmin != 0 :
                    xRMinP1T1 = pRmin * _np.sin(t1) * _np.cos(p1)
                    yRMinP1T1 = pRmin * _np.sin(t1) * _np.sin(p1)
                    zRMinP1T1 = pRmin * _np.cos(t1)

                    xRMinP2T1 = pRmin * _np.sin(t1) * _np.cos(p2)
                    yRMinP2T1 = pRmin * _np.sin(t1) * _np.sin(p2)
                    zRMinP2T1 = pRmin * _np.cos(t1)

                    xRMinP1T2 = pRmin * _np.sin(t2) * _np.cos(p1)
                    yRMinP1T2 = pRmin * _np.sin(t2) * _np.sin(p1)
                    zRMinP1T2 = pRmin * _np.cos(t2)

                    xRMinP2T2 = pRmin * _np.sin(t2) * _np.cos(p2)
                    yRMinP2T2 = pRmin * _np.sin(t2) * _np.sin(p2)
                    zRMinP2T2 = pRmin * _np.cos(t2)
                else :
                    xRMinP1T1 = 0.0
                    yRMinP1T1 = 0.0
                    zRMinP1T1 = 0.0

                    xRMinP2T1 = 0.0
                    yRMinP2T1 = 0.0
                    zRMinP2T1 = 0.0

                    xRMinP1T2 = 0.0
                    yRMinP1T2 = 0.0
                    zRMinP1T2 = 0.0

                    xRMinP2T2 = 0.0
                    yRMinP2T2 = 0.0
                    zRMinP2T2 = 0.0

                xRMaxP1T1 = pRmax * _np.sin(t1) * _np.cos(p1)
                yRMaxP1T1 = pRmax * _np.sin(t1) * _np.sin(p1)
                zRMaxP1T1 = pRmax * _np.cos(t1)

                xRMaxP2T1 = pRmax * _np.sin(t1) * _np.cos(p2)
                yRMaxP2T1 = pRmax * _np.sin(t1) * _np.sin(p2)
                zRMaxP2T1 = pRmax * _np.cos(t1)

                xRMaxP1T2 = pRmax * _np.sin(t2) * _np.cos(p1)
                yRMaxP1T2 = pRmax * _np.sin(t2) * _np.sin(p1)
                zRMaxP1T2 = pRmax * _np.cos(t2)

                xRMaxP2T2 = pRmax * _np.sin(t2) * _np.cos(p2)
                yRMaxP2T2 = pRmax * _np.sin(t2) * _np.sin(p2)
                zRMaxP2T2 = pRmax * _np.cos(t2)

                ###########################
                # Curved sphere faces
                ###########################
                if t1 == 0:                 # if north pole (triangles)
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                    vCurv.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                    # print "outer  north pole",len(polygons)
                    polygons.append(_Polygon(vCurv))
                elif t2 == _np.pi :   # if south pole (triangleS)
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                    vCurv.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                    # print "outer south pole",len(polygons)
                    polygons.append(_Polygon(vCurv))
                else :                      # normal curved quad
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                    vCurv.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                    vCurv.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                    # print "outer normal quad",len(polygons)
                    polygons.append(_Polygon(vCurv))

                if pRmin != 0:
                    if t1 == 0:  # if north pole (triangles)
                        vCurv = []
                        vCurv.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                        vCurv.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2]))
                        vCurv.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                        # print "inner north pole", len(polygons)
                        polygons.append(_Polygon(vCurv))
                    elif t2 == _np.pi:  # if south pole
                        vCurv = []
                        vCurv.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1]))
                        vCurv.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                        vCurv.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                        # print "inner south pole", len(polygons)
                        polygons.append(_Polygon(vCurv))
                    else:  # normal curved quad
                        vCurv = []
                        vCurv.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1]))
                        vCurv.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                        vCurv.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2]))
                        vCurv.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                        # print "inner quad ", len(polygons)
                        polygons.append(_Polygon(vCurv))
                if pDPhi != 2*_np.pi :
                    if i == 0 and pSPhi != 0 :
                        vEnd = []
                        if pRmin != 0 :
                            vEnd.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                        vEnd.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2]))
                        vEnd.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                        vEnd.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                        # print "theta low end ", len(polygons)
                        polygons.append(_Polygon(vEnd))

                    if i == self.nslice-1 and pSPhi + pDPhi != 2*_np.pi:
                        vEnd = []
                        if pRmin != 0 :
                            vEnd.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1]))
                        vEnd.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                        vEnd.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                        vEnd.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                        # print "theta low end ", len(polygons)
                        polygons.append(_Polygon(vEnd))

                if pDTheta != _np.pi:
                    if j == 0 and pSTheta != 0:
                        vEnd = []
                        if pRmin != 0 :
                            vEnd.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                        vEnd.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                        vEnd.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                        vEnd.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1]))
                        # print "theta low end ", len(polygons)
                        polygons.append(_Polygon(vEnd))

                    if j == self.nstack-1 and pSTheta + pDTheta != _np.pi :
                        vEnd = []
                        if pRmin != 0 :
                            vEnd.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2]))
                        vEnd.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                        vEnd.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                        vEnd.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                        # print "theta low end ", len(polygons)
                        polygons.append(_Polygon(vEnd))
        tAfter = _time.process_time()

        mBefore = _resource.getrusage(_resource.RUSAGE_SELF).ru_maxrss
        mesh = _CSG.fromPolygons(polygons)
        mAfter = _resource.getrusage(_resource.RUSAGE_SELF).ru_maxrss
        _log.info('Sphere.pycsgmesh> profile {} {} {} {} {}'.format(self.nstack, self.nslice, mesh.getNumberPolys(),mAfter-mBefore,tAfter-tBefore))
        return mesh
