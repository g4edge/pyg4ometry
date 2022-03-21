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
                 nslice=None, nstack=None, addRegistry=True):
        super(Ellipsoid, self).__init__(name, 'Ellipsoid', registry)
        self.pxSemiAxis  = pxSemiAxis
        self.pySemiAxis  = pySemiAxis
        self.pzSemiAxis  = pzSemiAxis
        self.pzBottomCut = pzBottomCut
        self.pzTopCut    = pzTopCut
        self.lunit       = lunit
        self.nslice      = nslice if nslice else _config.SolidDefaults.Ellipsoid.nslice
        self.nstack      = nstack if nstack else _config.SolidDefaults.Ellipsoid.nstack

        self.dependents = []

        self.varNames = ["pxSemiAxis", "pySemiAxis", "pzSemiAxis", "pzBottomCut", "pzTopCut"]
        self.varUnits = ["lunit", "lunit", "lunit", "lunit", "lunit"]

        if addRegistry:
            registry.addSolid(self)

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

        slices = self.nslice
        stacks = self.nstack

        # If cuts lay outside of the ellipsoid then don't do any cut.
        if pzTopCut > pzSemiAxis:
            pzTopCut = pzSemiAxis
        if pzBottomCut < -pzSemiAxis:
            pzBottomCut = -pzSemiAxis

        thetaTop =          _np.arccos(pzTopCut   / pzSemiAxis)
        thetaBot = _np.pi - _np.arccos(pzBottomCut/-pzSemiAxis)

        dTheta = (thetaBot - thetaTop) / stacks
        dPhi = 2 * _np.pi / self.nslice

        polygons = []

        for i in range(0,slices):
            i1 = i
            i2 = i + 1

            p1 = dPhi*i1
            p2 = dPhi*i2

            for j in range(0,stacks) :

                j1 = j
                j2 = j + 1

                t1 = dTheta*j1 + thetaTop
                t2 = dTheta*j2 + thetaTop

                x11 = pxSemiAxis * _np.sin(t1) * _np.cos(p1)
                y11 = pySemiAxis * _np.sin(t1) * _np.sin(p1)
                z11 = pzSemiAxis * _np.cos(t1)

                x12 = pxSemiAxis * _np.sin(t1) * _np.cos(p2)
                y12 = pySemiAxis * _np.sin(t1) * _np.sin(p2)
                z12 = pzSemiAxis * _np.cos(t1)

                x21 = pxSemiAxis * _np.sin(t2) * _np.cos(p1)
                y21 = pySemiAxis * _np.sin(t2) * _np.sin(p1)
                z21 = pzSemiAxis * _np.cos(t2)

                x22 = pxSemiAxis * _np.sin(t2) * _np.cos(p2)
                y22 = pySemiAxis * _np.sin(t2) * _np.sin(p2)
                z22 = pzSemiAxis * _np.cos(t2)

                # Curved edges
                if thetaTop == 0 and j == 0 :
                    vCurv = []
                    vCurv.append(_Vertex([x11, y11, z11]))
                    vCurv.append(_Vertex([x22, y22, z22]))
                    vCurv.append(_Vertex([x21, y21, z21]))
                    vCurv.reverse()
                    polygons.append(_Polygon(vCurv))
                elif thetaBot == _np.pi and j == stacks-1:
                    vCurv = []
                    vCurv.append(_Vertex([x11, y11, z11]))
                    vCurv.append(_Vertex([x12, y12, z12]))
                    vCurv.append(_Vertex([x21, y21, z21]))
                    vCurv.reverse()
                    polygons.append(_Polygon(vCurv))
                else :
                    vCurv = []
                    vCurv.append(_Vertex([x11, y11, z11]))
                    vCurv.append(_Vertex([x12, y12, z12]))
                    vCurv.append(_Vertex([x22, y22, z22]))
                    vCurv.append(_Vertex([x21, y21, z21]))
                    vCurv.reverse()
                    polygons.append(_Polygon(vCurv))

                # end plates if there are cuts
                if thetaTop > 0 and j == 0:
                    vEnd = []
                    vEnd.append(_Vertex([0, 0, pzTopCut]))
                    vEnd.append(_Vertex([x11, y11, pzTopCut]))
                    vEnd.append(_Vertex([x12, y12, pzTopCut]))
                    polygons.append(_Polygon(vEnd))

                elif thetaBot < _np.pi and j == stacks-1:
                    vEnd = []
                    vEnd.append(_Vertex([0, 0, pzBottomCut]))
                    vEnd.append(_Vertex([x22, y22, pzBottomCut]))
                    vEnd.append(_Vertex([x21, y21, pzBottomCut]))
                    polygons.append(_Polygon(vEnd))

        return _CSG.fromPolygons(polygons)

