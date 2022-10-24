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
    def __init__(self, name, anchor, p2, p3, p4, registry, lunit = "mm",
                 degeneracyFlag=False, addRegistry=True):
        super(Tet, self).__init__(name, 'Tet', registry)

        self.anchor  = anchor
        self.p2      = p2
        self.p3      = p3
        self.p4      = p4
        self.lunit   = lunit
        self.degen   = degeneracyFlag

        self.dependents = []

        self.varNames = ["anchor", "p2", "p3", "p4"]
        self.varUnits = ["lunit", "lunit", "lunit", "lunit"]

        if addRegistry:
            registry.addSolid(self) # Always need the registry

    def __repr__(self):
        return "Tet : {} Vertexes: {}, {}, {}, {}".format(self.name, 
                                                          str(self.anchor), 
                                                          str(self.p2),
                                                          str(self.p3), 
                                                          str(self.p4))

    def mesh(self):
        _log.info('tet.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)

        anchor = [val*luval for val in self.evaluateParameter(self.anchor)]
        p2 = [val*luval for val in self.evaluateParameter(self.p2)]
        p3 = [val*luval for val in self.evaluateParameter(self.p3)]
        p4 = [val*luval for val in self.evaluateParameter(self.p4)]

        _log.info('tet.pycsgmesh> mesh')
        vert_ancr = _Vertex(_Vector(p4[0], p4[1], p4[2]))
        base      = [anchor, p2, p3]
        vert_base = []

        for i in range(len(base)):
            vert_base.append(_Vertex(_Vector(base[i][0],base[i][1],base[i][2])))

        mesh = _CSG.fromPolygons([_Polygon([vert_base[2], vert_base[1], vert_base[0]]),
                                  _Polygon([vert_base[1], vert_ancr, vert_base[0]]),
                                  _Polygon([vert_base[2], vert_ancr, vert_base[1]]),
                                  _Polygon([vert_base[0], vert_ancr, vert_base[2]])])

        return mesh
