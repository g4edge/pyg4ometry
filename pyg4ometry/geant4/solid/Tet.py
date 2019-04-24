from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from Plane import Plane as _Plane
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np
import logging as _log
from copy import deepcopy as _dc

class Tet(_SolidBase):
    def __init__(self, name, anchor, p2, p3, p4, registry,
                 degeneracyFlag=False):
        """
        Constructs a tetrahedra.

        Inputs:
          name:           string, name of the volume
          anchor:         list, anchor point
          p2:             list, point 2
          p3:             list, point 3
          p4:             list, point 4
          degeneracyFlag: bool, indicates degeneracy of points
        """
        self.type    = 'Tet'
        self.name    = name
        self.anchor  = anchor
        self.p2      = p2
        self.p3      = p3
        self.p4      = p4
        self.degen   = degeneracyFlag
        self.dependents = []

        registry.addSolid(self) # Always need the registry
        self.registry = registry


    def __repr__(self):
        return "Tet : {} Vertexes: {}, {}, {}, {}".format(self.name, self.anchor.expr.expression, self.p2.expr.expression,
                                                          self.p3.expr.expression, self.p4.expr.expression)

    def pycsgmesh(self):
        _log.info('tet.pycsgmesh> antlr')

        anchor_pos = self.registry.defineDict[self.anchor.expr.expression]
        p2_pos = self.registry.defineDict[self.p2.expr.expression]
        p3_pos = self.registry.defineDict[self.p3.expr.expression]
        p4_pos = self.registry.defineDict[self.p4.expr.expression]

        anchor = [anchor_pos.x.eval(), anchor_pos.y.eval(), anchor_pos.z.eval()]
        p2 = [p2_pos.x.eval(), p2_pos.y.eval(), p2_pos.z.eval()]
        p3 = [p3_pos.x.eval(), p3_pos.y.eval(), p3_pos.z.eval()]
        p4 = [p4_pos.x.eval(), p4_pos.y.eval(), p4_pos.z.eval()]

        _log.info('tet.pycsgmesh> mesh')
        vert_ancr = _Vertex(_Vector(p4[0], p4[1], p4[2]), None)
        base      = [anchor, p2, p3]
        vert_base = []

        for i in range(len(base)):
            vert_base.append(_Vertex(_Vector(base[i][0],base[i][1],base[i][2]), None))

        mesh = _CSG.fromPolygons([_Polygon([_dc(vert_base[2]), _dc(vert_base[1]), _dc(vert_base[0])], None),
                                       _Polygon([_dc(vert_base[1]), _dc(vert_ancr), _dc(vert_base[0])], None),
                                       _Polygon([_dc(vert_base[2]), _dc(vert_ancr), _dc(vert_base[1])], None),
                                       _Polygon([_dc(vert_base[0]), _dc(vert_ancr), _dc(vert_base[2])], None)])

        return mesh
