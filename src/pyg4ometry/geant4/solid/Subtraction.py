from ... import config as _config
from .SolidBase import SolidBase as _SolidBase
from ... import exceptions
from ...transformation import *

import logging as _log

_log = _log.getLogger(__name__)


class Subtraction(_SolidBase):
    """
    Subtraction between two solids

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
        super().__init__(name, "Subtraction", registry)
        # circular import
        from ...gdml import Defines as _defines

        self.obj1 = obj1
        self.obj2 = obj2
        self.tra2 = _defines.upgradeToTransformation(tra2, registry)

        self.varNames = ["tra2"]
        self.varUnits = [None]
        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

        obj1.dependents.append(self)
        obj2.dependents.append(self)

    def __repr__(self):
        return "Subtraction : (" + self.obj1.name + ") - (" + str(self.obj2.name) + ")"

    def __str__(self):
        return f"Intersection {self.name} {self.obj1.name!s} {self.obj2.name!s}"

    def mesh(self):
        _log.debug("subtraction.pycsgmesh>")

        # look up solids in registry
        from ... import geant4 as _g4

        obj1 = self.registry.solidDict.get(_g4.solidName(self.obj1), self.obj1)
        obj2 = self.registry.solidDict.get(_g4.solidName(self.obj2), self.obj2)

        # transformation
        rot = tbxyz2axisangle(self.tra2[0].eval())
        tlate = self.tra2[1].eval()

        # get meshes
        _log.debug("subtraction.mesh> mesh1")
        m1 = obj1.mesh()
        _log.debug("subtraction.mesh> mesh2")
        m2 = obj2.mesh().clone()

        m2.rotate(rot[0], -rad2deg(rot[1]))
        m2.translate(tlate)

        self.obj2mesh = m2

        _log.debug("subtraction.pycshmsh> subtraction")
        mesh = m1.subtract(m2)
        if mesh.isNull():
            _log.warning("subtraction.pycshmsh> Subtraction null mesh solid name : %s", self.name)
            if _config.meshingNullException:
                raise exceptions.NullMeshError(self)

        return mesh

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
