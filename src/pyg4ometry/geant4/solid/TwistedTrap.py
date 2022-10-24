from ... import config as _config

from .SolidBase import SolidBase as _SolidBase
from .TwistedSolid import TwistedSolid as _TwistedSolid
from .TwoVector import TwoVector as _TwoVector
from .Layer import Layer as _Layer

import logging as _log
import numpy as _np

# from memory_profiler import profile as _profile

class TwistedTrap(_SolidBase, _TwistedSolid):
    """
    Constructs a general trapezoid with a twist around one axis.
    
    :param name:          of the solid
    :type name:           str
    :param twistedAngle:  angle of twist (<90 deg)
    :type twistedSngle:   float, Constant, Quantity, Variable, Expression
    :param pDz:           length along z
    :type pDz:            float, Constant, Quantity, Variable, Expression
    :param pDx1:          length along x of the side at y=-pDy1/2
    :type pDx1:           float, Constant, Quantity, Variable, Expression
    :param pDx2:          length along x of the side at y=+pDy1/2
    :type pDx2:           float, Constant, Quantity, Variable, Expression
    :param pTheta:        polar angle of the line joining the centres of the faces at -/+pDz/2
    :type pTheta:         float, Constant, Quantity, Variable, Expression
    :param pPhi:          azimuthal angle of the line joining the centres of the faces at -/+pDz/2
    :type pPhi:           float, Constant, Quantity, Variable, Expression
    :param pDy1:          length at -pDz/2
    :type pDy1:           float, Constant, Quantity, Variable, Expression
    :param pDy2:          length at +pDz/2
    :type pDy2:           float, Constant, Quantity, Variable, Expression
    :param pDx3:          length of the side at y=-pDy2 of the face at +pDz/2
    :type pDx3:           float, Constant, Quantity, Variable, Expression
    :param pDx4:          length of the side at y=+pDy2 of the face at +pDz/2
    :type pDx4:           float, Constant, Quantity, Variable, Expression
    :param pAlp:          angle wrt the y axi from the centre of the side
    :type pAlp:           float, Constant, Quantity, Variable, Expression
    :param registry:     for storing solid
    :type registry:      Registry
    :param lunit:        length unit (nm,um,mm,m,km) for solid
    :type lunit:         str    
    :param aunit:        angle unit (rad,deg) for solid
    :type aunit:         str
    """
    def __init__(self, name, twistedAngle, pDz, pTheta, pDPhi, pDy1,
                 pDx1, pDx2, pDy2, pDx3, pDx4, pAlp, registry,
                 lunit = "mm", aunit = "rad", nstack=None, addRegistry=True):
        super(TwistedTrap, self).__init__(name, 'TwistedTrap', registry)

        self.twistedAngle = twistedAngle
        self.pDz          = pDz
        self.pTheta       = pTheta
        self.pDPhi        = pDPhi
        self.pDy1         = pDy1
        self.pDx1         = pDx1
        self.pDx2         = pDx2
        self.pDy2         = pDy2
        self.pDx3         = pDx3
        self.pDx4         = pDx4
        self.pAlp         = pAlp
        self.lunit        = lunit 
        self.aunit        = aunit
        self.nstack       = nstack if nstack else _config.SolidDefaults.TwistedTrap.nstack

        self.dependents = []

        self.varNames = ["twistedAngle", "pDz", "pTheta", "pDPhi", "pDy1", "pDx1", "pDx2", "pDy2", "pDx3", "pDx4", "pAlp"]
        self.varUnits = ["aunit", "lunit", "aunit", "aunit", "lunit", "lunit", "lunit", "lunit", "lunit", "lunit", "aunit"]

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def checkParameters(self):
        if self.evaluateParameterWithUnits('twistedAngle') > _np.pi:
            raise ValueError("Twisted Angle must be less than 0.5*pi")

    def __repr__(self):
        return "Twisted Trap : {} {} {}".format(self.name, self.twistedAngle, self.pDz)

    def makeLayers(self, pl1, pl2, pl3, pl4, pu1, pu2, pu3, pu4, pDz, twist, theta, nsl):
        dz      = 2*pDz/float(nsl)
        dtwist  = twist/float(nsl)
        z       = -pDz

        r       = 2 * pDz * _np.tan(theta)
        dr      = r/nsl

        layers = []

        bottom = _Layer(pl1,pl2,pl3,pl4, z)
        bottom = bottom.Rotated(-twist*0.5) #overwrite
        b1 = bottom[0] - 0.5 * float(r)
        b2 = bottom[1] - 0.5 * float(r)
        b3 = bottom[2] - 0.5 * float(r)
        b4 = bottom[3] - 0.5 * float(r)
        bottom2 = _Layer(b1, b2, b3, b4, z)
        layers.append(bottom2)

        for i in range(nsl):
            pn1 = (pl1 + float(i + 1) * (pu1 - pl1) / nsl) #+ (float(i + 1) * float(dr))
            pn2 = (pl2 + float(i + 1) * (pu2 - pl2) / nsl) #+ (float(i + 1) * float(dr))
            pn3 = (pl3 + float(i + 1) * (pu3 - pl3) / nsl) #+ (float(i + 1) * float(dr))
            pn4 = (pl4 + float(i + 1) * (pu4 - pl4) / nsl) #+ (float(i + 1) * float(dr))

            z += dz # increment z
            n = _Layer(pn1, pn2, pn3, pn4, z)
            angle = -twist*0.5 + float(i + 1) * dtwist
            nr = n.Rotated(angle) # returns rotated copy
            shift = -float(r) * 0.5 + float(i + 1) * float(dr)
            n1 = nr[0] + shift #float(i + 1) * float(dr)
            n2 = nr[1] + shift #float(i + 1) * float(dr)
            n3 = nr[2] + shift #float(i + 1) * float(dr)
            n4 = nr[3] + shift #float(i + 1) * float(dr)
            nn = _Layer(n1, n2, n3, n4, z)
            layers.append(nn)

        return layers

    # @_profile
    def mesh(self):
        _log.info('twistedtrap.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        twistedAngle = self.evaluateParameter(self.twistedAngle)*auval
        pDz = self.evaluateParameter(self.pDz)/2.*luval
        pTheta = self.evaluateParameter(self.pTheta)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval
        pDy1 = self.evaluateParameter(self.pDy1)/2.*luval
        pDx1 = self.evaluateParameter(self.pDx1)/2.*luval
        pDx2 = self.evaluateParameter(self.pDx2)/2.*luval
        pDy2 = self.evaluateParameter(self.pDy2)/2.*luval
        pDx3 = self.evaluateParameter(self.pDx3)/2.*luval
        pDx4 = self.evaluateParameter(self.pDx4)/2.*luval
        pAlp = self.evaluateParameter(self.pAlp)*auval

        _log.info('twistedtrap.pycsgmesh> mesh')
        #Bottom plane coordinates:
        pl1 = _TwoVector(-pDx1, -pDy1)
        pl2 = _TwoVector(pDx1, -pDy1)
        pl3 = _TwoVector(pDx2, pDy1)
        pl4 = _TwoVector(-pDx2, pDy1)

        #Top plane coordinates:
        pu1 = _TwoVector(-pDx3, -pDy2)
        pu2 = _TwoVector(pDx3, -pDy2)
        pu3 = _TwoVector(pDx4, pDy2)
        pu4 = _TwoVector(-pDx4, pDy2)

        #making the layers:
        m = self.makeLayers(pl1, pl2, pl3, pl4, pu1, pu2, pu3, pu4, pDz,
                            twistedAngle, pTheta,  self.nstack)

        return self.meshFromLayers(m, self.nstack)
