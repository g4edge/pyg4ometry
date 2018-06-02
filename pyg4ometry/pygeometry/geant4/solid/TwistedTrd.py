from SolidBase import SolidBase as _SolidBase
from pygeometry.geant4.solid.TwistedSolid import TwistedSolid as _TwistedSolid
from pygeometry.pycsg.core import CSG as _CSG
from pygeometry.pycsg.geom import Vector as _Vector
from pygeometry.pycsg.geom import Vertex as _Vertex
from pygeometry.pycsg.geom import Polygon as _Polygon
from pygeometry.geant4.Registry import registry as _registry
from pygeometry.geant4.solid.TwoVector import TwoVector as _TwoVector
from pygeometry.geant4.solid.Layer import Layer as _Layer
import numpy as _np

class TwistedTrd(_SolidBase, _TwistedSolid) :
    def __init__(self, name, twistedangle, pDx1, pDx2, pDy1, pDy2, pDz, nslice=20, refine=0) :
        """
        Constructs a twisted general trapezoid. 

        Inputs:
          name:            string, name of the volume
          twistedangle:    float, twist angle, must be less than 0.5*pi
          pDx1:            float, half-length in x at surface positioned at -pDz
          pDx2:            float, half-length in x at surface positioned at +pDz
          pDy1:            float, half-length in y at surface positioned at -pDz
          pDy2:            float, half-length in y at surface positioned at +pDz
          pDz:             float, half-length in z
          refine:          int, number of steps to iteratively smoothen the mesh
                                by doubling the number of vertices at every step
        """
        self.type             = 'TwistedTrd'
        self.name             = name
        self.twistedAngle     = twistedangle
        self.pDx1             = pDx1
        self.pDx2             = pDx2        
        self.pDy1             = pDy1
        self.pDy2             = pDy2        
        self.pDz              = pDz
        self.nslice           = nslice
        self.refine           = refine
        _registry.addSolid(self)
        self.checkParameters()

    def checkParameters(self):
        if self.twistedAngle > _np.pi:
            raise ValueError("Twisted Angle must be less than 0.5*pi")


    def makeLayers(self, pl1, pl2, pl3, pl4, pu1, pu2, pu3, pu4, pDz, theta, nsl):
        dz = 2*pDz/nsl
        dtheta = theta/nsl
        z = -pDz

        layers = []
        
        bottom = _Layer(pl1,pl2,pl3,pl4, z)
        bottom = bottom.Rotated(-theta*0.5) #overwrite
        layers.append(bottom)
        
        for i in range(nsl):
            pn1 = pl1 + float(i + 1) * (pu1 - pl1) / nsl
            pn2 = pl2 + float(i + 1) * (pu2 - pl2) / nsl
            pn3 = pl3 + float(i + 1) * (pu3 - pl3) / nsl
            pn4 = pl4 + float(i + 1) * (pu4 - pl4) / nsl
            
            z += dz # increment z
            n = _Layer(pn1, pn2, pn3, pn4, z)
            angle = -theta*0.5 + float(i + 1) * dtheta
            nr = n.Rotated(angle) # returns rotated copy 
            layers.append(nr)

        return layers
        
    def pycsgmesh(self):
        pl1 = _TwoVector(-self.pDx1, -self.pDy1)#, self.pDz]
        pl2 = _TwoVector(self.pDx1, -self.pDy1) # self.pDz]
        pl3 = _TwoVector(self.pDx1, self.pDy1) #self.pDz]
        pl4 = _TwoVector(-self.pDx1, self.pDy1) # self.pDz]

        pu1 = _TwoVector(-self.pDx2, -self.pDy2)#, self.pDz]
        pu2 = _TwoVector(self.pDx2, -self.pDy2) # self.pDz]
        pu3 = _TwoVector(self.pDx2, self.pDy2) #self.pDz]
        pu4 = _TwoVector(-self.pDx2, self.pDy2) # self.pDz]pu1 = _TwoVector(-self.pDx2, -self.pDy2)

        m = self.makeLayers(pl1, pl2, pl3, pl4, pu1, pu2, pu3, pu4, self.pDz, self.twistedAngle, self.nslice)

        return self.meshFromLayers(m, self.nslice)
