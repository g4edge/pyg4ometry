from SolidBase import SolidBase as _SolidBase
from TwistedSolid import TwistedSolid as _TwistedSolid
from TwoVector import TwoVector as _TwoVector
from Layer import Layer as _Layer
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np

class TwistedTrap(_SolidBase, _TwistedSolid):
    def __init__(self, name, twistedangle, pDz, pTheta, pDPhi, pDy1,
                 pDx1, pDx2, pDy2, pDx3, pDx4, pAlp, nslice=20, register=True):
        """
        Constructs a general trapezoid with a twist around one axis.

        Inputs:
          name:          string, name of the volume
          twisted angle: float, angle of twist (<90 deg)
          pDz:           float, half length along z
          pDx1:          float, half length along x of the side at y=-pDy1
          pDx2:          float, half length along x of the side at y=+pDy1
          pTheta:        float, polar angle of the line joining the centres of the faces at -/+pDz
          pPhi:          float, azimuthal angle of the line joining the centres of the faces at -/+pDz
          pDy1:          float, half-length at -pDz
          pDy2:          float, half-length at +pDz
          pDx3:          float, halg-length of the side at y=-pDy2 of the face at +pDz
          pDx4:          float, halg-length of the side at y=+pDy2 of the face at +pDz
          pAlp:          float, angle wrt the y axi from the centre of the side
        """
        self.type         = 'TwistedTrap'
        self.name         = name
        self.twistedangle = twistedangle
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
        self.nslice       = nslice
        self.checkParameters()
        if register:
            _registry.addSolid(self)

    def checkParameters(self):
        if self.twistedangle > _np.pi:
            raise ValueError("Twisted Angle must be less than 0.5*pi")



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


    def pycsgmesh(self):
        #TBC: Meshing not yet completed!

        #Bottom plane coordinates:
        pl1 = _TwoVector(-self.pDx1, -self.pDy1)
        pl2 = _TwoVector(self.pDx1, -self.pDy1)
        pl3 = _TwoVector(self.pDx2, self.pDy1)
        pl4 = _TwoVector(-self.pDx2, self.pDy1)

        #Top plane coordinates:
        pu1 = _TwoVector(-self.pDx3, -self.pDy2)
        pu2 = _TwoVector(self.pDx3, -self.pDy2)
        pu3 = _TwoVector(self.pDx4, self.pDy2)
        pu4 = _TwoVector(-self.pDx4, self.pDy2)

        #making the layers:
        m = self.makeLayers(pl1, pl2, pl3, pl4, pu1, pu2, pu3, pu4, self.pDz, self.twistedangle, self.pTheta,  self.nslice)

        print 'Meshing not completed'

        return self.meshFromLayers(m, self.nslice)
