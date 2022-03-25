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

class EllipticalCone(_SolidBase):
    """
    Constructs a cone with elliptical cross-section and an
    optional cut.  Both zMax and pzTopCut are half lengths
    extending from the centre of the cone, at z=0.
    
    :param name:       name of the volume
    :type name:         str
    :param pxSemiAxis: semiaxis in x at z=0 as a fraction of zMax.
    :type pxSemiAxis:  float, Constant, Quantity, Variable, Expression
    :param pySemiAxis: semiaxis in y at z=0 as a fraction of zMax
    :type pySemiAxis:  float, Constant, Quantity, Variable, Expression
    :param zMax:       half length of the cone.
    :type zMax:        float, Constant, Quantity, Variable, Expression
    :param pzTopCut:   half length of the cut.
    :type pzTopCut:    float, Constant, Quantity, Variable, Expression

    """
    def __init__(self, name, pxSemiAxis, pySemiAxis, zMax, pzTopCut,
                 registry, lunit="mm", nslice=None, nstack=None, addRegistry=True):
        super(EllipticalCone, self).__init__(name, 'EllipticalCone', registry)

        self.pxSemiAxis = pxSemiAxis
        self.pySemiAxis = pySemiAxis
        self.zMax       = zMax
        self.pzTopCut   = pzTopCut
        self.lunit      = lunit
        self.nslice     = nslice if nslice else _config.SolidDefaults.EllipticalCone.nslice
        self.nstack     = nstack if nstack else _config.SolidDefaults.EllipticalCone.nstack

        self.dependents = []

        self.varNames = ["pxSemiAxis", "pySemiAxis", "zMax", "pzTopCut"]
        self.varUnits = ["lunit", "lunit", "lunit", "lunit"]

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "EllipticalCone : {} {} {} {} {}".format(self.name, self.pxSemiAxis,
                                                        self.pySemiAxis, self.zMax,
                                                        self.pzTopCut)

    def mesh(self):
        _log.info("ellipticalcone.antlr>")

        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        luval = _Units.unit(self.lunit)

        pxSemiAxis = self.evaluateParameter(self.pxSemiAxis) * luval
        pySemiAxis = self.evaluateParameter(self.pySemiAxis) * luval
        zMax = self.evaluateParameter(self.zMax) * luval
        pzTopCut = self.evaluateParameter(self.pzTopCut) * luval
        pzTopCut = min(zMax, pzTopCut) # Accounting for if cut > zmax.

        _log.info("ellipticalcone.pycsgmesh>")
        polygons = []

        # smaller face semi-axis (at z=ztopcut)
        dx0 = pxSemiAxis * (zMax - pzTopCut)
        dy0 = pySemiAxis * (zMax - pzTopCut)
        # Larger face semi-axis (at z=-ztopcut)
        dx1 = pxSemiAxis * (zMax + pzTopCut)
        dy1 = pySemiAxis * (zMax + pzTopCut)

        # Vertices of the larger and smaller faces.
        centreBig = _Vertex([0, 0, -pzTopCut])
        centreSmall = _Vertex([0, 0, +pzTopCut])

        dTheta = 2 * _np.pi / self.nslice
        for i1 in range(0, self.nslice):
            i2 = i1 + 1
            # Rectangular strips from one face to the other.
            z1 = pzTopCut
            x1 = dx0 * _np.cos(dTheta*i1)
            y1 = dy0 * _np.sin(dTheta*i1)

            z2 = -pzTopCut
            x2 = dx1 * _np.cos(dTheta*i1)
            y2 = dy1 * _np.sin(dTheta*i1)

            z3 = -pzTopCut
            x3 = dx1 * _np.cos(dTheta*i2)
            y3 = dy1 * _np.sin(dTheta*i2)

            z4 = pzTopCut
            x4 = dx0 * _np.cos(dTheta*i2)
            y4 = dy0 * _np.sin(dTheta*i2)

            vertices = []

            vertices.append(_Vertex([x4,y4,z4]))
            vertices.append(_Vertex([x3,y3,z3]))
            vertices.append(_Vertex([x2,y2,z2]))
            vertices.append(_Vertex([x1,y1,z1]))

            polygons.append(_Polygon(vertices))

            # Bigger face (-pzTopCut)
            verticesb = []
            verticesb.append(_Vertex([x2, y2, z2]))
            verticesb.append(_Vertex([x3, y3, z3]))
            verticesb.append(centreBig)
            polygons.append(_Polygon(verticesb))

            # Smaller face (+pzTopCut)
            verticest = []
            verticest.append(_Vertex([x1, y1, z1]))
            verticest.append(centreSmall)
            verticest.append(_Vertex([x4, y4, z4]))
            polygons.append(_Polygon(verticest))

        mesh = _CSG.fromPolygons(polygons)

        return mesh
