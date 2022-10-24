from .SolidBase import SolidBase as _SolidBase
import pyg4ometry.exceptions
from ...transformation import *

import copy as _copy
import logging as _log

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
        super(Union, self).__init__(name, 'Union', registry)
        # circular import 
        import pyg4ometry.gdml.Defines as _defines
        import pyg4ometry.geant4 as _g4

        self.obj1 = obj1
        self.obj2 = obj2
        self.tra2 = _defines.upgradeToTransformation(tra2,registry)

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
        return 'Union %s(%s %s)' % (self.name, self.obj1.name, self.obj2.name)

    def mesh(self):
        _log.info('union.pycsgmesh>')

        # look up solids in registry 
        import pyg4ometry.geant4 as _g4
        obj1 = self.registry.solidDict.get(_g4.solidName(self.obj1), self.obj1)
        obj2 = self.registry.solidDict.get(_g4.solidName(self.obj2), self.obj2)

        # transformation
        rot = tbxyz2axisangle(self.tra2[0].eval())
        tlate = self.tra2[1].eval()
        _log.info('Union.pycsgmesh> rot=%s tlate=%s' % (str(rot),str(tlate)))

        # get meshes 
        _log.info('union.mesh> mesh1')
        m1 = obj1.mesh()
        _log.info('union.mesh> mesh2')
        m2 = obj2.mesh().clone()

        # apply transform to second mesh 
        m2.rotate(rot[0],-rad2deg(rot[1]))
        m2.translate(tlate)

        _log.info('union.pycsgmesh> union')
        mesh = m1.union(m2)

        return mesh

    def translation(self):
        return self.tra2[1].eval()

    def rotation(self):
        return self.tra2[0].eval()

    def object1(self):
        import pyg4ometry.geant4 as _g4
        return self.registry.solidDict.get(_g4.solidName(self.obj1), self.obj1)

    def object2(self):
        import pyg4ometry.geant4 as _g4
        return self.registry.solidDict.get(_g4.solidName(self.obj2), self.obj2)
