from ... import config as _config

from .SolidBase             import SolidBase     as _SolidBase
from .GenericPolyhedra import GenericPolyhedra   as  _GenericPolyhedra

import logging as _log

class Polycone(_SolidBase):
    """
    Constructs a solid of rotation using an arbitrary 2D surface.
    
    :param name:   of the solid
    :type name:    str
    :param pSPhi:  starting rotation angle in radians
    :type pSPhi:   float, Constant, Quantity, Variable, Expression
    :param pDPhi:  total rotation angle in radius
    :type pDPhi:   float, Constant, Quantity, Variable, Expression
    :param pZPlns: z-positions of planes used
    :type pZPlns:  list of float, Constant, Quantity, Variable, Expression
    :param pRInr:  inner radii of surface at each z-plane
    :type pRInr:   list of float, Constant, Quantity, Variable, Expression 
    :param pROut:  outer radii of surface at each z-plane
    :type pROut:   list of float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str    
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    
    Optional registration as this solid is used as a temporary solid
    in Polyhedra and needn't be always registered.
    """
    def __init__(self, name, pSPhi, pDPhi, pZpl, pRMin, pRMax,
                 registry, lunit="mm", aunit="rad", nslice=None, addRegistry=True):
        super(Polycone, self).__init__(name, 'Polycone', registry)

        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pZpl    = pZpl
        self.pRMin   = pRMin
        self.pRMax   = pRMax
        self.lunit   = lunit
        self.aunit   = aunit
        self.nslice  = nslice if nslice else _config.SolidDefaults.Polycone.nslice

        self.dependents = []

        self.varNames = ["pSPhi", "pDPhi", "pZpl", "pRMin", "pRMax"]
        self.varUnits = ["aunit", "aunit", "lunit", "lunit", "lunit"]

        self._twoPiValueCheck("pDPhi", self.aunit)

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Polycone : {} {} {}".format(self.name, self.pSPhi, self.pDPhi)

    def mesh(self):

        _log.info("polycone.pycsgmesh>")

        _log.info("polycone.antlr>")

        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pSPhi = self.evaluateParameter(self.pSPhi) * auval
        pDPhi = self.evaluateParameter(self.pDPhi) * auval

        pZpl = [val * luval for val in self.evaluateParameter(self.pZpl)]
        pRMin = [val * luval for val in self.evaluateParameter(self.pRMin)]
        pRMax = [val * luval for val in self.evaluateParameter(self.pRMax)]


        pZ = []
        pR = []

        # first point or rInner
        pZ.append(pZpl[0])
        pR.append(pRMin[0])

        # rest of outer
        pZ.extend(pZpl)
        pR.extend(pRMax)

        # reversed inner
        pZ.extend(pZpl[-1:0:-1])
        pR.extend(pRMin[-1:0:-1])

        ps = _GenericPolyhedra("ps", pSPhi, pDPhi, self.nslice, pR, pZ, self.registry, "mm", "rad", addRegistry=False)

        return ps.mesh()




