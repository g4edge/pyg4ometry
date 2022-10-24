from ... import config as _config

from .SolidBase import SolidBase as _SolidBase
from .Box import cubeNet as _cubeNet

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

import logging as _log
import numpy as _np
import math as _math

class Trap(_SolidBase):
    """
    Constructs a general trapezoid.

    :param name:   name of the volume
    :type name:    str
    :param pDz:    half length along z
    :type pDz:     float, Constant, Quantity, Variable, Expression
    :param pTheta: polar angle of the line joining the centres of the faces at -/+pDz
    :type pTheta:  float, Constant, Quantity, Variable, Expression
    :param pPhi:   azimuthal angle of the line joining the centres of the faces at -/+pDz
    :type pPhi:    float, Constant, Quantity, Variable, Expression
    :param pDy1:   half-length at -pDz
    :type pDy1:    float, Constant, Quantity, Variable, Expression
    :param pDx1:   half length along x of the side at y=-pDy1
    :type pDx1:    float, Constant, Quantity, Variable, Expression
    :param pDx2:   half length along x of the side at y=+pDy1
    :type pDx2:    float, Constant, Quantity, Variable, Expression
    :param pAlp1:  angle wrt the y axis from the centre of the side (lower endcap)
    :type pAlp1:   float, Constant, Quantity, Variable, Expression
    :param pDy2:   half-length at +pDz
    :type pDy2:    float, Constant, Quantity, Variable, Expression
    :param pDx3:   half-length of the side at y=-pDy2 of the face at +pDz
    :type pDx3:    float, Constant, Quantity, Variable, Expression
    :param pDx4:   half-length of the side at y=+pDy2 of the face at +pDz
    :type pDx4:    float, Constant, Quantity, Variable, Expression
    :param pAlp2:  angle wrt the y axis from the centre of the side (upper endcap)
    :type pAlp2:   float, Constant, Quantity, Variable, Expression
    """
    def __init__(self, name, pDz,
                 pTheta, pDPhi,
                 pDy1, pDx1,
                 pDx2, pAlp1,
                 pDy2, pDx3,
                 pDx4, pAlp2,
                 registry,
                 lunit="mm", aunit="rad",
                 addRegistry=True):
        super(Trap, self).__init__(name, 'Trap', registry)

        self.pDz     = pDz
        self.pTheta  = pTheta
        self.pDPhi   = pDPhi
        self.pDy1    = pDy1
        self.pDx1    = pDx1
        self.pDx2    = pDx2
        self.pAlp1   = pAlp1
        self.pDy2    = pDy2
        self.pDx3    = pDx3
        self.pDx4    = pDx4
        self.pAlp2   = pAlp2
        self.lunit   = lunit
        self.aunit   = aunit

        self.dependents = []

        self.varNames = ["pDz", "pTheta", "pDPhi", "pDy1", "pDx1", "pDx2", "pAlp1", "pDy2", "pDx3", "pDx4", "pAlp2"]
        self.varUnits = ["lunit", "aunit", "aunit", "lunit", "lunit", "lunit", "aunit", "lunit", "lunit", "lunit", "aunit"]

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Trap : {} {} {} {} {} {} {} {} {} {} {} {}".format(self.name, self.pDz,
                                                                   self.pTheta, self.pDPhi,
                                                                   self.pDy1, self.pDx1,
                                                                   self.pDx2, self.pAlp1,
                                                                   self.pDy2, self.pDx3,
                                                                   self.pDx4, self.pAlp2)

    def mesh(self):

        _log.info("trap.antlr>")
        import pyg4ometry.gdml.Units as _Units # TODO move circular import

        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pDz  = self.evaluateParameter(self.pDz)*luval/2.

        pDx1   = self.evaluateParameter(self.pDx1)*luval/2.
        pDx2   = self.evaluateParameter(self.pDx2)*luval/2.
        pDy1   = self.evaluateParameter(self.pDy1)*luval/2.

        pDy2   = self.evaluateParameter(self.pDy2)*luval/2.
        pDx3   = self.evaluateParameter(self.pDx3)*luval/2.
        pDx4   = self.evaluateParameter(self.pDx4)*luval/2.

        pTheta = self.evaluateParameter(self.pTheta)*auval
        pDPhi  = self.evaluateParameter(self.pDPhi)*auval

        pAlp1  = self.evaluateParameter(self.pAlp1)*auval
        pAlp2  = self.evaluateParameter(self.pAlp2)*auval

        va1 = _Vector(pDx1, 0, 0)
        va2 = _Vector(pDx2, 0, 0)
        va3 = _Vector(pDx3, 0, 0)
        va4 = _Vector(pDx4, 0, 0)
        vb1 = pDy1/_math.cos(pAlp1) * _Vector(_math.sin(pAlp1), _math.cos(pAlp1), 0)
        vb2 = pDy2/_math.cos(pAlp2) * _Vector(_math.sin(pAlp2), _math.cos(pAlp2), 0)
        vg  = pDz/_math.cos(pTheta) * _Vector(_math.sin(pTheta)*_math.cos(pDPhi),
                                              _math.sin(pTheta)*_math.sin(pDPhi),
                                              _math.cos(pTheta))

        return _cubeNet([-vg - va1 - vb1,
                         -vg - va2 + vb1,
                         -vg + va2 + vb1,
                         -vg + va1 - vb1,
                          vg - va3 - vb2,
                          vg - va4 + vb2,
                          vg + va4 + vb2,
                          vg + va3 - vb2])

        return mesh

