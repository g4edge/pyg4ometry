from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg:
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm:
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

import numpy as _np
import logging as _log


class Tubs(_SolidBase):
    """
    Constructs a cylindrical section.

    :param name: of solid for registry
    :type name: str
    :param pRMin: inner radius
    :type pRMin: float, Constant, Quantity, Variable
    :param pRMax: outer radius
    :type pRMax: float, Constant, Quantity, Variable
    :param pDz: full length along z
    :type pDz: float, Constant, Quantity, Variable
    :param pSPhi: starting phi angle
    :type pSPhi: float, Constant, Quantity, Variable
    :param pDPhi: angle of segment in phi
    :type pDPhi: float, Constant, Quantity, Variable
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param aunit: angle unit (rad,deg) for solid
    :type aunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int
    """

    def __init__(
        self,
        name,
        pRMin,
        pRMax,
        pDz,
        pSPhi,
        pDPhi,
        registry,
        lunit="mm",
        aunit="rad",
        nslice=None,
        addRegistry=True,
    ):
        super().__init__(name, "Tubs", registry)

        if not nslice:
            nslice = _config.SolidDefaults.Tubs.nslice

        self.lunit = lunit
        self.aunit = aunit

        self.dependents = []
        self.varNames = ["pRMin", "pRMax", "pDz", "pSPhi", "pDPhi", "nslice"]
        self.varUnits = ["lunit", "lunit", "lunit", "aunit", "aunit", None]

        for varName in self.varNames:
            self._addProperty(varName)
            setattr(self, varName, locals()[varName])

        self._twoPiValueCheck("pDPhi", aunit)

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Tubs : {} {} {} {} {} {}".format(
            self.name, self.pRMin, self.pRMax, self.pDz, self.pSPhi, self.pDPhi
        )

    def __str__(self):
        return "Tubs : {} rmin={} rmax={} dz={} sphi={} dphi={} lunit={} aunit={}".format(
            self.name,
            float(self.pRMin),
            float(self.pRMax),
            float(self.pDz),
            float(self.pSPhi),
            float(self.pDPhi),
            self.lunit,
            self.aunit,
        )

    def mesh(self):
        _log.info("tubs.pycsgmesh> antlr")

        import pyg4ometry.gdml.Units as _Units  # TODO move circular import

        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRMin = self.evaluateParameter(self.pRMin) * luval
        pSPhi = self.evaluateParameter(self.pSPhi) * auval
        pDPhi = self.evaluateParameter(self.pDPhi) * auval
        pDz = self.evaluateParameter(self.pDz) * luval / 2
        pRMax = self.evaluateParameter(self.pRMax) * luval

        _log.info("tubs.pycsgmesh> mesh")

        polygons = []

        dPhi = pDPhi / self.nslice

        for i in range(0, self.nslice, 1):
            i1 = i
            i2 = i + 1

            p1 = dPhi * i1 + pSPhi
            p2 = dPhi * i2 + pSPhi

            xRMinP1 = pRMin * _np.cos(p1)
            yRMinP1 = pRMin * _np.sin(p1)
            xRMinP2 = pRMin * _np.cos(p2)
            yRMinP2 = pRMin * _np.sin(p2)

            xRMaxP1 = pRMax * _np.cos(p1)
            yRMaxP1 = pRMax * _np.sin(p1)
            xRMaxP2 = pRMax * _np.cos(p2)
            yRMaxP2 = pRMax * _np.sin(p2)

            ###########################
            # wedge ends
            ###########################
            if pDPhi != 2 * _np.pi and i == 0:
                pass
                vWedg = []
                vWedg.append(_Vertex([xRMinP1, yRMinP1, -pDz]))
                vWedg.append(_Vertex([xRMinP1, yRMinP1, pDz]))
                vWedg.append(_Vertex([xRMaxP1, yRMaxP1, pDz]))
                vWedg.append(_Vertex([xRMaxP1, yRMaxP1, -pDz]))
                vWedg.reverse()
                polygons.append(_Polygon(vWedg))

            if pDPhi != 2 * _np.pi and i == self.nslice - 1:
                pass
                vWedg = []
                vWedg.append(_Vertex([xRMinP2, yRMinP2, -pDz]))
                vWedg.append(_Vertex([xRMaxP2, yRMaxP2, -pDz]))
                vWedg.append(_Vertex([xRMaxP2, yRMaxP2, pDz]))
                vWedg.append(_Vertex([xRMinP2, yRMinP2, pDz]))
                vWedg.reverse()
                polygons.append(_Polygon(vWedg))

            ###########################
            # tube ends
            ###########################
            if pRMin == 0:
                vEnd = []
                vEnd.append(_Vertex([0, 0, -pDz]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, -pDz]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, -pDz]))
                polygons.append(_Polygon(vEnd))

                vEnd = []
                vEnd.append(_Vertex([0, 0, pDz]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, pDz]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, pDz]))
                polygons.append(_Polygon(vEnd))

            else:
                vEnd = []
                vEnd.append(_Vertex([xRMinP1, yRMinP1, -pDz]))
                vEnd.append(_Vertex([xRMinP2, yRMinP2, -pDz]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, -pDz]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, -pDz]))
                polygons.append(_Polygon(vEnd))

                vEnd = []
                vEnd.append(_Vertex([xRMinP1, yRMinP1, pDz]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, pDz]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, pDz]))
                vEnd.append(_Vertex([xRMinP2, yRMinP2, pDz]))
                polygons.append(_Polygon(vEnd))

            ###########################
            # Curved cylinder faces
            ###########################
            vCurv = []
            vCurv.append(_Vertex([xRMaxP1, yRMaxP1, -pDz]))
            vCurv.append(_Vertex([xRMaxP2, yRMaxP2, -pDz]))
            vCurv.append(_Vertex([xRMaxP2, yRMaxP2, pDz]))
            vCurv.append(_Vertex([xRMaxP1, yRMaxP1, pDz]))
            polygons.append(_Polygon(vCurv))

            if pRMin != 0:
                vCurv = []
                vCurv.append(_Vertex([xRMinP1, yRMinP1, -pDz]))
                vCurv.append(_Vertex([xRMinP1, yRMinP1, pDz]))
                vCurv.append(_Vertex([xRMinP2, yRMinP2, pDz]))
                vCurv.append(_Vertex([xRMinP2, yRMinP2, -pDz]))
                polygons.append(_Polygon(vCurv))

        mesh = _CSG.fromPolygons(polygons)

        return mesh
