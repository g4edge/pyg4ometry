from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon
import logging as _log

import numpy as _np

class EllipticalTube(_SolidBase):
    """
    Constructs a tube of elliptical cross-section.
    
    :param name: name of the solid
    :type name:  str
    :param pDx:  length in x
    :type pDx:   float, Constant, Quantity, Variable, Expression
    :param pDy:  length in y
    :type pDy:   float, Constant, Quantity, Variable, Expression
    :param pDz:  length in z
    :type pDz:   float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    :param nstack: number of theta elements for meshing
    :type nstack: int     
    
    """
    

    def __init__(self, name, pDx, pDy, pDz, registry, lunit="mm",
                 nslice=6, nstack=6, addRegistry=True):

        self.type   = 'EllipticalTube'
        self.name   = name
        self.pDx    = pDx
        self.pDy    = pDy
        self.pDz    = pDz
        self.lunit  = lunit
        self.nslice = nslice
        self.nstack = nstack

        self.dependents = []

        self.varNames = ["pDx", "pDy", "pDz"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "EllipticalTube : {} {} {} {}".format(self.name, self.pDx,
                                                     self.pDy, self.pDz)

    def pycsgmesh(self):

        _log.info('ellipticaltube.antlr>')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pDx = self.evaluateParameter(self.pDx)*luval/2.0
        pDy = self.evaluateParameter(self.pDy)*luval/2.0
        pDz = self.evaluateParameter(self.pDz)*luval/2.0

        _log.info('ellipticaltube.pycsgmesh>')
        sz      = -pDz
        dz      = 2*pDz/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        polygons = []

        def appendVertex(vertices, theta, z, dx=pDx, dy=pDy, norm=[]):
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

        mesh  = _CSG.fromPolygons(polygons)

        return mesh
