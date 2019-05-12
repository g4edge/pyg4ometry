from SolidBase import SolidBase as _SolidBase
from TwoVector import TwoVector as _TwoVector
from Layer import Layer as _Layer
from TwistedSolid import TwistedSolid as _TwistedSolid
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np
import logging as _log

class TwistedTrd(_SolidBase, _TwistedSolid):
    def __init__(self, name, twistedangle, pDx1, pDx2, pDy1, pDy2,
                 pDz, registry=None, lunit = "mm", aunit = "rad", nstack=20, refine=0):
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
        self.lunit            = lunit
        self.aunit            = aunit 
        self.nstack           = nstack
        self.refine           = refine

        self.dependents = []
        
        self.checkParameters()
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "TwistedTrd : {} {} {} {} {} {} {}".format(self.name, self.twistedAngle,
                                                          self.pDx1, self.pDx2,
                                                          self.pDy1, self.pDy2,
                                                          self.pDz)

    def checkParameters(self):
        if float(self.twistedAngle) > _np.pi:
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
        _log.info('twistedtrd.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        twistedAngle = float(self.twistedAngle)
        pDx1 = float(self.pDx1)/2.
        pDx2 = float(self.pDx2)/2.
        pDy1 = float(self.pDy1)/2.
        pDy2 = float(self.pDy2)/2.
        pDz = float(self.pDz)/2.

        _log.info('hype.pycsgmesh> mesh')
        pl1 = _TwoVector(-pDx1, -pDy1)#, pDz]
        pl2 = _TwoVector(pDx1, -pDy1) # pDz]
        pl3 = _TwoVector(pDx1, pDy1) #pDz]
        pl4 = _TwoVector(-pDx1, pDy1) # pDz]

        pu1 = _TwoVector(-pDx2, -pDy2)#, pDz]
        pu2 = _TwoVector(pDx2, -pDy2) # pDz]
        pu3 = _TwoVector(pDx2, pDy2) #pDz]
        pu4 = _TwoVector(-pDx2, pDy2) # pDz]pu1 = _TwoVector(-pDx2, -pDy2)

        m = self.makeLayers(pl1, pl2, pl3, pl4, pu1, pu2, pu3, pu4, pDz, twistedAngle, self.nstack)

        return self.meshFromLayers(m, self.nstack)
