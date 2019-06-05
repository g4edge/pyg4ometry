from   SolidBase import SolidBase as _SolidBase
from   pyg4ometry.geant4.Registry import registry as _registry
import pyg4ometry.exceptions
from   pyg4ometry.transformation import *

import copy as _copy
import logging as _log

class MultiUnion(_SolidBase):
    """
    Union between two solids     

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
        # circular import 
        import pyg4ometry.gdml.Defines as _defines
        import pyg4ometry.geant4       as _g4

        self.type            = "MultiUnion"
        self.name            = name
        self.objects         = objects
        self.transformations = [_defines.upgradeToTransformation(t,registry) for t in transformations]
        self.mesh = None

        self.dependents = []

        registry.addSolid(self)
        self.registry = registry

        for obj in objects : 
            obj.dependents.append(self) 

    def __repr__(self):
        return 'Multi Union %s' % (self.name)

    def pycsgmesh(self):

        _log.info('MultiUnion.pycshmesh>')

        
        # untransformed first solid
        m1 = self.objects[0].pycsgmesh()

        for obj,tra2,idx in zip(self.objects[1:],self.transformations[1:],range(1,len(self.objects))) : 
            
            # tranformation
            rot = tbxyz2axisangle(tra2[0].eval())
            tlate = tra2[1].eval()
            _log.info('MulUnion.pycsgmesh> rot=%s tlate=%s' % (str(rot),str(tlate)))
            
            # get meshes 
            _log.info('union.pycshmesh> mesh %s' % str(idx))
            m2 = obj.pycsgmesh()

            # apply transform to second mesh 
            m2.rotate(rot[0],-rad2deg(rot[1]))
            m2.translate(tlate)

            _log.info('MultiUnion.pycsgmesh> union')
            m1 = m1.union(m2)

        return m1
