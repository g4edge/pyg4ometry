from SolidBase import SolidBase as _SolidBase
from pyg4ometry.geant4.Registry import registry as _registry
import pyg4ometry.exceptions
from pyg4ometry.transformation import *

import logging as _log
import copy as _copy

class Subtraction(_SolidBase):
    """
    output = obj1 - obj2
    name = name
    obj1 = unrotated, untranslated solid
    obj2 = solid rotated and translated according to tra2
    tra2 = [rot,tra] = [[a,b,g],[dx,dy,dz]]
    """
    def __init__(self,name, obj1, obj2, tra2, registry):
        # circular import 
        import pyg4ometry.gdml.Defines as _defines
        import pyg4ometry.geant4 as _g4

        self.type = "Subtraction"
        self.name = name
        self.obj1 = obj1
        self.obj2 = obj2
        self.tra2 = _defines.upgradeToTransformation(tra2,registry)
        self.mesh = None

        registry.addSolid(self)
        self.registry = registry 

        self.dependents = []
        obj1 = self.registry.solidDict[_g4.solidName(self.obj1)]
        obj2 = self.registry.solidDict[_g4.solidName(self.obj2)]
        obj1.dependents.append(self) 
        obj2.dependents.append(self)

    def __repr__(self):
        return 'Subtraction : ('+self.obj1.name+') - ('+str(self.obj2.name)+')'

    def pycsgmesh(self):

        _log.info('subtraction.pycshmesh>')

        # look up solids in registry 
        import pyg4ometry.geant4 as _g4
        obj1 = self.registry.solidDict[_g4.solidName(self.obj1)]
        obj2 = self.registry.solidDict[_g4.solidName(self.obj2)]

        # transformation 
        rot = tbxyz2axisangle(self.tra2[0].eval())
        tlate = self.tra2[1].eval()

        # get meshes 
        _log.info('subtraction.pycsgmesh> mesh1')
        m1 = obj1.pycsgmesh()
        _log.info('subtraction.pycsgmesh> mesh2')
        m2 = obj2.pycsgmesh().clone()

        m2.rotate(rot[0],-rad2deg(rot[1]))
        m2.translate(tlate)

        self.obj2mesh = m2

        _log.info('subtraction.pycshmsh> subtraction')
        mesh = m1.subtract(m2)
        if not mesh.toPolygons():
            raise pyg4ometry.exceptions.NullMeshError(self)

        return mesh
