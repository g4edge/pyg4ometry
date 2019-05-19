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
    """
    Constructs a tetrahedra.
    
    :param name:           of the solid
    :param anchor:         point 1 (anchor point)
    :type anchor:          list
    :param p2:             point 2
    :type p2:              list
    :param p3:             point 3
    :type p3:              list
    :param p4:             point 4
    :type p4:              list
    :param registry:       for storing solid
    :type registry:        Registry
    :param lunit:          length unit (nm,um,mm,m,km) for solid
    :type lunit:           str
    
    :param degeneracyFlag: bool, indicates degeneracy of points
    """


    def __init__(self, name, anchor, p2, p3, p4, registry,
                 lunit = "mm",
                 degeneracyFlag=False):
        self.type    = 'Tet'
        self.name    = name
        self.anchor  = anchor
        self.p2      = p2
        self.p3      = p3
        self.p4      = p4
        self.lunit   = lunit
        self.degen   = degeneracyFlag
        self.dependents = []

        registry.addSolid(self) # Always need the registry

        self.registry = registry


    def __repr__(self):
        return "Tet : {} Vertexes: {}, {}, {}, {}".format(self.name, self.anchor.expr.expression, self.p2.expr.expression,
                                                          self.p3.expr.expression, self.p4.expr.expression)

    def pycsgmesh(self):
        _log.info('tet.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)

        anchor = _np.array([self.anchor.x.eval(), self.anchor.y.eval(), self.anchor.z.eval()])*luval
        p2     = _np.array([self.p2.x.eval(), self.p2.y.eval(), self.p2.z.eval()])*luval
        p3     = _np.array([self.p3.x.eval(), self.p3.y.eval(), self.p3.z.eval()])*luval
        p4     = _np.array([self.p4.x.eval(), self.p4.y.eval(), self.p4.z.eval()])*luval

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
