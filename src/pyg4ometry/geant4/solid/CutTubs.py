from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

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

import numpy as _np
import logging as _log

class CutTubs(_SolidBase):
    """
    Constructs a cylindrical section with end face cuts. Note pLowNorm and pHighNorm can be
    lists of floats, Constants, Quantities or Variables.

    :param name: of solid for registry
    :type name: str
    :param pRMin: Inner radius
    :type pRMin: float, Constant, Quantity, Variable
    :param pRMax: Outer radius
    :type pRMax: float, Constant, Quantity, Variable
    :param pDz: length along z
    :type pDz: float, Constant, Quantity, Variable
    :param pSPhi: starting phi angle
    :type pSPhi: float, Constant, Quantity, Variable
    :param pDPhi: angle of segment
    :type pDPhi: float, Constant, Quantity, Variable
    :param pLowNorm: normal vector of the cut plane at -pDz/2
    :type pLowNorm: list 
    :param pHighNorm: normal vector of the cut plane at +pDz/2
    :type pHighNorm: list 
    """
    def __init__(self, name, pRMin, pRMax, pDz, pSPhi, pDPhi,
                 pLowNorm, pHighNorm, registry, lunit="mm",
                 aunit="rad", nslice=None, addRegistry=True):
        super(CutTubs, self).__init__(name, 'CutTubs', registry)

        if not nslice:
            nslice = _config.SolidDefaults.CutTubs.nslice

        self.lunit = lunit
        self.aunit = aunit
        self.dependents = []
        self.varNames = ["pRMin", "pRMax", "pDz", "pSPhi", "pDPhi",
                         "pLowNorm", "pHighNorm", "nslice"]
        self.varUnits = ["lunit", "lunit", "lunit", "aunit", "aunit",
                         "lunit", "lunit", None]

        for varName in self.varNames:
            self._addProperty(varName)
            setattr(self, varName, locals()[varName])

        self._twoPiValueCheck("pDPhi", self.aunit)

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        # Low norm and high norm excluded as they are lists
        return "Cut tubs : {} {} {} {} {} {}".format(self.name, self.pRMin, self.pRMax,
                                                        self.pDz, self.pSPhi, self.pDPhi)

    def mesh(self):
        # 0.00943803787231 66
        _log.info('tubs.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRMin = self.evaluateParameter(self.pRMin)*luval
        pSPhi = self.evaluateParameter(self.pSPhi)*auval
        pDPhi = self.evaluateParameter(self.pDPhi)*auval # issue with 2*pi
        pDz   = self.evaluateParameter(self.pDz)*luval/2
        pRMax = self.evaluateParameter(self.pRMax)*luval

        pHighNorm = [val*luval for val in self.evaluateParameter(self.pHighNorm)]
        pLowNorm = [val*luval for val in self.evaluateParameter(self.pLowNorm)]

        _log.info('tubs.pycsgmesh> mesh')

        polygons = []

        dPhi = pDPhi/self.nslice

        for i in range(0,self.nslice,1) :

            i1 = i
            i2 = i+1

            p1 = dPhi*i1 + pSPhi
            p2 = dPhi*i2 + pSPhi

            xRMinP1     = pRMin*_np.cos(p1)
            yRMinP1     = pRMin*_np.sin(p1)
            xRMaxP1     = pRMax*_np.cos(p1)
            yRMaxP1     = pRMax*_np.sin(p1)

            xRMinP2     = pRMin*_np.cos(p2)
            yRMinP2     = pRMin*_np.sin(p2)
            xRMaxP2     = pRMax*_np.cos(p2)
            yRMaxP2     = pRMax*_np.sin(p2)

            zLowRMinP1  = (-pLowNorm[2]*pDz - pLowNorm[0]*xRMinP1 - pLowNorm[1]*yRMinP1)/pLowNorm[2]
            zLowRMaxP1  = (-pLowNorm[2]*pDz - pLowNorm[0]*xRMaxP1 - pLowNorm[1]*yRMaxP1)/pLowNorm[2]
            zHighRMinP1 = (pHighNorm[2]*pDz - pHighNorm[0]*xRMinP1 - pHighNorm[1]*yRMinP1)/pHighNorm[2]
            zHighRMaxP1 = (pHighNorm[2]*pDz - pHighNorm[0]*xRMaxP1 - pHighNorm[1]*yRMaxP1)/pHighNorm[2]

            zLowRMinP2  = (-pLowNorm[2]*pDz - pLowNorm[0]*xRMinP2 - pLowNorm[1]*yRMinP2)/pLowNorm[2]
            zLowRMaxP2  = (-pLowNorm[2]*pDz - pLowNorm[0]*xRMaxP2 - pLowNorm[1]*yRMaxP2)/pLowNorm[2]
            zHighRMinP2 = (pHighNorm[2]*pDz - pHighNorm[0]*xRMinP2 - pHighNorm[1]*yRMinP2)/pHighNorm[2]
            zHighRMaxP2 = (pHighNorm[2]*pDz - pHighNorm[0]*xRMaxP2 - pHighNorm[1]*yRMaxP2)/pHighNorm[2]

            ###########################
            # wedge ends
            ###########################
            if pDPhi != 2*_np.pi and i == 0:
                vWedg = []
                vWedg.append(_Vertex([xRMinP1,yRMinP1, zLowRMinP1]))
                vWedg.append(_Vertex([xRMinP1,yRMinP1, zHighRMinP1]))
                vWedg.append(_Vertex([xRMaxP1,yRMaxP1, zHighRMaxP1]))
                vWedg.append(_Vertex([xRMaxP1,yRMaxP1, zLowRMaxP1]))
                vWedg.reverse()
                polygons.append(_Polygon(vWedg))

            if pDPhi != 2*_np.pi and i == self.nslice-1 :
                vWedg = []
                vWedg.append(_Vertex([xRMinP2,yRMinP2, zLowRMinP2]))
                vWedg.append(_Vertex([xRMaxP2,yRMaxP2, zLowRMaxP2]))
                vWedg.append(_Vertex([xRMaxP2,yRMaxP2, zHighRMaxP2]))
                vWedg.append(_Vertex([xRMinP2,yRMinP2, zHighRMinP2]))
                vWedg.reverse()
                polygons.append(_Polygon(vWedg))

            ###########################
            # tube ends
            ###########################
            if pRMin == 0:
                vEnd = []
                vEnd.append(_Vertex([0,0,-pDz]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zLowRMaxP2]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zLowRMaxP1]))
                polygons.append(_Polygon(vEnd))

                vEnd = []
                vEnd.append(_Vertex([0,0, pDz]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zHighRMaxP1]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zHighRMaxP2]))
                polygons.append(_Polygon(vEnd))

            else :
                vEnd = []
                vEnd.append(_Vertex([xRMinP1, yRMinP1, zLowRMinP1]))
                vEnd.append(_Vertex([xRMinP2, yRMinP2, zLowRMinP2]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zLowRMaxP2]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zLowRMaxP1]))
                polygons.append(_Polygon(vEnd))

                vEnd = []
                vEnd.append(_Vertex([xRMinP1, yRMinP1, zHighRMinP1]))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zHighRMaxP1]))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zHighRMaxP2]))
                vEnd.append(_Vertex([xRMinP2, yRMinP2, zHighRMinP2]))
                polygons.append(_Polygon(vEnd))

            ###########################
            # Curved cylinder faces
            ###########################
            vCurv = []
            vCurv.append(_Vertex([xRMaxP1, yRMaxP1, zLowRMaxP1]))
            vCurv.append(_Vertex([xRMaxP2, yRMaxP2, zLowRMaxP2]))
            vCurv.append(_Vertex([xRMaxP2, yRMaxP2, zHighRMaxP2]))
            vCurv.append(_Vertex([xRMaxP1, yRMaxP1, zHighRMaxP1]))
            polygons.append(_Polygon(vCurv))

            if pRMin != 0 :
                vCurv = []
                vCurv.append(_Vertex([xRMinP1, yRMinP1, zLowRMinP1]))
                vCurv.append(_Vertex([xRMinP1, yRMinP1, zHighRMinP1]))
                vCurv.append(_Vertex([xRMinP2, yRMinP2, zHighRMinP2]))
                vCurv.append(_Vertex([xRMinP2, yRMinP2, zLowRMinP2]))
                polygons.append(_Polygon(vCurv))

        mesh = _CSG.fromPolygons(polygons)

        return mesh
