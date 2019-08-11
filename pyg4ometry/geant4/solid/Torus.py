from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from pyg4ometry.pycsg.core import CSG as _CSG
from pyg4ometry.pycsg.geom import Vector as _Vector
from pyg4ometry.pycsg.geom import Vertex as _Vertex
from pyg4ometry.pycsg.geom import Polygon as _Polygon
import numpy as _np
import logging as _log


class Torus(_SolidBase):
    """
    Constructs a torus.
    
    :param name:   string, name of the volume
    :type name:    str
    :param pRmin:  innder radius
    :type pRmin:   float, Constant, Quantity, Variable, Expression
    :param pRmax:  outer radius
    :type pRMax:   float, Constant, Quantity, Variable, Expression
    :param pRtor:  swept radius of torus
    :type pRtor:   float, Constant, Quantity, Variable, Expression
    :param pSphi:  start phi angle
    :type pSphi:   float, Constant, Quantity, Variable, Expression
    :param pDPhi:  delta phi angle
    :type pDPhi:   float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str    
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    :param nstack: number of theta elements for meshing
    :type nstack: int         

    """

    def __init__(self, name, pRmin, pRmax, pRtor, pSPhi, pDPhi,
                 registry = None, lunit="mm",aunit="rad",nslice=16, nstack=16):

        self.type    = 'Torus'
        self.name    = name
        self.pRmin   = pRmin
        self.pRmax   = pRmax
        self.pRtor   = pRtor
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.nslice  = nslice
        self.nstack  = nstack
        self.lunit   = lunit
        self.aunit   = aunit
        self.mesh = None

        self.dependents = []

        self.varNames = ["pRmin", "pRmax", "pStor","pSPhi","pDPhi"]

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Torus : {} {} {} {} {} {}".format(self.name, self.pRmin,
                                                  self.pRmax, self.pRtor,
                                                  self.pSPhi, self.pDPhi)

    def pycsgmesh(self):

        _log.info("torus.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin = float(self.pRmin)*luval
        pRmax = float(self.pRmax)*luval
        pRtor = float(self.pRtor)*luval
        pSPhi = float(self.pSPhi)*auval
        pDPhi = float(self.pDPhi)*auval

        _log.info("torus.pycsgmesh>")
        polygons = []

        nstack  = self.nstack
        nslice  = self.nslice
        dTheta  = 2*_np.pi/nstack
        dPhi    = 2*_np.pi/nslice


        def appendVertex(vertices, theta, phi, r):
            c = _Vector([0,0,0])
            x = r*_np.cos(theta)+pRtor
            z = r*_np.sin(theta)
            y = 0
            x_rot = _np.cos(phi)*x - _np.sin(phi)*y
            y_rot = _np.sin(phi)*x + _np.cos(phi)*y

            d = _Vector(
                x_rot,
                y_rot,
                z)

            vertices.append(_Vertex(c.plus(d), None))

        rinout    = [pRmin, pRmax]
        meshinout = []

        for r in rinout:
            if not r:
                continue
            for j0 in range(nslice):
                j1 = j0 + 0.5
                j2 = j0 + 1
                for i0 in range(nstack):
                    i1 = i0 + 0.5
                    i2 = i0 + 1
                    verticesN = []
                    appendVertex(verticesN, i1 * dTheta, j1 * dPhi + pSPhi, r)
                    appendVertex(verticesN, i2 * dTheta, j2 * dPhi + pSPhi, r)
                    appendVertex(verticesN, i0 * dTheta, j2 * dPhi + pSPhi, r)
                    polygons.append(_Polygon(verticesN))
                    verticesS = []
                    appendVertex(verticesS, i1 * dTheta, j1 * dPhi + pSPhi, r)
                    appendVertex(verticesS, i0 * dTheta, j0 * dPhi + pSPhi, r)
                    appendVertex(verticesS, i2 * dTheta, j0 * dPhi + pSPhi, r)
                    polygons.append(_Polygon(verticesS))
                    verticesW = []
                    appendVertex(verticesW, i1 * dTheta, j1 * dPhi + pSPhi, r)
                    appendVertex(verticesW, i0 * dTheta, j2 * dPhi + pSPhi, r)
                    appendVertex(verticesW, i0 * dTheta, j0 * dPhi + pSPhi, r)
                    polygons.append(_Polygon(verticesW))
                    verticesE = []
                    appendVertex(verticesE, i1 * dTheta, j1 * dPhi + pSPhi, r)
                    appendVertex(verticesE, i2 * dTheta, j0 * dPhi + pSPhi, r)
                    appendVertex(verticesE, i2 * dTheta, j2 * dPhi + pSPhi, r)
                    polygons.append(_Polygon(verticesE))

            mesh      = _CSG.fromPolygons(polygons)
            meshinout.append(mesh)
            polygons = []

        if pRmin != 0:
            mesh  = meshinout[0].subtract(meshinout[1])

        else:
           mesh = meshinout[0].inverse()

        if pDPhi != 2*_np.pi:
            wrmax    = 3*pRtor #make sure intersection wedge is much larger than solid
            wzlength = 5*pRmax

            pWedge = _Wedge("wedge_temp",wrmax, pSPhi, pDPhi, wzlength).pycsgmesh()
            mesh = pWedge.intersect(mesh)

        return mesh
