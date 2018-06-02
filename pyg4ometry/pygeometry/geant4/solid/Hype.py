from SolidBase import SolidBase as _SolidBase
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Polygon as _Polygon
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.Wedge import Wedge as _Wedge
from pygeometry.geant4.solid.Plane import Plane as _Plane
import numpy as _np

class Hype(_SolidBase) :
    def __init__(self, name, innerRadius, outerRadius, innerStereo, outerStereo, halfLenZ, nslice=16, nstack=16) :
        """
        Constructs a tube with hyperbolic profile. 

        Inputs:
          name:        string, name of the volume
          innerRadius: float, inner radius
          outerRadius: float, outer radius
          innerStereo: float, inner stereo angle
          outerStereo: float, outer stereo angle
          halfLenZ:    float, half length along z
        """
        self.type        = 'Hype'
        self.name        = name
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.innerStereo = innerStereo
        self.outerStereo = outerStereo
        self.halfLenZ    = halfLenZ
        self.nslice      = nslice
        self.nstack      = nstack
        _registry.addSolid(self)        

    def checkParameters(self):
        if self.innerRadius > self.outerRadius:
            raise ValueError("Inner radius must be less than outer radius.")

    def pycsgmesh(self):
        dz     = 2*(self.halfLenZ+1.e-6)/self.nstack #make a little bigger as safety for subtractions
        sz     = -self.halfLenZ-1.e-6
        dTheta = 2*_np.pi/self.nslice
        stacks = self.nstack
        slices = self.nslice
        rinout  = [self.innerRadius, self.outerRadius] if self.innerRadius else [self.outerRadius]
        stinout = [self.innerStereo, self.outerStereo]

        polygons = []

        def appendVertex(vertices, theta, z, r, stereo, norm=1):
            c     = _Vector([0,0,0])
            x     = _np.sqrt(r**2+(_np.tan(stereo)*z)**2)
            y     = 0
            x_rot = _np.cos(theta)*x - _np.sin(theta)*y
            y_rot = _np.sin(theta)*x + _np.cos(theta)*y
            
            d = _Vector(
                x_rot,
                y_rot,
                z)
            
            if norm == 0:
                n = None
            if norm == 1:
                n = d
            else:
                n = d.negated()

            vertices.append(_Vertex(c.plus(d), n))
            
        meshinout = []
        for i in range(len(rinout)):
            for j0 in range(stacks):
                j1 = j0 + 0.5
                j2 = j0 + 1
                for i0 in range(slices):
                    nrm = 0
                    
                    i1 = i0 + 0.5
                    i2 = i0 + 1
                    verticesN = []
                    appendVertex(verticesN, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesN, i2 * dTheta, j2 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesN, i0 * dTheta, j2 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    polygons.append(_Polygon(verticesN))
                    verticesS = []
                    appendVertex(verticesS, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesS, i0 * dTheta, j0 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesS, i2 * dTheta, j0 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    polygons.append(_Polygon(verticesS))
                    verticesW = []
                    appendVertex(verticesW, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesW, i0 * dTheta, j2 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesW, i0 * dTheta, j0 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    polygons.append(_Polygon(verticesW))
                    verticesE = []
                    appendVertex(verticesE, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesE, i2 * dTheta, j0 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    appendVertex(verticesE, i2 * dTheta, j2 * dz + sz, rinout[i], stinout[i], norm=nrm)
                    polygons.append(_Polygon(verticesE))

            mesh      = _CSG.fromPolygons(polygons)
            meshinout.append(mesh)
            polygons = []
        
        for i in range(len(meshinout)):
            wzlength     = 3*self.halfLenZ
            topNorm      = _Vector(0,0,1)
            botNorm      = _Vector(0,0,-1)
            pTopCut      = _Plane("pTopCut", topNorm, self.halfLenZ, wzlength).pycsgmesh()
            pBottomCut   = _Plane("pBottomCut" , botNorm, -self.halfLenZ, wzlength).pycsgmesh()
            meshinout[i] = meshinout[i].subtract(pTopCut).subtract(pBottomCut)
        
        if self.innerRadius:
            self.mesh = meshinout[1].subtract(meshinout[0])
        else:
            self.mesh = meshinout[0]
        
        return self.mesh
