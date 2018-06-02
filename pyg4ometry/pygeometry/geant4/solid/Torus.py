from SolidBase import SolidBase as _SolidBase
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Polygon as _Polygon
import numpy as _np


class Torus(_SolidBase) :
    def __init__(self, name, pRmin, pRmax, pRtor, pSPhi, pDPhi, nslice=16, nstack=16) :
        """
        Constructs a torus. 

        Inputs:
          name:   string, name of the volume
          pRmin:  float, innder radius
          pRmax:  float, outer radius
          pRtor:  float, swept radius of torus
          pSphi:  float, start phi angle
          pDPhi:  float, delta angle
        """
        self.type    = 'Torus'
        self.name    = name
        self.pRmin   = pRmin
        self.pRmax   = pRmax
        self.pRtor   = pRtor
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.nslice = nslice
        self.nstack = nstack
        self.mesh = None
        _registry.addSolid(self)


    def pycsgmesh(self):
#        if self.mesh :
#            return self.mesh

        self.basicmesh()
        self.csgmesh()

        return self.mesh

    def basicmesh(self) :
        polygons = []
        
        dTheta  = 2*_np.pi/self.nstack
        dPhi    = 2*_np.pi/self.nslice
        sphi    = self.pSPhi
        stacks  = self.nstack
        slices  = self.nslice 

        def appendVertex(vertices, theta, phi, r):
            c = _Vector([0,0,0])
            x = r*_np.cos(theta)+self.pRtor
            z = r*_np.sin(theta)
            y = 0
            x_rot = _np.cos(phi)*x - _np.sin(phi)*y
            y_rot = _np.sin(phi)*x + _np.cos(phi)*y
            
            d = _Vector(
                x_rot,
                y_rot,
                z)

            vertices.append(_Vertex(c.plus(d), None))
            
        rinout    = [self.pRmin, self.pRmax]
        self.meshinout = []
        
        for r in rinout:
            for j0 in range(slices):
                j1 = j0 + 0.5
                j2 = j0 + 1
                for i0 in range(stacks):
                    i1 = i0 + 0.5
                    i2 = i0 + 1
                    verticesN = []
                    appendVertex(verticesN, i1 * dTheta, j1 * dPhi + sphi, r)
                    appendVertex(verticesN, i2 * dTheta, j2 * dPhi + sphi, r)
                    appendVertex(verticesN, i0 * dTheta, j2 * dPhi + sphi, r)
                    polygons.append(_Polygon(verticesN))
                    verticesS = []
                    appendVertex(verticesS, i1 * dTheta, j1 * dPhi + sphi, r)
                    appendVertex(verticesS, i0 * dTheta, j0 * dPhi + sphi, r)
                    appendVertex(verticesS, i2 * dTheta, j0 * dPhi + sphi, r)
                    polygons.append(_Polygon(verticesS))
                    verticesW = []
                    appendVertex(verticesW, i1 * dTheta, j1 * dPhi + sphi, r)
                    appendVertex(verticesW, i0 * dTheta, j2 * dPhi + sphi, r)
                    appendVertex(verticesW, i0 * dTheta, j0 * dPhi + sphi, r)
                    polygons.append(_Polygon(verticesW))
                    verticesE = []
                    appendVertex(verticesE, i1 * dTheta, j1 * dPhi + sphi, r)
                    appendVertex(verticesE, i2 * dTheta, j0 * dPhi + sphi, r)
                    appendVertex(verticesE, i2 * dTheta, j2 * dPhi + sphi, r)
                    polygons.append(_Polygon(verticesE))

            mesh      = _CSG.fromPolygons(polygons)
            self.meshinout.append(mesh)
            polygons = []
            
        
        self.mesh = self.meshinout[1]
        return self.mesh


    def csgmesh(self) :
        if self.pRmin != 0:
            self.mesh  = self.meshinout[0].subtract(self.meshinout[1])
        
        else:
           self.mesh = self.meshinout[1].inverse()

        if self.pDPhi != 2*_np.pi:
            wrmax    = 3*self.pRtor #make sure intersection wedge is much larger than solid
            wzlength = 5*self.pRmax
            
            pWedge = _Wedge("wedge_temp",wrmax, self.pSPhi, self.pDPhi, wzlength).pycsgmesh()
            self.mesh = pWedge.intersect(self.mesh)

        return self.mesh


