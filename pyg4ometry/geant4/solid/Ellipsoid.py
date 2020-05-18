from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

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

        self.dependents = []

        self.varNames = ["pxSemiAxis", "pySemiAxis", "pzSemiAxis","pzBottomCut","pzTopCut"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Ellipsoid : {} {} {} {} {} {}".format(self.name, self.pxSemiAxis,
                                                      self.pySemiAxis, self.pzSemiAxis,
                                                      self.pzBottomCut, self.pzTopCut)

    def mesh(self):
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

        # If cuts lay outside of the ellipsoid then don't do any cut.
        if pzTopCut > pzSemiAxis:
            pzTopCut = pzSemiAxis
        if pzBottomCut < -pzSemiAxis:
            pzBottomCut = -pzSemiAxis

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

                vertices.append(_Vertex([x1, y1, z1]))
                vertices.append(_Vertex([x2, y2, z2]))
                vertices.append(_Vertex([x3, y3, z3]))

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

                vertices.append(_Vertex([x1, y1, z1]))
                vertices.append(_Vertex([x2, y2, z2]))
                vertices.append(_Vertex([x3, y3, z3]))

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

                vertices.append(_Vertex([x1, y1, z1]))
                vertices.append(_Vertex([x2, y2, z2]))
                vertices.append(_Vertex([x3, y3, z3]))
                vertices.append(_Vertex([x4, y4, z4]))

                polygons.append(_Polygon(vertices))

        return _CSG.fromPolygons(polygons)

