from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import logging as _log
import numpy as _np

class Paraboloid(_SolidBase):
    """
    Constructs a paraboloid with possible cuts along the z axis.
    
    :param name:     of solid 
    :type name:      str
    :param pDz:      length along z
    :type pDz:       float, Constant, Quantity, Variable, Expression
    :param pR1:      radius at -Dz/2
    :type pR1:       float, Constant, Quantity, Variable, Expression
    :param pR2:      radius at +Dz/2 (pR2 > pR1)
    :type pR2:       float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry:  Registry
    :param lunit:    length unit (nm,um,mm,m,km) for solid
    :type lunit:     str    
    :param nslice:   number of phi elements for meshing
    :type nslice:    int  
    :param nstack:   number of theta elements for meshing
    :type nstack:    int       
    
    """
    
    def __init__(self, name, pDz, pR1, pR2, registry, lunit="mm",
                 nslice=16, nstack=8, addRegistry=True) :

        self.type   = 'Paraboloid'
        self.name   = name
        self.pDz    = pDz
        self.pR1    = pR1
        self.pR2    = pR2
        self.lunit  = lunit
        self.nstack = nstack
        self.nslice = nslice

        self.dependents = []

        self.varNames = ["pDz", "pR1", "pR2"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Paraboloid : {} {} {} {}".format(self.name, self.pDz,
                                                 self.pR1, self.pR2)

    '''
    def pycsgmeshOld(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        _log.info("paraboloid.antlr>")

        uval = _Units.unit(self.lunit)
        pDz    = self.evaluateParameter(self.pDz)/2.0*uval
        pR1    = self.evaluateParameter(self.pR1)*uval
        pR2    = self.evaluateParameter(self.pR2)*uval

        _log.info("paraboloid.pycsgmesh>")
        polygons = []

        sz      = -pDz
        dz      = 2*pDz/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        K1 = (pR2**2-pR1**2)/(2*pDz)
        K2 = (pR2**2+pR1**2)/2

        def appendVertex(vertices, theta, z, k1=K1, k2=K2, norm=[]):
            if k1 and k2:
                rho = _np.sqrt(k1*z+k2)
            else:
                rho = 0

            c = _Vector([0,0,0])
            x = rho*_np.cos(theta)
            y = rho*_np.sin(theta)

            d = _Vector(x,y,z)

#            if not norm:
#                n = d
#            else:
#                n = _Vector(norm)
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
            appendVertex(vertices, 0, sz, k1=0) #Setting K1=0 forces a zero vector which is used as the center
            appendVertex(vertices, i1 * dTheta, sz)
            polygons.append(_Polygon(vertices))

            vertices = []
            appendVertex(vertices, i1 * dTheta, stacks * dz + sz)
            appendVertex(vertices, 0, stacks*dz + sz, k1=0)
            appendVertex(vertices, i0 * dTheta, stacks * dz + sz)
            polygons.append(_Polygon(vertices))

        mesh  = _CSG.fromPolygons(polygons)

        return mesh
    '''

    def pycsgmesh(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import

        _log.info("paraboloid.antlr>")

        uval = _Units.unit(self.lunit)
        pDz    = self.evaluateParameter(self.pDz)/2.0*uval
        pR1    = self.evaluateParameter(self.pR1)*uval
        pR2    = self.evaluateParameter(self.pR2)*uval

        _log.info("paraboloid.pycsgmesh>")
        polygons = []

        sz      = -pDz
        dz      = 2*pDz/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        b = 2*pDz/(pR2**2 - pR1**2)
        a = b*pR1**2 + pDz

        for j0 in range(0,slices):

            j1 = j0
            j2 = j0 + 1

            z1b = sz
            rho1b = _np.sqrt((z1b + a) / b)
            x1b = rho1b * _np.cos(dTheta * j1)
            y1b = rho1b * _np.sin(dTheta * j1)

            z2b = sz
            rho2b = 0
            x2b = rho2b * _np.cos(dTheta * j1)
            y2b = rho2b * _np.sin(dTheta * j1)

            z3b = sz
            rho3b = _np.sqrt((z3b + a) / b)
            x3b = rho3b * _np.cos(dTheta * j2)
            y3b = rho3b * _np.sin(dTheta * j2)

            vertices_Bottom = []

            vertices_Bottom.append(_Vertex([x1b, y1b, z1b], None))
            vertices_Bottom.append(_Vertex([x2b, y2b, z2b], None))
            vertices_Bottom.append(_Vertex([x3b, y3b, z3b], None))

            polygons.append(_Polygon(vertices_Bottom))

            z1t = pDz
            rho1t = pR2
            x1t = rho1t * _np.cos(dTheta * j1)
            y1t = rho1t * _np.sin(dTheta * j1)

            z2t = pDz
            rho2t = pR2
            x2t = rho2t * _np.cos(dTheta * j1)
            y2t = rho2t * _np.sin(dTheta * j1)

            z3t = pDz
            rho3t = 0
            x3t = rho3t * _np.cos(dTheta * j2)
            y3t = rho3t * _np.sin(dTheta * j2)

            vertices_Top = []

            vertices_Top.append(_Vertex([x1t, y1t, z1t], None))
            vertices_Top.append(_Vertex([x2t, y2t, z2t], None))
            vertices_Top.append(_Vertex([x3t, y3t, z3t], None))

            polygons.append(_Polygon(vertices_Top))

            for i0 in range(stacks):
                i1 = i0
                i2 = i0 + 1

                z1 = i1 * dz + sz
                rho = _np.sqrt((z1 + a)/b)
                x1 = rho * _np.cos(dTheta * j1)
                y1 = rho * _np.sin(dTheta * j1)
                z1 = i1 * dz + sz

                z2 = i2 * dz + sz
                rho = _np.sqrt((z2 + a) / b)
                x2 = rho * _np.cos(dTheta * j1)
                y2 = rho * _np.sin(dTheta * j1)

                z3 = i2 * dz + sz
                rho = _np.sqrt((z3 + a) / b)
                x3 = rho * _np.cos(dTheta * j2)
                y3 = rho * _np.sin(dTheta * j2)

                z4 = i1 * dz + sz
                rho = _np.sqrt((z4 + a) / b)
                x4 = rho * _np.cos(dTheta * j2)
                y4 = rho * _np.sin(dTheta * j2)

                vertices = []

                vertices.append(_Vertex([x1, y1, z1], None))
                vertices.append(_Vertex([x2, y2, z2], None))
                vertices.append(_Vertex([x3, y3, z3], None))
                vertices.append(_Vertex([x4, y4, z4], None))

                polygons.append(_Polygon(vertices))

        mesh  = _CSG.fromPolygons(polygons)

        return mesh
