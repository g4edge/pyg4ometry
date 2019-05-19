from SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon
from Plane import Plane as _Plane
import logging as _log

import numpy as _np

class Ellipsoid(_SolidBase):

    """
    Constructs an ellipsoid optinoally cut by planes perpendicular to the z-axis.
    
    :param name:        of the solid
    :type name:         str
    :param pxSemiAxis:  length of x semi axis
    :type pxSemiAxis:   float, Constant, Quantity, Variable, Expression
    :param pySemiAxis:  length of y semi axis
    :type pySemiAxis:   float, Constant, Quantity, Variable, Expression
    :param pzSemiAxis:  length of z semi axis
    :type pzSemiAxis:   float, Constant, Quantity, Variable, Expression
    :param pzBottomCut: z-position of bottom cut plane
    :type pzBottomCut:  float, Constant, Quantity, Variable, Expression
    :param pzTopCut:    z-position of top cut plane
    :type pzTopCut:     float, Constant, Quantity, Variable, Expression
    :param registry:    for storing solid
    :type registry:     Registry
    :param lunit:       length unit (nm,um,mm,m,km) for solid
    :type lunit:        str
    :param nslice:      number of phi elements for meshing
    :type nslice:       int  
    :param nstack:      number of theta elements for meshing
    :type nstack:       int         
    """


    def __init__(self, name, pxSemiAxis, pySemiAxis, pzSemiAxis,
                 pzBottomCut, pzTopCut, registry=None, lunit = "mm", nslice=8, nstack=8):
        self.type        = 'Ellipsoid'
        self.name        = name
        self.pxSemiAxis  = pxSemiAxis
        self.pySemiAxis  = pySemiAxis
        self.pzSemiAxis  = pzSemiAxis
        self.pzBottomCut = pzBottomCut
        self.pzTopCut    = pzTopCut
        self.lunit       = lunit
        self.nslice      = nslice
        self.nstack      = nstack
        self.mesh      = None
        self.dependents = []
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Ellipsoid : {} {} {} {} {} {}".format(self.name, self.pxSemiAxis,
                                                      self.pySemiAxis, self.pzSemiAxis,
                                                      self.pzBottomCut, self.pzTopCut)

    def pycsgmesh(self):

        _log.info('ellipsoid.pycsgmesh>')
        basicmesh = self.basicmesh()
        mesh = self.csgmesh(basicmesh)

        return mesh

    def basicmesh(self):

        _log.info('ellipsoid.antlr>')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pxSemiAxis = float(self.pxSemiAxis)*luval
        pySemiAxis = float(self.pySemiAxis)*luval
        pzSemiAxis = float(self.pzSemiAxis)*luval

        _log.info('ellipsoid.basicmesh>')
        def appendVertex(vertices, u, v):
            d = _Vector(
                pxSemiAxis*_np.cos(u)*_np.sin(v),
                pySemiAxis*_np.cos(u)*_np.cos(v),
                pzSemiAxis*_np.sin(u))

            vertices.append(_Vertex(c.plus(d), None))

        polygons = []

        c      = _Vector([0,0,0])
        slices = self.nslice
        stacks = self.nstack

        du     = _np.pi / float(slices)
        dv     = 2*_np.pi / float(stacks)

        su     = -_np.pi/2
        sv     = -_np.pi

        for j0 in range(0, slices):
            j1 = j0 + 0.5
            j2 = j0 + 1
            for i0 in range(0, slices):
                i1 = i0 + 0.5
                i2 = i0 + 1

                verticesN = []
                appendVertex(verticesN, i1 * du + su, j1 * dv + sv)
                appendVertex(verticesN, i2 * du + su, j2 * dv + sv)
                appendVertex(verticesN, i0 * du + su, j2 * dv + sv)
                polygons.append(_Polygon(verticesN))
                verticesS = []
                appendVertex(verticesS, i1 * du + su, j1 * dv + sv)
                appendVertex(verticesS, i0 * du + su, j0 * dv + sv)
                appendVertex(verticesS, i2 * du + su, j0 * dv + sv)
                polygons.append(_Polygon(verticesS))
                verticesW = []
                appendVertex(verticesW, i1 * du + su, j1 * dv + sv)
                appendVertex(verticesW, i0 * du + su, j2 * dv + sv)
                appendVertex(verticesW, i0 * du + su, j0 * dv + sv)
                polygons.append(_Polygon(verticesW))
                verticesE = []
                appendVertex(verticesE, i1 * du + su, j1 * dv + sv)
                appendVertex(verticesE, i2 * du + su, j0 * dv + sv)
                appendVertex(verticesE, i2 * du + su, j2 * dv + sv)
                polygons.append(_Polygon(verticesE))

        self.mesh  = _CSG.fromPolygons(polygons)

        return self.mesh

    def csgmesh(self, basicmesh):
        _log.info('ellipsoid.antlr>')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pzBottomCut = float(self.pzBottomCut)*luval
        pzTopCut    = float(self.pzTopCut)*luval

        _log.info('ellipsoid.csgmesh>')
        topNorm     = _Vector(0,0,1)                              # These are tests of booleans operations, keep here for now
        botNorm     = _Vector(0,0,-1)
        pTopCut     = _Plane("pTopCut", topNorm, pzTopCut).pycsgmesh()
        pBottomCut  = _Plane("pBottomCut", botNorm, pzBottomCut).pycsgmesh()
        mesh   = basicmesh.subtract(pBottomCut).subtract(pTopCut)

        return mesh
