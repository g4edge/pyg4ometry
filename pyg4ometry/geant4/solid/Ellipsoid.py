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
                 pzBottomCut, pzTopCut, registry, lunit = "mm",
                 nslice=8, nstack=8, addRegistry=True):
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

        self.varNames = ["pxSemiAxis", "pySemiAxis", "pzSemiAxis","pzBottomCut","pzTopCut"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Ellipsoid : {} {} {} {} {} {}".format(self.name, self.pxSemiAxis,
                                                      self.pySemiAxis, self.pzSemiAxis,
                                                      self.pzBottomCut, self.pzTopCut)

    def pycsgmeshOld(self):

        _log.info('ellipsoid.pycsgmesh>')
        basicmesh = self.basicmesh()
        mesh = self.csgmesh(basicmesh)

        return mesh

    def basicmesh(self):

        _log.info('ellipsoid.antlr>')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pxSemiAxis = self.evaluateParameter(self.pxSemiAxis)*luval
        pySemiAxis = self.evaluateParameter(self.pySemiAxis)*luval
        pzSemiAxis = self.evaluateParameter(self.pzSemiAxis)*luval

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

    def pycsgmesh(self):
        _log.info("ellipsoid.antlr>")

        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        luval = _Units.unit(self.lunit)

        pxSemiAxis  = self.evaluateParameter(self.pxSemiAxis) * luval
        pySemiAxis  = self.evaluateParameter(self.pySemiAxis) * luval
        pzSemiAxis  = self.evaluateParameter(self.pzSemiAxis) * luval
        pzBottomCut = float(self.pzBottomCut) * luval
        pzTopCut    = float(self.pzTopCut)    * luval

        _log.info("ellipsoid.pycsgmesh>")
        polygons = []

        slices = self.nslice
        stacks = self.nstack

        dTheta = 2 * _np.pi / self.nslice

        PhiTop =          _np.arccos(pzTopCut   / pzSemiAxis)
        PhiBot = _np.pi - _np.arccos(pzBottomCut/-pzSemiAxis)

      #  PhiTop = 0.5
      #   PhiBot = 3

       # TopRadius = _np.srt( (pxSemiAxis * np_cos())**2 * (pySemiAxis * _np.sin())**2)

        # yt = (pySemiAxis*_np.sqrt(1-(pzTopCut/pzSemiAxis)**2))
        # xt = (pxSemiAxis*_np.sqrt(1-(pzTopCut/pzSemiAxis)**2))
        # rt = _np.sqrt(xt**2 + yt**2)
        #
        # PhiTop = _np.arctan(rt/pzTopCut)




        dPhi = (PhiBot - PhiTop) / stacks

        # print('TOP = {}, BOT = {}, yt = {}, xt = {}, rt = {},{}'.format(PhiTop,PhiBot,yt,xt,rt,(pzTopCut/pzSemiAxis)**2))


        for i0 in range(0,slices):
            i1 = i0
            i2 = i0 + 1

            if PhiBot < _np.pi:

                i1 = i0
                i2 = i0 + 1

                vertices = []

               # PhiBot = -_np.arcsin(pzBottomCut/pzSemiAxis)

                x1 = pxSemiAxis * _np.sin(PhiBot) * _np.cos(i1 * dTheta)
                y1 = pySemiAxis * _np.sin(PhiBot) * _np.sin(i1 * dTheta)
                z1 = pzBottomCut

                x2 = 0
                y2 = 0
                z2 = pzBottomCut

                x3 = pxSemiAxis * _np.sin(PhiBot) * _np.cos(i2 * dTheta)
                y3 = pySemiAxis * _np.sin(PhiBot) * _np.sin(i2 * dTheta)
                z3 = pzBottomCut

                vertices.append(_Vertex([x1, y1, z1], None))
                vertices.append(_Vertex([x2, y2, z2], None))
                vertices.append(_Vertex([x3, y3, z3], None))

                polygons.append(_Polygon(vertices))

            if PhiTop > 0:

                i1 = i0
                i2 = i0 + 1

                vertices = []

                x1 = pxSemiAxis * _np.sin(PhiTop) * _np.cos(i1 * dTheta)
                y1 = pySemiAxis * _np.sin(PhiTop) * _np.sin(i1 * dTheta)
                z1 = pzTopCut

                x2 = pxSemiAxis * _np.sin(PhiTop) * _np.cos(i2 * dTheta)
                y2 = pySemiAxis * _np.sin(PhiTop) * _np.sin(i2 * dTheta)
                z2 = pzTopCut

                x3 = 0
                y3 = 0
                z3 = pzTopCut

                vertices.append(_Vertex([x1, y1, z1], None))
                vertices.append(_Vertex([x2, y2, z2], None))
                vertices.append(_Vertex([x3, y3, z3], None))

                polygons.append(_Polygon(vertices))

            for j0 in range(stacks):
                j1 = j0
                j2 = j0 + 1

                x1 = pxSemiAxis * _np.sin((j1 * dPhi) + PhiTop) * _np.cos(i1 * dTheta)
                y1 = pySemiAxis * _np.sin((j1 * dPhi) + PhiTop) * _np.sin(i1 * dTheta)
                z1 = pzSemiAxis * _np.cos((j1 * dPhi) + PhiTop)

                x2 = pxSemiAxis * _np.sin((j2 * dPhi) + PhiTop) * _np.cos(i1 * dTheta)
                y2 = pySemiAxis * _np.sin((j2 * dPhi) + PhiTop) * _np.sin(i1 * dTheta)
                z2 = pzSemiAxis * _np.cos((j2 * dPhi) + PhiTop)

                x3 = pxSemiAxis * _np.sin((j2 * dPhi) + PhiTop) * _np.cos(i2 * dTheta)
                y3 = pySemiAxis * _np.sin((j2 * dPhi) + PhiTop) * _np.sin(i2 * dTheta)
                z3 = pzSemiAxis * _np.cos((j2 * dPhi) + PhiTop)

                x4 = pxSemiAxis * _np.sin((j1 * dPhi) + PhiTop) * _np.cos(i2 * dTheta)
                y4 = pySemiAxis * _np.sin((j1 * dPhi) + PhiTop) * _np.sin(i2 * dTheta)
                z4 = pzSemiAxis * _np.cos((j1 * dPhi) + PhiTop)

                vertices = []

                vertices.append(_Vertex([x1, y1, z1], None))
                vertices.append(_Vertex([x2, y2, z2], None))
                vertices.append(_Vertex([x3, y3, z3], None))
                vertices.append(_Vertex([x4, y4, z4], None))

                polygons.append(_Polygon(vertices))

        mesh = _CSG.fromPolygons(polygons)

        return mesh