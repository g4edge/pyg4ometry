from .SolidBase import SolidBase as _SolidBase
from ... import exceptions
from ...transformation import *

import logging as _log

_log = _log.getLogger(__name__)


class Union(_SolidBase):
    """
    Union between two solids

    :param name: of solid
    :type name: str
    :param obj1: unrotated, untranslated solid
    :type obj1: pyg4ometry.geant4.solid
    :param obj2: solid rotated and translated according to tra2
    :type obj2: pyg4ometry.geant4.solid
    :param tra2: [rot,tra] = [[a,b,g],[dx,dy,dz]]
    :type tra2: list
    :param registry: for storing solid
    :type registry: Registry
    """

    def __init__(self, name, obj1, obj2, tra2, registry, addRegistry=True):
        super().__init__(name, "Union", registry)
        # circular import
        from ...gdml import Defines as _defines
        from ... import geant4 as _g4

        self.obj1 = obj1
        self.obj2 = obj2
        self.tra2 = _defines.upgradeToTransformation(tra2, registry)

        self.varNames = ["tra2"]
        self.varUnits = [None]
        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

        # obj1 = self.registry.solidDict[_g4.solidName(self.obj1)]
        # obj2 = self.registry.solidDict[_g4.solidName(self.obj2)]
        obj1.dependents.append(self)
        obj2.dependents.append(self)

    def __repr__(self):
        return f"Union {self.name}({self.obj1.name} {self.obj2.name})"

    def __str__(self):
        return f"Union {self.name} {self.obj1.name} {self.obj2.name}"

    def mesh(self):
        _log.debug("union.pycsgmesh>")

        from ... import geant4 as _g4

        obj1 = self.registry.solidDict.get(_g4.solidName(self.obj1), self.obj1)
        obj2 = self.registry.solidDict.get(_g4.solidName(self.obj2), self.obj2)

        rot = tbxyz2axisangle(self.tra2[0].eval())
        tlate = self.tra2[1].eval()

        try:
            m1 = obj1.mesh()
        except exceptions.NullMeshError:
            m1 = None
        try:
            m2 = obj2.mesh().clone()
        except exceptions.NullMeshError:
            m2 = None
        if m1 is None and m2 is None:
            raise exceptions.NullMeshError(self)
        if m2 is not None:
            m2.rotate(rot[0], -rad2deg(rot[1]))
            m2.translate(tlate)
        if m1 is None:
            return m2
        if m2 is None:
            return m1
        return m1.union(m2)

    def translation(self):
        return self.tra2[1].eval()

    def rotation(self):
        return self.tra2[0].eval()

    def object1(self):
        from ... import geant4 as _g4

        return self.registry.solidDict.get(_g4.solidName(self.obj1), self.obj1)

    def object2(self):
        from ... import geant4 as _g4

        return self.registry.solidDict.get(_g4.solidName(self.obj2), self.obj2)
