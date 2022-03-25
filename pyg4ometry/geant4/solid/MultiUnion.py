from   .SolidBase import SolidBase as _SolidBase
import pyg4ometry.exceptions
from   pyg4ometry.transformation import *

import copy as _copy
import logging as _log

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
        super(MultiUnion, self).__init__(name, 'MultiUnion', registry)
        # circular import
        import pyg4ometry.gdml.Defines as _defines
        import pyg4ometry.geant4       as _g4

        self.objects         = objects
        self.transformations = [_defines.upgradeToTransformation(t,registry)
                                for t in transformations]

        self.varNames = ["transformations"]
        self.varUnits = [None]
        self.dependents = []

        if addRegistry:
            registry.addSolid(self)

        for obj in objects :
            obj.dependents.append(self)

    def __repr__(self):
        return 'Multi Union %s' % (self.name)

    def mesh(self):

        _log.info('MultiUnion.pycsgmesh>')

        result = self.objects[0].mesh()
        tra2 = self.transformations[0]
        rot = tbxyz2axisangle(tra2[0].eval())
        tlate = tra2[1].eval()
        result.rotate(rot[0], -rad2deg(rot[1]))
        result.translate(tlate)

        for idx, (solid, tra2) in enumerate(zip(self.objects[1:],
                                                self.transformations[1:]),
                                            start=1):

            # tranformation
            rot = tbxyz2axisangle(tra2[0].eval())
            tlate = tra2[1].eval()
            _log.info('MulUnion.mesh> rot=%s tlate=%s' % (str(rot),str(tlate)))

            # get meshes
            _log.info('union.mesh> mesh %s' % str(idx))
            mesh = solid.mesh()

            # apply transform to second mesh
            mesh.rotate(rot[0],-rad2deg(rot[1]))
            mesh.translate(tlate)

            _log.info('MultiUnion.mesh> union')
            result = result.union(mesh)

        return result
