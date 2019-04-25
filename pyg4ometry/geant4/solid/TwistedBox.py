from SolidBase import SolidBase as _SolidBase
from TwistedSolid import TwistedSolid as _TwistedSolid
from Wedge import Wedge as _Wedge
from TwoVector import TwoVector as _TwoVector
from Layer import Layer as _Layer
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Plane as _Plane
from ...pycsg.geom import Polygon as _Polygon
import numpy as _np

import logging as _log

class TwistedBox(_SolidBase, _TwistedSolid):
    def __init__(self, name, twistedangle, pDx, pDy, pDz, registry=None, nslice=20,
                 refine=0):
        """
        Constructs a box that is twisted through angle 'twistedangle'.

        Inputs:
          name:         string, name of the volume
          twistedangle: float, twist angle, must be less than 0.5*pi
          pDx:          float, half-length in x
          pDy:          float, half-length in y
          pDz:          float, half-length in z
          refine:       int, number of steps to iteratively smoothen the mesh
                             by doubling the number of vertices at every step
        """
        self.type         = 'TwistedBox'
        self.name         = name
        self.twistedAngle = twistedangle
        self.pDx          = pDx
        self.pDy          = pDy
        self.pDz          = pDz
        self.nslice       = nslice
        self.refine       = refine

        self.dependents = []
        self.checkParameters()
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Twisted Box : {} {} {} {} {} {}".format(self.name, self.twistedAngle,
                                                        self.pDx, self.pDy, self.pDz)
    def checkParameters(self):
        if float(self.twistedAngle) > _np.pi:
            raise ValueError("Twisted Angle must be less than 0.5*pi")


    def makeLayers(self, p1, p2, p3, p4, pDz, theta, nslice):
        dz = 2*pDz/nslice
        dtheta = theta/nslice
        z = -pDz

        layers = []

        bottom = _Layer(p1,p2,p3,p4, z)
        bottom = bottom.Rotated(-theta*0.5) #overwrite
        layers.append(bottom)

        for i in range(nslice):
            l = layers[-1].Rotated(dtheta) # returns rotated copy
            z += dz # increment z
            l.z = z # fix z
            layers.append(l)

        return layers

    def pycsgmesh(self):
        _log.info('twistedbox.pycsgmesh> antlr')
        twistedAngle = float(self.twistedAngle)
        pDx = float(self.pDx)/2
        pDy = float(self.pDy)/2
        pDz = float(self.pDz)/2
        refine  = float(self.refine)

        _log.info('twistedbox.pycsgmesh> mesh')
        p1 = _TwoVector(-pDx, -pDy)#, pDz]
        p2 = _TwoVector(pDx, -pDy) # pDz]
        p3 = _TwoVector(pDx, pDy) #pDz]
        p4 = _TwoVector(-pDx, pDy) # pDz]

        m = self.makeLayers(p1, p2, p3, p4, pDz, -twistedAngle, self.nslice)

        return self.meshFromLayers(m, self.nslice)
