from .SolidBase import SolidBase as _SolidBase
from .Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Plane as _Plane
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np

class Layer(object):
    def __init__(self, p1, p2, p3, p4, z):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.z  = z

    def __getitem__(self, index):
        if index == 0:
            return self.p1
        elif index == 1:
            return self.p2
        elif index == 2:
            return self.p3
        elif index == 3:
            return self.p4
        elif index ==4:
            return self.z
        else:
            raise IndexError("Invalid index "+str(index))

    def Rotated(self, angle):
        result = Layer(self.p1.Rotated(angle),
                       self.p2.Rotated(angle),
                       self.p3.Rotated(angle),
                       self.p4.Rotated(angle),
                       self.z)
        return result

    def __repr__(self):
        s = 'Layer<'
        s += str(self.p1) + ', '
        s += str(self.p2) + ', '
        s += str(self.p3) + ', '
        s += str(self.p4) + ', '
        s += ' z = ' + str(self.z) + '>'
        return s
