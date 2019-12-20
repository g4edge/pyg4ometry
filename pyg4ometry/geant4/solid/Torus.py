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
                 registry, lunit="mm", aunit="rad", nslice=50, nstack=10,
                 addRegistry=True):

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

        self.dependents = []

        self.varNames = ["pRmin", "pRmax", "pRtor","pSPhi","pDPhi","nslice","nstack","lunit","aunit"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Torus : {} {} {} {} {} {}".format(self.name, self.pRmin,
                                                  self.pRmax, self.pRtor,
                                                  self.pSPhi, self.pDPhi)

    def pycsgmeshOld(self):

        _log.info("torus.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin = self.evaluateParameter(self.pRmin)*luval
        pRmax = self.evaluateParameter(self.pRmax)*luval
        pRtor = self.evaluateParameter(self.pRtor)*luval
        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval

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

    def pycsgmesh(self):

        _log.info("torus.antlr>")

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRmin = self.evaluateParameter(self.pRmin)*luval
        pRmax = self.evaluateParameter(self.pRmax)*luval
        pRtor = self.evaluateParameter(self.pRtor)*luval
        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval

        _log.info("torus.pycsgmesh>")
        polygons = []

        nstack  = self.nstack
        nslice  = self.nslice

        dTheta  = 2*_np.pi/nstack
        dPhi    = (pDPhi-pSPhi)/nslice

        for j0 in range(nslice):
            j1 = j0
            j2 = j0 + 1

            for i0 in range(nstack):
                i1 = i0
                i2 = i0 + 1

                x1_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.cos(dPhi * j1)
                y1_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.sin(dPhi * j1)
                z1_outter =           pRmax * _np.sin(dTheta * i1)

                x2_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.cos(dPhi * j1)
                y2_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.sin(dPhi * j1)
                z2_outter =           pRmax * _np.sin(dTheta * i2)

                x3_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.cos(dPhi * j2)
                y3_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.sin(dPhi * j2)
                z3_outter =           pRmax * _np.sin(dTheta * i2)

                x4_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.cos(dPhi * j2)
                y4_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.sin(dPhi * j2)
                z4_outter =           pRmax * _np.sin(dTheta * i1)

                vertices_outter = []

                vertices_outter.append(_Vertex([x1_outter, y1_outter, z1_outter], None))
                vertices_outter.append(_Vertex([x2_outter, y2_outter, z2_outter], None))
                vertices_outter.append(_Vertex([x3_outter, y3_outter, z3_outter], None))
                vertices_outter.append(_Vertex([x4_outter, y4_outter, z4_outter], None))

                polygons.append(_Polygon(vertices_outter))

                if 0 < pRmin < pRmax:

                    x1_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.cos(dPhi * j1)
                    y1_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.sin(dPhi * j1)
                    z1_inner =           pRmin * _np.sin(dTheta * i1)

                    x2_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.cos(dPhi * j1)
                    y2_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.sin(dPhi * j1)
                    z2_inner =           pRmin * _np.sin(dTheta * i2)

                    x3_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.cos(dPhi * j2)
                    y3_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.sin(dPhi * j2)
                    z3_inner =           pRmin * _np.sin(dTheta * i2)

                    x4_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.cos(dPhi * j2)
                    y4_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.sin(dPhi * j2)
                    z4_inner =           pRmin * _np.sin(dTheta * i1)

                    vertices_inner = []

                    vertices_inner.append(_Vertex([x1_inner, y1_inner, z1_inner], None))
                    vertices_inner.append(_Vertex([x2_inner, y2_inner, z2_inner], None))
                    vertices_inner.append(_Vertex([x3_inner, y3_inner, z3_inner], None))
                    vertices_inner.append(_Vertex([x4_inner, y4_inner, z4_inner], None))

                    polygons.append(_Polygon(vertices_inner))


        ###### wedges #####

        if ((pDPhi - pSPhi) != 2 * _np.pi):

            for i0 in range(nstack):
                i1 = i0
                i2 = i0 + 1

                x1_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.cos(pSPhi)
                y1_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.sin(pSPhi)
                z1_inner =           pRmin * _np.sin(dTheta * i1)

                x2_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.cos(pSPhi)
                y2_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.sin(pSPhi)
                z2_inner =           pRmin * _np.sin(dTheta * i2)

                x1_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.cos(pSPhi)
                y1_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.sin(pSPhi)
                z1_outter =           pRmax * _np.sin(dTheta * i1)

                x2_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.cos(pSPhi)
                y2_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.sin(pSPhi)
                z2_outter =           pRmax * _np.sin(dTheta * i2)

                vertices_wedges_S = []

                vertices_wedges_S.append(_Vertex([x1_inner, y1_inner, z1_inner], None))
                vertices_wedges_S.append(_Vertex([x2_inner, y2_inner, z2_inner], None))
                vertices_wedges_S.append(_Vertex([x2_outter, y2_outter, z2_outter], None))
                vertices_wedges_S.append(_Vertex([x1_outter, y1_outter, z1_outter], None))

                polygons.append(_Polygon(vertices_wedges_S))

                #############################################################################

                x4_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.cos(pDPhi)
                y4_outter = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.sin(pDPhi)
                z4_outter =           pRmax * _np.sin(dTheta * i1)

                x3_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.cos(pDPhi)
                y3_outter = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.sin(pDPhi)
                z3_outter =           pRmax * _np.sin(dTheta * i2)

                x3_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.cos(pDPhi)
                y3_inner = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.sin(pDPhi)
                z3_inner =           pRmin * _np.sin(dTheta * i2)

                x4_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.cos(pDPhi)
                y4_inner = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.sin(pDPhi)
                z4_inner =           pRmin * _np.sin(dTheta * i1)
                
                vertices_wedges_D = []

                vertices_wedges_D.append(_Vertex([x4_outter, y4_outter, z4_outter], None))
                vertices_wedges_D.append(_Vertex([x3_outter, y3_outter, z3_outter], None))
                vertices_wedges_D.append(_Vertex([x3_inner, y3_inner, z3_inner], None))
                vertices_wedges_D.append(_Vertex([x4_inner, y4_inner, z4_inner], None))

                polygons.append(_Polygon(vertices_wedges_D))

        mesh    = _CSG.fromPolygons(polygons)

        return mesh
