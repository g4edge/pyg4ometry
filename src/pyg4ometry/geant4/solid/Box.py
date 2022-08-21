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


def cubeNet(vecList):

    return _CSG.fromPolygons([_Polygon([_Vertex(vecList[0]), _Vertex(vecList[1]), _Vertex(vecList[2]), _Vertex(vecList[3])]),
                              _Polygon([_Vertex(vecList[4]), _Vertex(vecList[7]), _Vertex(vecList[6]), _Vertex(vecList[5])]),
                              _Polygon([_Vertex(vecList[0]), _Vertex(vecList[4]), _Vertex(vecList[5]), _Vertex(vecList[1])]),
                              _Polygon([_Vertex(vecList[2]), _Vertex(vecList[6]), _Vertex(vecList[7]), _Vertex(vecList[3])]),
                              _Polygon([_Vertex(vecList[0]), _Vertex(vecList[3]), _Vertex(vecList[7]), _Vertex(vecList[4])]),
                              _Polygon([_Vertex(vecList[1]), _Vertex(vecList[5]), _Vertex(vecList[6]), _Vertex(vecList[2])])])


class Box(_SolidBase):
    """
    Constructs a box. Note the lengths are full lengths and not half lengths as in Geant4

    :param name: of solid for registry
    :type name: str
    :param pX: length along x
    :type pX: float, Constant, Quantity, Variable, Expression
    :param pY: length along y
    :type pY: float, Constant, Quantity, Variable, Expression
    :param pZ: length along z
    :type pZ: float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    """

    def __init__(self, name, pX, pY, pZ, registry, lunit="mm", addRegistry=True):
        super(Box, self).__init__(name, 'Box', registry)

        self.lunit = lunit

        self.dependents = []

        self.varNames = ["pX", "pY", "pZ"]
        self.varUnits = ["lunit", "lunit", "lunit"]

        for varName in self.varNames:
            self._addProperty(varName)
            setattr(self, varName, locals()[varName])

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Box : {} {} {} {}".format(self.name, self.pX, self.pY, self.pZ)

    def mesh(self):
        _log.info('box.pycsgmesh> antlr')
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        uval = _Units.unit(self.lunit)

        pX = self.evaluateParameter(self.pX)*uval/2.0
        pY = self.evaluateParameter(self.pY)*uval/2.0
        pZ = self.evaluateParameter(self.pZ)*uval/2.0

        c = _Vector(0, 0, 0)
        r = [pX, pY, pZ]

        polygons = list([_Polygon(
            list([_Vertex(
                _Vector(
                    c.x + r[0] * (2 * bool(i & 1) - 1),
                    c.y + r[1] * (2 * bool(i & 2) - 1),
                    c.z + r[2] * (2 * bool(i & 4) - 1)
                )
            ) for i in v[0]])) for v in [
                [[0, 4, 6, 2], [-1, 0, 0]],
                [[1, 3, 7, 5], [+1, 0, 0]],
                [[0, 1, 5, 4], [0, -1, 0]],
                [[2, 6, 7, 3], [0, +1, 0]],
                [[0, 2, 3, 1], [0, 0, -1]],
                [[4, 5, 7, 6], [0, 0, +1]]
            ]])
        return _CSG.fromPolygons(polygons)
