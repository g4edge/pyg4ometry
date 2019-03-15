from SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon
from Plane import Plane as _Plane
import logging as _log

import numpy as _np

class Ellipsoid(_SolidBase):
    def __init__(self, name, pxSemiAxis, pySemiAxis, pzSemiAxis,
                 pzBottomCut, pzTopCut, registry=None, nslice=8, nstack=8):
        """
        Constructs an ellipsoid optinoally cut by planes perpendicular to the z-axis.

        Inputs:
          name:    string, name of the volume
          pxSemiAxis:  float, length of x semi axis
          pySemiAxis:  float, length of y semi axis
          pzSemiAxis:  float, length of z semi axis
          pzBottomCut: float, z-position of bottom cut plane
          pzTopCut:    float, z-position of top cut plane
        """
        self.type        = 'Ellipsoid'
        self.name        = name
        self.pxSemiAxis  = pxSemiAxis
        self.pySemiAxis  = pySemiAxis
        self.pzSemiAxis  = pzSemiAxis
        self.pzBottomCut = pzBottomCut
        self.pzTopCut    = pzTopCut
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
        pxSemiAxis = float(self.pxSemiAxis)
        pySemiAxis = float(self.pySemiAxis)
        pzSemiAxis = float(self.pzSemiAxis)

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
        pzBottomCut = float(self.pzBottomCut)
        pzTopCut = float(self.pzTopCut)

        _log.info('ellipsoid.csgmesh>')
        topNorm     = _Vector(0,0,1)                              # These are tests of booleans operations, keep here for now
        botNorm     = _Vector(0,0,-1)
        pTopCut     = _Plane("pTopCut", topNorm, pzTopCut).pycsgmesh()
        pBottomCut  = _Plane("pBottomCut", botNorm, pzBottomCut).pycsgmesh()
        mesh   = basicmesh.subtract(pBottomCut).subtract(pTopCut)

        return mesh
