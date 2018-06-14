from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np

class EllipticalTube(_SolidBase):
    def __init__(self, name, pDx, pDy, pDz, nslice=16, nstack=16, register=True):
        """
        Constructs a tube of elliptical cross-section.

        Inputs:
          name: string, name of the volume
          pDx:  float, half-length in x
          pDy:  float, half-length in y
          pDz:  float, half-length in z
        """
        self.type   = 'EllipticalTube'
        self.name   = name
        self.pDx    = pDx
        self.pDy    = pDy
        self.pDz    = pDz
        self.nslice = nslice
        self.nstack = nstack
        if register:
            _registry.addSolid(self)

    def pycsgmesh(self):
        polygons = []

        sz      = -self.pDz
        dz      = 2*self.pDz/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        def appendVertex(vertices, theta, z, dx=self.pDx, dy=self.pDy, norm=[]):
            c = _Vector([0,0,0])
            x = dx*_np.cos(theta)
            y = dy*_np.sin(theta)

            d = _Vector(
                x,
                y,
                z)

            if not norm:
                n = d
            else:
                n = _Vector(norm)
            vertices.append(_Vertex(c.plus(d), d))


        for j0 in range(slices):
            j1 = j0 + 0.5
            j2 = j0 + 1
            for i0 in range(stacks):
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

            appendVertex(vertices, i0 * dTheta, sz, norm=[0,0,1])
            appendVertex(vertices, 0, sz, dx=0, dy=0, norm=[0,0,1])
            appendVertex(vertices, i1 * dTheta, sz, norm=[0,0,1])
            polygons.append(_Polygon(vertices))

            vertices = []
            appendVertex(vertices, i1 * dTheta, stacks * dz + sz, norm=[0,0,-1])
            appendVertex(vertices, 0, slices*dz + sz, dx=0, dy=0, norm=[0,0,-1])
            appendVertex(vertices, i0 * dTheta, stacks * dz + sz, norm=[0,0,-1])
            polygons.append(_Polygon(vertices))

        self.mesh  = _CSG.fromPolygons(polygons)

        return self.mesh
