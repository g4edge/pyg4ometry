from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np

class EllipticalCone(_SolidBase):
    def __init__(self, name, pxSemiAxis, pySemiAxis, zMax, pzTopCut,
                 nslice=16, nstack=16, register=True):
        """
        Constructs a cone with elliptical cross-section.

        Inputs:
          name:       string, name of the volume
          pxSemiAxis: float, semiaxis in x (fraction of zMax)
          pySemiAxis: float, semiaxis in y (fraction of zMax)
          zMax:       float, height of cone
          pzTopCut:   float, z-position of upper
        """

        self.type       = 'EllipticalCone'
        self.name       = name
        self.pxSemiAxis = pxSemiAxis
        self.pySemiAxis = pySemiAxis
        self.zMax       = zMax
        self.pzTopCut   = pzTopCut
        self.nslice     = nslice
        self.nstack     = nslice
        self.checkParameters()
        if register:
            _registry.addSolid(self)

    def checkParameters(self):
        if self.pzTopCut <= 0 or self.pzTopCut > self.zMax:
            raise ValueError("zMax must be greater than pzTopCut")

    def pycsgmesh(self):
        polygons = []

        sz      = -self.zMax/2.
        dz      = self.zMax/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        # semix and semiy are fractions of zmax - calculate absolute numbers
        dxabs = self.pxSemiAxis * self.zMax
        dyabs = self.pySemiAxis * self.zMax

        def appendVertex(vertices, theta, z, dx=dxabs, dy=dyabs, norm=[]):
            c = _Vector([0,0,0])
            x = dx*(((self.zMax - z)/self.zMax)*_np.cos(theta)) #generate points on an ellipse
            y = dy*(((self.zMax - z)/self.zMax)*_np.sin(theta))
            d = _Vector(
                x,
                y,
                z)
            if not norm:
                n = d
            else:
                n = _Vector(norm)
            vertices.append(_Vertex(c.plus(d), n))


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
