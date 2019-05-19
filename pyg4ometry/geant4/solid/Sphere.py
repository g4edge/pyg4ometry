from   SolidBase import SolidBase as _SolidBase
from   ...pycsg.core import CSG as _CSG
from   ...pycsg.geom import Vertex as _Vertex
from   ...pycsg.geom import Vector as _Vector
from   ...pycsg.geom import Polygon as _Polygon
from   Wedge import Wedge as _Wedge
import numpy as _np
import sys as _sys
from   copy import deepcopy as _dc
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
                 pDTheta, registry=None, lunit="mm", aunit="rad", nslice=10, nstack=10):

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
        self.mesh    = None

        self.dependents = []
        
        # self.checkParameters()
        if registry:
            registry.addSolid(self)

    def checkParameters(self):
        if self.pRmin > self.pRmax:
            raise ValueError("Inner radius must be less than outer radius.")
        if self.pDTheta > _np.pi:
            raise ValueError("pDTheta must be less than pi")
        if self.pDPhi > _np.pi*2:
            raise ValueError("pDPhi must be less than 2 pi")

    def __repr__(self):
        return "Sphere : {} {} {} {} {} {} {}".format(self.name, self.pRmin,
                                                      self.pRmax, self.pSPhi,
                                                      self.pDPhi, self.pSTheta,
                                                      self.pDTheta)

    def pycsgmesh(self):
        _log.info("sphere.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin   = float(self.pRmin)*luval
        pRmax   = float(self.pRmax)*luval
        pSPhi   = float(self.pSPhi)*auval
        pDPhi   = float(self.pDPhi)*auval
        pSTheta = float(self.pSTheta)*auval
        pDTheta = float(self.pDTheta)*auval
        
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
