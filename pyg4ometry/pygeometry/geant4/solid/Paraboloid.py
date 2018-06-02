from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Polygon as _Polygon
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
import numpy as _np

class Paraboloid(_SolidBase) :
    def __init__(self, name, pDz, pR1, pR2, nstack=8, nslice=16) :
        """
        Constructs a paraboloid with possible cuts along the z axis. 

        Inputs:
          name: string, name of the volume
          pDz:  float, half-length along z
          pR1:  float, radius at -Dz
          pR2:  float, radius at +Dz (R2 > R1)   
        """
        self.type   = 'Paraboloid'
        self.name   = name
        self.pDz    = pDz
        self.pR1    = pR1
        self.pR2    = pR2
        self.nstack = nstack
        self.nslice = nslice
        _registry.addSolid(self)        
    
    def pycsgmesh(self):
        polygons = []
        
        sz      = -self.pDz
        dz      = 2*self.pDz/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        K1 = (self.pR2**2-self.pR1**2)/(2*self.pDz)
        K2 = (self.pR2**2+self.pR1**2)/2

        def appendVertex(vertices, theta, z, k1=K1, k2=K2, norm=[]):
            if k1 and k2:
                rho = _np.sqrt(k1*z+k2)
            else:
                rho = 0
                
            c = _Vector([0,0,0])
            x = rho*_np.cos(theta)
            y = rho*_np.sin(theta)

            d = _Vector(
                x,
                y,
                z)
            
            if not norm:
                n = d
            else:
                n = _Vector(norm)
            vertices.append(_Vertex(c.plus(d), d))


        for j0 in range(stacks):
            j1 = j0 + 0.5
            j2 = j0 + 1
            for i0 in range(slices):
                i1 = i0 + 0.5
                i2 = i0 + 1
                verticesN = []
                appendVertex(verticesN, i1 * dTheta, j1 * dz + sz)
                appendVertex(verticesN, i2 * dTheta, j2 * dz + sz)
                appendVertex(verticesN, i0 * dTheta, j2 * dz + sz)
                polygons.append(_Polygon(verticesN))
                verticesS = []
                appendVertex(verticesS, i1 * dTheta, j1 * dz + sz)
                appendVertex(verticesS, i0 * dTheta, j0 * dz + sz)
                appendVertex(verticesS, i2 * dTheta, j0 * dz + sz)
                polygons.append(_Polygon(verticesS))
                verticesW = []
                appendVertex(verticesW, i1 * dTheta, j1 * dz + sz)
                appendVertex(verticesW, i0 * dTheta, j2 * dz + sz)
                appendVertex(verticesW, i0 * dTheta, j0 * dz + sz)
                polygons.append(_Polygon(verticesW))
                verticesE = []
                appendVertex(verticesE, i1 * dTheta, j1 * dz + sz)
                appendVertex(verticesE, i2 * dTheta, j0 * dz + sz)
                appendVertex(verticesE, i2 * dTheta, j2 * dz + sz)
                polygons.append(_Polygon(verticesE))
        
        for i0 in range(0, slices):
            i1 = i0 + 1
            
            vertices = []
            
            appendVertex(vertices, i0 * dTheta, sz)
            appendVertex(vertices, 0, sz, k1 = 0) #Setting K1=0 forces a zero vector which is used as the center
            appendVertex(vertices, i1 * dTheta, sz)
            polygons.append(_Polygon(vertices))

            vertices = []
            appendVertex(vertices, i1 * dTheta, stacks * dz + sz)
            appendVertex(vertices, 0, stacks*dz + sz, k1 = 0)
            appendVertex(vertices, i0 * dTheta, stacks * dz + sz)
            polygons.append(_Polygon(vertices))
         
        self.mesh  = _CSG.fromPolygons(polygons)
    
        return self.mesh

    
