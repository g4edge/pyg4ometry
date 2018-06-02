from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Polygon as _Polygon
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
import numpy as _np
import sys as _sys
from copy import deepcopy as _dc

class Sphere(_SolidBase) :
    def __init__(self, name, pRmin, pRmax, pSPhi, pDPhi, pSTheta, pDTheta, nslice = 10, nstack = 10) :
        """
        Constructs a section of a spherical shell. 

        Inputs:
          name:    string, name of the volume
          pRmin:   float, innner radius of the shell
          pRmax:   float, outer radius of the shell
          pSPhi:   float, starting phi angle in radians
          pSTheta: float, starting theta angle in radians
          pDPhi:   float, total phi angle in radians 0 to 2 pi
          pDTheta: float, total theta angle in radians 0 to pi

        Phi & Theta are the usual spherical coodrinates.
        """
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
        self.mesh    = None
        _registry.addSolid(self)
        self.checkParameters()

    def checkParameters(self):
        if self.pRmin > self.pRmax:
            raise ValueError("Inner radius must be less than outer radius.")
        if self.pDTheta > _np.pi:
            raise ValueError("pDTheta must be less than pi")
        if self.pDPhi > _np.pi*2:
            raise ValueError("pDPhi must be less than 2 pi")
        
    def __repr__(self):
        return 'Sphere : '+self.name+' '+str(self.pRmin)+' '+str(self.pRmax)+' '+str(self.pSPhi)+' '+str(self.pDPhi)+' '+str(self.pSTheta)+' '+str(self.pDTheta)+' '+str(self.nslice)+' '+str(self.nstack)
    
    def pycsgmesh(self):

        #Called as a csgmesh for profiling
        self.csgmesh()

        return self.mesh


    def csgmesh(self) :

        thetaFin = self.pSTheta + self.pDTheta
        phiFin   = self.pSPhi + self.pDPhi

        self.mesh = _CSG.sphere(radius=self.pRmax, slices=self.nslice, stacks=self.nstack)

        #makes shell by removing a sphere of radius pRmin from the inside of sphere
        if self.pRmin:
            mesh_inner = _CSG.sphere(radius=self.pRmin, slices=self.nslice, stacks=self.nstack)
            self.mesh = self.mesh.subtract(mesh_inner)

            
        #Theta change: allows for different theta angles, using primtives: cube and cone.
        if thetaFin == _np.pi/2.:
            mesh_box = _CSG.cube(center=[0,0,1.1*self.pRmax], radius=1.1*self.pRmax)
            self.mesh = self.mesh.subtract(mesh_box)

        if thetaFin > _np.pi/2. and thetaFin < _np.pi:
            mesh_lower = _CSG.cone(start=[0,0,-2*self.pRmax], end=[0,0,0], radius=2*self.pRmax*_np.tan(_np.pi - thetaFin))
            self.mesh = self.mesh.subtract(mesh_lower)

        if self.pSTheta > _np.pi/2. and self.pSTheta < _np.pi:
            mesh_lower2 = _CSG.cone(start=[0,0,-2*self.pRmax], end=[0,0,0], radius=2*self.pRmax*_np.tan(_np.pi - self.pSTheta))
            self.mesh = self.mesh.intersect(mesh_lower2)

        if thetaFin < _np.pi/2.:
            mesh_upper = _CSG.cone(start=[0,0,2*self.pRmax], end=[0,0,0], radius=2*self.pRmax*_np.tan(thetaFin))
            self.mesh = self.mesh.intersect(mesh_upper)

        if self.pSTheta < _np.pi/2. and self.pSTheta > 0:
            mesh_upper2 = _CSG.cone(start=[0,0,2*self.pRmax], end=[0,0,0], radius=2*self.pRmax*_np.tan(self.pSTheta))
            self.mesh = self.mesh.subtract(mesh_upper2)

            
        #Phi change: allows for different theta angles, using the Wedge solid class
        if phiFin < 2*_np.pi:
            mesh_wedge = _Wedge("wedge_temp", 2*self.pRmax, self.pSPhi, self.pDPhi, 3*self.pRmax).pycsgmesh()
            self.mesh = self.mesh.intersect(mesh_wedge)
        
        return self.mesh
