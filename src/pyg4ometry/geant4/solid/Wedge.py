from ... import config as _config

from .SolidBase import SolidBase as _SolidBase
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Polygon as _Polygon
import numpy as _np

from copy import deepcopy as _dc

class Wedge(_SolidBase):
    """
    Constructs a *infinite* wedge. Should not be used to construct geant4 geometry.

    :param name: of object in registry
    :type name: str
    :param normal: normal [x,y,z]
    :type normal: tuple
    :param dist: distance from origin to plane
    :type dist: float
    :param zlength: large transverse box size to emulate infinite plane
    :type zlength: float
    """
    def __init__(self, name, pRMax=1000, pSPhi=0, pDPhi=1.5, halfzlength=10000, nslice=None):
        super(Wedge, self).__init__(name, 'InfiniteWedge', None)

        self.pRMax = float(pRMax)
        self.pSPhi = float(pSPhi)
        self.pDPhi = float(pDPhi)
        self.pDz   = float(halfzlength)
        self.nslice = nslice if nslice else _config.SolidDefaults.Wedge.nslice
        self.mesh = None

    def __repr__(self):
        return 'Wedge : '+self.name+' '+str(self.pRMax)+' '+str(self.pSPhi)+' '+str(self.pDPhi)+' '+str(self.pDz)

    def pycsgmesh(self):

        d = self.pDz

        phi = _np.linspace(self.pSPhi, self.pDPhi, self.nslice)
        x  = self.pRMax*_np.cos(phi)
        y  = self.pRMax*_np.sin(phi)

        polygons = []

        vZero1 = _Vertex(_Vector(0,0,-d),None)
        vZero2 = _Vertex(_Vector(0,0, d),None)

        p1     = [_Vertex(_Vector(x[i],y[i],-d),None)  for i in range(0,len(x))]
        p2     = [_Vertex(_Vector(x[i],y[i], d),None)  for i in range(0,len(x))]


        for i in range(0,len(x)):
            if i != len(x)-1:
                # top triangle
                polygons.append(_Polygon([_dc(vZero2),_dc(p2[i]),_dc(p2[i+1])]))
                # bottom triangle
                polygons.append(_Polygon([_dc(vZero1),_dc(p1[i]),_dc(p1[i+1])]))
                # end square
                polygons.append(_Polygon([_dc(p1[i]),_dc(p1[i+1]),_dc(p2[i+1]),_dc(p2[i])]))

        # first end face
        polygons.append(_Polygon([_dc(vZero1),_dc(p1[0]),_dc(p2[0]),_dc(vZero2)]))

        # last end face
        polygons.append(_Polygon([_dc(vZero1),_dc(vZero2),_dc(p2[-1]),_dc(p1[-1])]))

        mesh = _CSG.fromPolygons(polygons)

        return mesh

