from .SolidBase import SolidBase as _SolidBase
from ... import exceptions
from ...transformation import *

import copy as _copy
import logging as _log

_log = _log.getLogger(__name__)


class MultiUnion(_SolidBase):
    """
    Union between two or more solids.

    :param name: of solid
    :type name: str
    :param objects: unrotated, untranslated solid objects to form union
    :param transformations: [[rot1,tra1],[rot2,tra2], [rot3,tra3] .. ] or [[[a,b,g],[dx,dy,dz]],  [[a,b,g],[dx,dy,dz]], [[a,b,g],[dx,dy,dz]], ...]
    :param registry: for storing solid
    :type registry: Registry
    :param addRegistry: Add solid to registry
    :type addRegitry: bool
    """

    def __init__(self, name, objects, transformations, registry, addRegistry=True):
        super().__init__(name, "MultiUnion", registry)
        # circular import
        from ...gdml import Defines as _defines
        from ... import geant4 as _g4

        self.objects = objects
        self.transformations = [
            _defines.upgradeToTransformation(t, registry) for t in transformations
        ]

        self.varNames = ["transformations"]
        self.varUnits = [None]
        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

        for obj in objects:
            obj.dependents.append(self)

    def __repr__(self):
        return f"Multi Union {self.name}"

    def __str__(self):
        # TODO put all information
        return f"Multi Union {self.name}"

    def mesh(self):
        _log.debug("MultiUnion.pycsgmesh>")

        result = None
        for solid, tra2 in zip(self.objects, self.transformations):
            try:
                mesh = solid.mesh()
            except exceptions.NullMeshError:
                continue
            rot = tbxyz2axisangle(tra2[0].eval())
            tlate = tra2[1].eval()
            mesh.rotate(rot[0], -rad2deg(rot[1]))
            mesh.translate(tlate)
            result = mesh if result is None else result.union(mesh)

        if result is None or result.isNull():
            raise exceptions.NullMeshError(self)
        return result
