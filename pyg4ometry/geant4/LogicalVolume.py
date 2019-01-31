import pyg4ometry.exceptions
from   pyg4ometry.pycsg.geom import Vector as _Vector
from   pyg4ometry.pycsg.core import CSG as _CSG

from   pyg4ometry.visualisation import Mesh as _Mesh
import solid as _solid
from   Material              import Material as _Material

import numpy as _np
import sys as _sys

class LogicalVolume(object):
    def __init__(self, solid, material, name, debug=False, registry=None, **kwargs):
        super(LogicalVolume, self).__init__()
        self.solid           = solid

        if isinstance(material, _Material):
            self.material = material
        elif isinstance(material, str):
            self.material = _Material.nist(material)
        else:
            raise SystemExit("Unsupported type for material: {}".format(type(material)))

        self.name            = name
        self.daughterVolumes = []
        self.debug           = debug

        self.mesh          = _Mesh(self.solid)

        if registry:
            registry.addLogicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Logical volume : '+self.name+' '+str(self.solid)+' '+str(self.material)

    def add(self, physicalVolume):
        self.daughterVolumes.append(physicalVolume)

    def extent(self) : 
        print 'LogicalVolume.extent> ', self.name

        for dv in self.daughterVolumes : 
            dv.extent()

