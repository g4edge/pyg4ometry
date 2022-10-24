from ... import config as _config

from .SolidBase import SolidBase as _SolidBase
from .TwoVector import TwoVector as _TwoVector
from .Layer import Layer as _Layer
from .TwistedSolid import TwistedSolid as _TwistedSolid

import numpy as _np
import logging as _log

class TwistedTrd(_SolidBase, _TwistedSolid):
    """
    Constructs a twisted general trapezoid.
    
    :param name:            of solid
    :type name:             str
    :param twistedangle:    twist angle, must be less than 0.5*pi
    :type twistedangle:     float, Constant, Quantity, Variable, Expression
    :param pDx1:            length in x at surface positioned at -pDz/2
    :type pDx1:             float, Constant, Quantity, Variable, Expression
    :param pDx2:            length in x at surface positioned at +pDz/2
    :type pDx2:             float, Constant, Quantity, Variable, Expression
    :param pDy1:            length in y at surface positioned at -pDz/2
    :type pDy1:             float, Constant, Quantity, Variable, Expression
    :param pDy2:            length in y at surface positioned at +pDz/2
    :type pDy2:             float, Constant, Quantity, Variable, Expression
    :param pDz:             length in z
    :type pDz:              float, Constant, Quantity, Variable, Expression
    :param refine:          number of steps to iteratively smoothen the mesh by doubling the number of vertices at every step
    :type refine:           int
    :param registry:        for storing solid
    :type registry:         Registry
    :param lunit:           length unit (nm,um,mm,m,km) for solid
    :type lunit:            str
    :param aunit:           angle unit (rad,deg) for solid
    :type aunit:            str    
    :param nstack:          number of theta elements for meshing
    :type nstack:           int       
    """
    def __init__(self, name, twistedangle, pDx1, pDx2, pDy1, pDy2,
                 pDz, registry, lunit="mm", aunit="rad",
                 nstack=None, refine=0, addRegistry=True):
        super(TwistedTrd, self).__init__(name, 'TwistedTrd', registry)

        self.twistedAngle     = twistedangle
        self.pDx1             = pDx1
        self.pDx2             = pDx2
        self.pDy1             = pDy1
        self.pDy2             = pDy2
        self.pDz              = pDz
        self.lunit            = lunit
        self.aunit            = aunit
        self.nstack           = nstack if nstack else _config.SolidDefaults.TwistedTrap.nstack
        self.refine           = refine

        self.dependents = []

        self.varNames = ["twistedAngle", "pDx1", "pDx2", "pDy1", "pDy2", "pDz"]
        self.varUnits = ["aunit", "lunit", "lunit", "lunit", "lunit", "lunit"]

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "TwistedTrd : {} {} {} {} {} {} {}".format(self.name, self.twistedAngle,
                                                          self.pDx1, self.pDx2,
                                                          self.pDy1, self.pDy2,
                                                          self.pDz)

    def checkParameters(self):
        if self.evaluateParameterWithUnits('twistedAngle') > _np.pi:
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

    def mesh(self):
        _log.info('twistedtrd.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        twistedAngle = self.evaluateParameter(self.twistedAngle)*auval
        pDx1 = self.evaluateParameter(self.pDx1)/2.*luval
        pDx2 = self.evaluateParameter(self.pDx2)/2.*luval
        pDy1 = self.evaluateParameter(self.pDy1)/2.*luval
        pDy2 = self.evaluateParameter(self.pDy2)/2.*luval
        pDz = self.evaluateParameter(self.pDz)/2.*luval

        _log.info('twistedtrd.mesh> mesh')
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
