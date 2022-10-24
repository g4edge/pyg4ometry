from .SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector

import math as _math

class Plane(_SolidBase): # point on plane is on z-axis
    """
    Constructs a *infinite* plane. Should not be used to construct geant4 geometry.

    :param name: of object in registry
    :type name: str
    :param normal: normal [x,y,z]
    :type normal: tuple
    :param dist: distance from origin to plane
    :type dist: float
    :param zlength: large transverse box size to emulate infinite plane
    :type zlength: float
    """
    def __init__(self, name, normal, dist, zlength=10000):
        super(Plane, self).__init__(name, 'Plane', None)

        self.normal = _Vector(normal).unit()
        self.dist   = float(dist)
        self.pDz    = float(zlength)
        self.mesh   = None

    def __repr__(self):
        return "Pane : {} [{},{},{}] {}".format(self.name, 
                                                str(self.normal[0]), 
                                                str(self.normal[1]), 
                                                str(self.normal[2]),
                                                str(self.dist), 
                                                str(self.pDz))

    def pycsgmesh(self):

        d = self.pDz
        c = _CSG.cube(radius=[10*d,10*d,d])

        dp = self.normal.dot(_Vector(0,0,1))

        if dp != 1 and dp != -1:
            cp = self.normal.cross(_Vector(0,0,1))
            an = _math.acos(dp)
            an = an/_math.pi*180.
            c.rotate(cp,an)

        c.translate(_Vector([0, 0, self.dist+d/dp]))

        mesh = c
        return  mesh
