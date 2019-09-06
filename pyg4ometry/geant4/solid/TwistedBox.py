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

    """
    Constructs a box that is twisted though angle twisted angle

    :param name:         of the solid
    :type name:          str
    :param twistedangle: twist angle, must be less than pi/2
    :type twistedangle:  float, Constant, Quantity, Variable, Expression
    :param pDx:          length in x
    :type pDx:           float, Constant, Quantity, Variable, Expression
    :param pDy:          length in y
    :type pDy:           float, Constant, Quantity, Variable, Expression
    :param pDz:          length in z
    :type pDz:           float, Constant, Quantity, Variable, Expression
    :param refine:       number of steps to iteratively smoothen the mesh by doubling the number of vertices at every step
    :type refine:        int
    :param registry:     for storing solid
    :type registry:      Registry
    :param lunit:        length unit (nm,um,mm,m,km) for solid
    :type lunit:         str    
    :param aunit:        angle unit (rad,deg) for solid
    :type aunit:         str
    :param nstack:       Not written
    :type nstack:        int
    """


    def __init__(self, name, twistedangle, pDx, pDy, pDz, registry,
                 lunit = "mm", aunit = "rad",
                 nstack=20, refine=0, addRegistry=True):
        self.type         = 'TwistedBox'
        self.name         = name
        self.twistedAngle = twistedangle
        self.pDx          = pDx
        self.pDy          = pDy
        self.pDz          = pDz
        self.lunit        = lunit
        self.aunit        = aunit
        self.nstack       = nstack
        self.refine       = refine

        self.dependents = []

        self.varNames = ["twistedAngle", "pDx", "pDy","pDz"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry
        self.checkParameters()

    def __repr__(self):
        return "Twisted Box : {} {} {} {} {}".format(self.name, self.twistedAngle,
                                                     self.pDx, self.pDy, self.pDz)
    def checkParameters(self):
        if self.evaluateParameter(self.twistedAngle) > _np.pi:
            raise ValueError("Twisted Angle must be less than 0.5*pi")


    def makeLayers(self, p1, p2, p3, p4, pDz, theta, nstack):
        dz = 2*pDz/nstack
        dtheta = theta/nstack
        z = -pDz

        layers = []

        bottom = _Layer(p1,p2,p3,p4, z)
        bottom = bottom.Rotated(-theta*0.5) #overwrite
        layers.append(bottom)

        for i in range(nstack):
            l = layers[-1].Rotated(dtheta) # returns rotated copy
            z += dz # increment z
            l.z = z # fix z
            layers.append(l)

        return layers

    def pycsgmesh(self):
        _log.info('twistedbox.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        twistedAngle = self.evaluateParameter(self.twistedAngle)*auval
        pDx = self.evaluateParameter(self.pDx)/2.*luval
        pDy = self.evaluateParameter(self.pDy)/2.*luval
        pDz = self.evaluateParameter(self.pDz)/2.*luval
        refine  = self.evaluateParameter(self.refine)

        _log.info('twistedbox.pycsgmesh> mesh')
        p1 = _TwoVector(-pDx, -pDy)#, pDz]
        p2 = _TwoVector(pDx, -pDy) # pDz]
        p3 = _TwoVector(pDx, pDy) #pDz]
        p4 = _TwoVector(-pDx, pDy) # pDz]

        m = self.makeLayers(p1, p2, p3, p4, pDz, -twistedAngle, self.nstack)

        return self.meshFromLayers(m, self.nstack)
