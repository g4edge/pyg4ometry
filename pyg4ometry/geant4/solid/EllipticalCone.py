from .SolidBase import SolidBase as _SolidBase
from .Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon
import logging as _log

import numpy as _np

class EllipticalCone(_SolidBase):
    def __init__(self, name, pxSemiAxis, pySemiAxis, zMax, pzTopCut,
                 registry, lunit="mm",nslice=16, nstack=16, addRegistry=True):
        """
        Constructs a cone with elliptical cross-section and an
        optional cut.  Both zMax and pzTopCut are half lengths
        extending from the centre of the cone, at z=0.

        Inputs:
          name:       string, name of the volume
          pxSemiAxis: float, semiaxis in x at z=0 as a fraction of zMax.
          pySemiAxis: float, semiaxis in y at z=0 as a fraction of zMax
          zMax:       float, half length of the cone.
          pzTopCut:   float, half length of the cut.

        """

        self.type       = 'EllipticalCone'
        self.name       = name
        self.pxSemiAxis = pxSemiAxis
        self.pySemiAxis = pySemiAxis
        self.zMax       = zMax
        self.pzTopCut   = pzTopCut
        self.lunit      = lunit
        self.nslice     = nslice
        self.nstack     = nslice

        self.dependents = []

        self.varNames = ["pxSemiAxis", "pySemiAxis", "zMax","pzTopCut"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "EllipticalCone : {} {} {} {} {}".format(self.name, self.pxSemiAxis,
                                                        self.pySemiAxis, self.zMax,
                                                        self.pzTopCut)

    def pycsgmesh(self):
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
        centreBig = _Vertex([0, 0, -pzTopCut], None)
        centreSmall = _Vertex([0, 0, +pzTopCut], None)

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

            vertices.append(_Vertex([x4,y4,z4], None))
            vertices.append(_Vertex([x3,y3,z3], None))
            vertices.append(_Vertex([x2,y2,z2], None))
            vertices.append(_Vertex([x1,y1,z1], None))

            polygons.append(_Polygon(vertices))

            # Bigger face (-pzTopCut)
            verticesb = []
            from copy import deepcopy
            verticesb.append(_Vertex([x2, y2, z2], None))
            verticesb.append(_Vertex([x3, y3, z3], None))
            verticesb.append(deepcopy(centreBig))
            polygons.append(_Polygon(verticesb))

            # Smaller face (+pzTopCut)
            verticest = []
            verticest.append(_Vertex([x1, y1, z1], None))
            verticest.append(deepcopy(centreSmall))
            verticest.append(_Vertex([x4, y4, z4], None))
            polygons.append(_Polygon(verticest))

        mesh = _CSG.fromPolygons(polygons)

        return mesh
