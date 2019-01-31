from SolidBase import SolidBase as _SolidBase
from ..Registry import registry as _registry
from ...transformation import *


import copy as _copy
import pyg4ometry.exceptions

class Intersection(_SolidBase):
    """
    name = name
    obj1 = unrotated, untranslated solid
    obj2 = solid rotated and translated according to tra2
    tra2 = [rot,tra] = [[a,b,g],[dx,dy,dz]]
    """
    def __init__(self, name, obj1name, obj2name, tra2, registry=None):
        self.type = "Intersection"
        self.name = name
        self.obj1name = obj1name
        self.obj2name = obj2name
        self.tra2 = tra2
        self.mesh = None
        if registry:
            registry.addSolid(self)
            self.registry = registry

    def __repr__(self):
        return 'Intersection '+self.name+': ('+str(self.obj1)+') with ('+str(self.obj2)+')'

    def pycsgmesh(self):

        print 'intersection.pycshmesh>' 

        # look up solids in registry 
        obj1 = self.registry.solidDict[self.obj1name]
        obj2 = self.registry.solidDict[self.obj2name]

        # transformation 
        rot   = tbxyz(self.tra2[0].eval())
        tlate = self.tra2[1].eval()

        # get meshes 
        print 'intersection.pycshmesh> mesh1' 
        m1 = obj1.pycsgmesh()
        print 'intersection.pycshmesh> mesh2' 
        m2 = obj2.pycsgmesh()
        
        # apply transform to second mesh
        m2.rotate(rot[0],-rad2deg(rot[1]))
        m2.translate(tlate)

        print 'intersection.pycshmesh> intersect' 
        mesh = m1.intersect(m2)
        if not mesh.toPolygons():
            raise pyg4ometry.exceptions.NullMeshError(self)

        #print 'intersection mesh ', self.name
        return mesh
