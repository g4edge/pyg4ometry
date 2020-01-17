from   SolidBase import SolidBase as _SolidBase
from   ...pycsg.core import CSG as _CSG
from   ...pycsg.geom import Vertex as _Vertex
from   ...pycsg.geom import Vector as _Vector
from   ...pycsg.geom import Polygon as _Polygon
from   Wedge import Wedge as _Wedge
import sys as _sys
from   copy import deepcopy as _dc

import numpy as _np
import logging as _log

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
                 nslice=10, nstack=10, addRegistry=True):

        self.type    = 'Sphere'
        self.name    = name
        self.pRmin   = pRmin
        self.pRmax   = pRmax
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pSTheta = pSTheta
        self.pDTheta = pDTheta    
        self.nslice  = nslice
        self.nstack  = nstack
        self.lunit   = lunit
        self.aunit   = aunit

        self.dependents = []

        self.varNames = ["pRmin", "pRmax", "pSPhi","pDPhi","pSTheta","pDTheta"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

        self.checkParameters()

    def checkParameters(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        auval = _Units.unit(self.aunit)
        if self.evaluateParameter(self.pRmin) > self.evaluateParameter(self.pRmax):
            raise ValueError("Inner radius must be less than outer radius.")
        if self.evaluateParameter(self.pDTheta)*auval > _np.pi:
            raise ValueError("pDTheta must be less than pi")
        if self.evaluateParameter(self.pDPhi)*auval > _np.pi*2:
            raise ValueError("pDPhi must be less than 2 pi")

    def __repr__(self):
        return "Sphere : {} {} {} {} {} {} {}".format(self.name, self.pRmin,
                                                      self.pRmax, self.pSPhi,
                                                      self.pDPhi, self.pSTheta,
                                                      self.pDTheta)

    def pycsgmeshOld(self):
        # 2.78316307068 1612
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

        _log.info("sphere.pycsgmesh>")
        thetaFin = pSTheta + pDTheta
        phiFin   = pSPhi + pDPhi

        mesh = _CSG.sphere(radius=pRmax, slices=self.nslice, stacks=self.nstack)

        #makes shell by removing a sphere of radius pRmin from the inside of sphere
        if pRmin:
            mesh_inner = _CSG.sphere(radius=pRmin, slices=self.nslice, stacks=self.nstack)
            mesh = mesh.subtract(mesh_inner)

        #Theta change: allows for different theta angles, using primtives: cube and cone.
        if thetaFin == _np.pi/2.:
            mesh_box = _CSG.cube(center=[0,0,1.1*pRmax], radius=1.1*pRmax)
            mesh = mesh.subtract(mesh_box)

        if thetaFin > _np.pi/2. and thetaFin < _np.pi:
            mesh_lower = _CSG.cone(start=[0,0,-2*pRmax], end=[0,0,0], radius=2*pRmax*_np.tan(_np.pi - thetaFin))
            mesh = mesh.subtract(mesh_lower)

        if self.pSTheta > _np.pi/2. and self.pSTheta < _np.pi:
            mesh_lower2 = _CSG.cone(start=[0,0,-2*pRmax], end=[0,0,0], radius=2*self.pRmax*_np.tan(_np.pi - pSTheta))
            mesh = mesh.intersect(mesh_lower2)

        if thetaFin < _np.pi/2.:
            mesh_upper = _CSG.cone(start=[0,0,2*pRmax], end=[0,0,0], radius=2*pRmax*_np.tan(thetaFin))
            mesh = mesh.intersect(mesh_upper)

        if pSTheta < _np.pi/2. and pSTheta > 0:
            mesh_upper2 = _CSG.cone(start=[0,0,2*pRmax], end=[0,0,0], radius=2*pRmax*_np.tan(self.pSTheta))
            mesh = mesh.subtract(mesh_upper2)


        #Phi change: allows for different theta angles, using the Wedge solid class
        if phiFin < 2*_np.pi:
            mesh_wedge = _Wedge("wedge_temp", 2*pRmax, pSPhi, pDPhi, 3*pRmax).pycsgmesh()
            mesh = mesh.intersect(mesh_wedge)

        return mesh


    def pycsgmesh(self):
        """
        working off
        0 < phi < 2pi
        0 < theta < pi
        """
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

        dPhi   = (pDPhi-pSPhi)/self.nslice
        dTheta = (pDTheta-pSTheta)/self.nstack

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
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1], None))
                    vCurv.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2], None))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2], None))
                    polygons.append(_Polygon(vCurv))
                elif t2 == _np.pi :   # if south pole (triangleS)
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1], None))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2], None))
                    vCurv.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1], None))
                    polygons.append(_Polygon(vCurv))
                else :                      # normal curved quad
                    vCurv = []
                    vCurv.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1], None))
                    vCurv.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2], None))
                    vCurv.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2], None))
                    vCurv.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1], None))
                    polygons.append(_Polygon(vCurv))

                if pRmin != 0:
                    if t1 == 0:  # if north pole (triangles)
                        vCurv = []
                        vCurv.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1], None))
                        vCurv.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2], None))
                        vCurv.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2], None))
                        polygons.append(_Polygon(vCurv))
                    elif t2 == _np.pi:  # if south pole
                        vCurv = []
                        vCurv.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1], None))
                        vCurv.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2], None))
                        vCurv.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1], None))
                        polygons.append(_Polygon(vCurv))
                    else:  # normal curved quad
                        vCurv = []
                        vCurv.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1], None))
                        vCurv.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2], None))
                        vCurv.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2], None))
                        vCurv.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1], None))
                        polygons.append(_Polygon(vCurv))

        # checking pole to pole angle coverage
        if (pDTheta - pSTheta) != 2 * _np.pi:

            # if north pole dont mesh as will be degen
            if (pSTheta != 0 ) and (pSTheta != 2*_np.pi):

                for i0 in range(0, self.nslice, 1):
                    i1 = i0
                    i2 = i0 + 1

                    x1_inner = pRmin * _np.sin(pSTheta) * _np.cos(dPhi * i1 + pSPhi)
                    y1_inner = pRmin * _np.sin(pSTheta) * _np.sin(dPhi * i1 + pSPhi)
                    z1_inner = pRmin * _np.cos(pSTheta)

                    x2_inner = pRmin * _np.sin(pSTheta) * _np.cos(dPhi * i2 + pSPhi)
                    y2_inner = pRmin * _np.sin(pSTheta) * _np.sin(dPhi * i2 + pSPhi)
                    z2_inner = pRmin * _np.cos(pSTheta)

                    x2_outer = pRmax * _np.sin(pSTheta) * _np.cos(dPhi * i2 + pSPhi)
                    y2_outer = pRmax * _np.sin(pSTheta) * _np.sin(dPhi * i2 + pSPhi)
                    z2_outer = pRmax * _np.cos(pSTheta)

                    x1_outer = pRmax * _np.sin(pSTheta) * _np.cos(dPhi * i1 + pSPhi)
                    y1_outer = pRmax * _np.sin(pSTheta) * _np.sin(dPhi * i1 + pSPhi)
                    z1_outer = pRmax * _np.cos(pSTheta)

                    vertices_wedges_S = [] # leading face

                    vertices_wedges_S.append(_Vertex([x1_inner, y1_inner, z1_inner], None))
                    vertices_wedges_S.append(_Vertex([x2_inner, y2_inner, z2_inner], None))
                    vertices_wedges_S.append(_Vertex([x2_outer, y2_outer, z2_outer], None))
                    vertices_wedges_S.append(_Vertex([x1_outer, y1_outer, z1_outer], None))

                    polygons.append(_Polygon(vertices_wedges_S))

                #############################################################################

            # if south pole dont mesh as will be degen
            if (pDTheta != 0) and (pDTheta != 2 * _np.pi):

                for i0 in range(0, self.nslice, 1):
                    i1 = i0
                    i2 = i0 + 1

                    x4_outer = pRmax * _np.sin(pDTheta) * _np.cos(dPhi * i1 + pSPhi)
                    y4_outer = pRmax * _np.sin(pDTheta) * _np.sin(dPhi * i1 + pSPhi)
                    z4_outer = pRmax * _np.cos(pDTheta)

                    x3_outer = pRmax * _np.sin(pDTheta) * _np.cos(dPhi * i2 + pSPhi)
                    y3_outer = pRmax * _np.sin(pDTheta) * _np.sin(dPhi * i2 + pSPhi)
                    z3_outer = pRmax * _np.cos(pDTheta)

                    x3_inner = pRmin * _np.sin(pDTheta) * _np.cos(dPhi * i2 + pSPhi)
                    y3_inner = pRmin * _np.sin(pDTheta) * _np.sin(dPhi * i2 + pSPhi)
                    z3_inner = pRmin * _np.cos(pDTheta)

                    x4_inner = pRmin * _np.sin(pDTheta) * _np.cos(dPhi * i1 + pSPhi)
                    y4_inner = pRmin * _np.sin(pDTheta) * _np.sin(dPhi * i1 + pSPhi)
                    z4_inner = pRmin * _np.cos(pDTheta)

                    vertices_wedges_D = [] # ending face

                    vertices_wedges_D.append(_Vertex([x4_outer, y4_outer, z4_outer], None))
                    vertices_wedges_D.append(_Vertex([x3_outer, y3_outer, z3_outer], None))
                    vertices_wedges_D.append(_Vertex([x3_inner, y3_inner, z3_inner], None))
                    vertices_wedges_D.append(_Vertex([x4_inner, y4_inner, z4_inner], None))

                    polygons.append(_Polygon(vertices_wedges_D))

        # checking equator angle coverage
        if (pDPhi - pSPhi) != _np.pi:

            for i0 in range(self.nstack):
                i1 = i0
                i2 = i0 + 1

                x1_inner = pRmin * _np.sin(dTheta * i1 + pSTheta) * _np.cos(pSPhi)
                y1_inner = pRmin * _np.sin(dTheta * i1 + pSTheta) * _np.sin(pSPhi)
                z1_inner = pRmin * _np.cos(dTheta * i1 + pSTheta)

                x2_inner = pRmin * _np.sin(dTheta * i2 + pSTheta) * _np.cos(pSPhi)
                y2_inner = pRmin * _np.sin(dTheta * i2 + pSTheta) * _np.sin(pSPhi)
                z2_inner = pRmin * _np.cos(dTheta * i2 + pSTheta)

                x2_outer = pRmax * _np.sin(dTheta * i2 + pSTheta) * _np.cos(pSPhi)
                y2_outer = pRmax * _np.sin(dTheta * i2 + pSTheta) * _np.sin(pSPhi)
                z2_outer = pRmax * _np.cos(dTheta * i2 + pSTheta)

                x1_outer = pRmax * _np.sin(dTheta * i1 + pSTheta) * _np.cos(pSPhi)
                y1_outer = pRmax * _np.sin(dTheta * i1 + pSTheta) * _np.sin(pSPhi)
                z1_outer = pRmax * _np.cos(dTheta * i1 + pSTheta)

                vertices_wedges_S = [] # leading face

                vertices_wedges_S.append(_Vertex([x1_inner, y1_inner, z1_inner], None))
                vertices_wedges_S.append(_Vertex([x2_inner, y2_inner, z2_inner], None))
                vertices_wedges_S.append(_Vertex([x2_outer, y2_outer, z2_outer], None))
                vertices_wedges_S.append(_Vertex([x1_outer, y1_outer, z1_outer], None))

                polygons.append(_Polygon(vertices_wedges_S))

                #############################################################################

                x4_outer = pRmax * _np.sin(dTheta * i1 + pSTheta) * _np.cos(pDPhi)
                y4_outer = pRmax * _np.sin(dTheta * i1 + pSTheta) * _np.sin(pDPhi)
                z4_outer = pRmax * _np.cos(dTheta * i1 + pSTheta)

                x3_outer = pRmax * _np.sin(dTheta * i2 + pSTheta) * _np.cos(pDPhi)
                y3_outer = pRmax * _np.sin(dTheta * i2 + pSTheta) * _np.sin(pDPhi)
                z3_outer = pRmax * _np.cos(dTheta * i2 + pSTheta)

                x3_inner = pRmin * _np.sin(dTheta * i2 + pSTheta) * _np.cos(pDPhi)
                y3_inner = pRmin * _np.sin(dTheta * i2 + pSTheta) * _np.sin(pDPhi)
                z3_inner = pRmin * _np.cos(dTheta * i2 + pSTheta)

                x4_inner = pRmin * _np.sin(dTheta * i1 + pSTheta) * _np.cos(pDPhi)
                y4_inner = pRmin * _np.sin(dTheta * i1 + pSTheta) * _np.sin(pDPhi)
                z4_inner = pRmin * _np.cos(dTheta * i1 + pSTheta)

                vertices_wedges_D = [] # ending face

                vertices_wedges_D.append(_Vertex([x4_outer, y4_outer, z4_outer], None))
                vertices_wedges_D.append(_Vertex([x3_outer, y3_outer, z3_outer], None))
                vertices_wedges_D.append(_Vertex([x3_inner, y3_inner, z3_inner], None))
                vertices_wedges_D.append(_Vertex([x4_inner, y4_inner, z4_inner], None))

                polygons.append(_Polygon(vertices_wedges_D))

        mesh = _CSG.fromPolygons(polygons)
        return mesh