from SolidBase import SolidBase as _SolidBase

from Tubs import Tubs as _Tubs
from Plane import Plane as _Plane

from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np
import logging as _log

class CutTubs(_SolidBase):
    """
    Constructs a cylindrical section with end face cuts. Note pLowNorm and pHighNorm can be lists of floats, Constants, Quantities or Variables.

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
                 aunit="rad", nslice=16, addRegistry = True):

        self.type      = 'CutTubs'
        self.name      = name

        if addRegistry :
            registry.addSolid(self)
        self.registry = registry

        self.nslice    = nslice
        self.lunit     = lunit
        self.aunit     = aunit
        self.dependents = []
        self.varNames = ["pRMin", "pRMax", "pDz", "pSPhi", "pDPhi",
                         "pLowNorm", "pHighNorm", "lunit", "aunit", "nslice"]

        for name in self.varNames:
            self._addProperty(name)
            setattr(self, name, locals()[name])


    def __repr__(self):
        # Low norm and high norm exlcluded as they are lists
        return "Cut tubs : {} {} {} {} {} {}".format(self.name, self.pRMin, self.pRMax,
                                                        self.pDz, self.pSPhi, self.pDPhi)
    def pycsgmesh(self):
        # 0.0381021499634 80
        _log.info('cuttubs.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pRMin     = self.evaluateParameter(self.pRMin)*luval
        pRMax     = self.evaluateParameter(self.pRMax)*luval
        pDz       = self.evaluateParameter(self.pDz)*luval/2.
        pSPhi     = self.evaluateParameter(self.pSPhi)*auval
        pDPhi     = self.evaluateParameter(self.pDPhi)*auval

        pHighNorm = [val*luval for val in self.evaluateParameter(self.pHighNorm)]
        pLowNorm = [val*luval for val in self.evaluateParameter(self.pLowNorm)]

        _log.info('cuttubs.pycsgmesh> mesh')
        mesh = _Tubs("tubs_temp", pRMin, pRMax, 2 * pDz * 10, pSPhi, pDPhi, # Units are already rendered
                     registry=self.registry, nslice=self.nslice, addRegistry=False).pycsgmesh()

        if pLowNorm != [0,0,-1] or pHighNorm != [0,0,1]:
                
            zlength = 3 * pDz  # make the dimensions of the semi-infinite plane large enough
            if pHighNorm != [0,0,1]:
                pHigh = _Plane("pHigh_temp", pHighNorm, pDz, zlength).pycsgmesh()
                mesh = mesh.subtract(pHigh)
            if pLowNorm != [0,0,-1]:
                pLow  = _Plane("pLow_temp", pLowNorm, -pDz, zlength).pycsgmesh()
                mesh = mesh.subtract(pLow)
                
            return mesh
        else : 
            return mesh


    def pycsgmeshNew(self):
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
                vWedg.append(_Vertex([xRMinP1,yRMinP1, zLowRMinP1],None))
                vWedg.append(_Vertex([xRMinP1,yRMinP1, zHighRMinP1],None))
                vWedg.append(_Vertex([xRMaxP1,yRMaxP1, zHighRMaxP1],None))
                vWedg.append(_Vertex([xRMaxP1,yRMaxP1, zLowRMaxP1],None))
                polygons.append(_Polygon(vWedg))

            if pDPhi != 2*_np.pi and i == self.nslice-1 :
                vWedg = []
                vWedg.append(_Vertex([xRMinP2,yRMinP2, zLowRMinP2],None))
                vWedg.append(_Vertex([xRMaxP2,yRMaxP2, zLowRMaxP2],None))
                vWedg.append(_Vertex([xRMaxP2,yRMaxP2, zHighRMaxP2],None))
                vWedg.append(_Vertex([xRMinP2,yRMinP2, zHighRMinP2],None))
                polygons.append(_Polygon(vWedg))

            ###########################
            # tube ends
            ###########################
            if pRMin == 0:
                vEnd = []
                vEnd.append(_Vertex([0,0,-pDz],None))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zLowRMaxP1],None))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zLowRMaxP2],None))
                polygons.append(_Polygon(vEnd))

                vEnd = []
                vEnd.append(_Vertex([ 0,0, pDz],None))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zHighRMaxP2],None))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zHighRMaxP1],None))
                polygons.append(_Polygon(vEnd))

            else :
                vEnd = []
                vEnd.append(_Vertex([xRMinP1, yRMinP1, zLowRMinP1],None))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zLowRMaxP1],None))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zLowRMaxP2],None))
                vEnd.append(_Vertex([xRMinP2, yRMinP2, zLowRMinP2],None))

                polygons.append(_Polygon(vEnd))

                vEnd = []
                vEnd.append(_Vertex([xRMinP1, yRMinP1, zHighRMinP1],None))
                vEnd.append(_Vertex([xRMinP2, yRMinP2, zHighRMinP2],None))
                vEnd.append(_Vertex([xRMaxP2, yRMaxP2, zHighRMaxP2],None))
                vEnd.append(_Vertex([xRMaxP1, yRMaxP1, zHighRMaxP1],None))

                polygons.append(_Polygon(vEnd))

            ###########################
            # Curved cylinder faces
            ###########################
            vCurv = []
            vCurv.append(_Vertex([xRMaxP1, yRMaxP1, zLowRMaxP1],None))
            vCurv.append(_Vertex([xRMaxP1, yRMaxP1, zHighRMaxP1],None))
            vCurv.append(_Vertex([xRMaxP2, yRMaxP2, zHighRMaxP2],None))
            vCurv.append(_Vertex([xRMaxP2, yRMaxP2, zLowRMaxP2],None))
            polygons.append(_Polygon(vCurv))

            if pRMin != 0 :
                vCurv = []
                vCurv.append(_Vertex([xRMinP1, yRMinP1, zLowRMinP1], None))
                vCurv.append(_Vertex([xRMinP2, yRMinP2, zLowRMinP2], None))
                vCurv.append(_Vertex([xRMinP2, yRMinP2, zHighRMinP2],None))
                vCurv.append(_Vertex([xRMinP1, yRMinP1, zHighRMinP1],None))
                polygons.append(_Polygon(vCurv))

        mesh = _CSG.fromPolygons(polygons)

        return mesh
