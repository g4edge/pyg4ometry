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

class Trd(_SolidBase):
    """
    Constructs a trapezoid.

    :param name:  of the solid
    :type name:   str
    :param pDx1:  length along x at the surface positioned at -dz/2
    :type pDx1:   float, Constant, Quantity, Variable
    :param pDx2:  length along x at the surface postitioned at +dz/2
    :type pDx2:   float, Constant, Quantity, Variable
    :param pDy1:  length along y at the surface positioned at -dz/2
    :type pDy1:   float, Constant, Quantity, Variable
    :param pDy2:  length along y at the surface positioned at +dz/2
    :type pDy2:   float, Constant, Quantity, Variable
    :param dz:    length along the z axis
    :type dz:     float, Constant, Quantity, Variable
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    """
    def __init__(self, name, pDx1, pDx2, pDy1, pDy2, pDz, registry, lunit="mm", addRegistry=True):
        super(Trd, self).__init__(name, 'Trd', registry)

        self.pX1    = pDx1
        self.pX2    = pDx2
        self.pY1    = pDy1
        self.pY2    = pDy2
        self.pZ     = pDz
        self.lunit  = lunit

        self.dependents = []

        self.varNames = ["pX1", "pX2", "pY1", "pY2", "pZ"]
        self.varUnits = ["lunit", "lunit", "lunit", "lunit", "lunit"]

        if addRegistry:
            registry.addSolid(self)

    def mesh(self):
        _log.info('trd.pycsgmesh> antlr')
        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pX1 = self.evaluateParameter(self.pX1)*luval/2.
        pX2 = self.evaluateParameter(self.pX2)*luval/2.
        pY1 = self.evaluateParameter(self.pY1)*luval/2.
        pY2 = self.evaluateParameter(self.pY2)*luval/2.
        pZ  = self.evaluateParameter(self.pZ)*luval/2.

        _log.info('trd.pycsgmesh> mesh')
        mesh  = _CSG.fromPolygons([_Polygon([_Vertex(_Vector(-pX2,  pY2, pZ)),
                                             _Vertex(_Vector(-pX2, -pY2, pZ)),
                                             _Vertex(_Vector(pX2,  -pY2, pZ)),
                                             _Vertex(_Vector(pX2,  pY2,  pZ))]),
                                   
                                   _Polygon([ _Vertex(_Vector(-pX1, -pY1, -pZ)),
                                              _Vertex(_Vector(-pX1,  pY1, -pZ)),
                                              _Vertex(_Vector(pX1,   pY1, -pZ)),
                                              _Vertex(_Vector(pX1,  -pY1, -pZ))]),
                                   
                                   _Polygon([_Vertex(_Vector(pX2,  -pY2,  pZ)),
                                             _Vertex(_Vector(-pX2, -pY2,  pZ)),
                                             _Vertex(_Vector(-pX1, -pY1, -pZ)),
                                             _Vertex(_Vector(pX1,  -pY1, -pZ))]),
                                   
                                   _Polygon([_Vertex(_Vector(pX2,  pY2,  pZ)),
                                             _Vertex(_Vector(pX1,  pY1, -pZ)),
                                             _Vertex(_Vector(-pX1, pY1, -pZ)),
                                             _Vertex(_Vector(-pX2, pY2,  pZ))]),
                                   
                                   _Polygon([_Vertex(_Vector(-pX2,  pY2,  pZ)),
                                             _Vertex(_Vector(-pX1,  pY1, -pZ)),
                                             _Vertex(_Vector(-pX1, -pY1, -pZ)),
                                             _Vertex(_Vector(-pX2, -pY2,  pZ))]),
                                   
                                   _Polygon([_Vertex(_Vector(pX2, -pY2,  pZ)),
                                             _Vertex(_Vector(pX1, -pY1, -pZ)),
                                             _Vertex(_Vector(pX1,  pY1, -pZ)),
                                             _Vertex(_Vector(pX2,  pY2,  pZ))])])
        
        return mesh

