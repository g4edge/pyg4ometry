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
                 registry, lunit="mm", aunit="rad",
                 nslice=None, nstack=None, addRegistry=True):
        super(Torus, self).__init__(name, 'Torus', registry)

        self.pRmin   = pRmin
        self.pRmax   = pRmax
        self.pRtor   = pRtor
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.nslice  = nslice if nslice else _config.SolidDefaults.Torus.nslice
        self.nstack  = nstack if nstack else _config.SolidDefaults.Torus.nstack
        self.lunit   = lunit
        self.aunit   = aunit

        self.dependents = []

        self.varNames = ["pRmin", "pRmax", "pRtor", "pSPhi", "pDPhi", "nslice", "nstack"]
        self.varUnits = ["lunit", "lunit", "lunit", "aunit", "aunit", None, None]

        self._twoPiValueCheck("pDPhi", self.aunit)

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Torus : {} {} {} {} {} {}".format(self.name, self.pRmin,
                                                  self.pRmax, self.pRtor,
                                                  self.pSPhi, self.pDPhi)

    def mesh(self):

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
        dPhi    = pDPhi/nslice

        for j0 in range(nslice):
            j1 = j0
            j2 = j0 + 1

            for i0 in range(nstack):
                i1 = i0
                i2 = i0 + 1

                xRMaxP1T1 = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.cos(pSPhi + dPhi * j1)
                yRMaxP1T1 = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.sin(pSPhi + dPhi * j1)
                zRMaxP1T1 =           pRmax * _np.sin(dTheta * i1)

                xRMaxP1T2 = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.cos(pSPhi + dPhi * j1)
                yRMaxP1T2 = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.sin(pSPhi + dPhi * j1)
                zRMaxP1T2 =           pRmax * _np.sin(dTheta * i2)

                xRMaxP2T2 = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.cos(pSPhi + dPhi * j2)
                yRMaxP2T2 = (pRtor + (pRmax * _np.cos(dTheta * i2))) * _np.sin(pSPhi + dPhi * j2)
                zRMaxP2T2 =           pRmax * _np.sin(dTheta * i2)

                xRMaxP2T1 = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.cos(pSPhi + dPhi * j2)
                yRMaxP2T1 = (pRtor + (pRmax * _np.cos(dTheta * i1))) * _np.sin(pSPhi + dPhi * j2)
                zRMaxP2T1 =           pRmax * _np.sin(dTheta * i1)

                vertices_outer = []
                vertices_outer.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                vertices_outer.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                vertices_outer.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                vertices_outer.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                vertices_outer.reverse()
                polygons.append(_Polygon(vertices_outer))

                xRMinP1T1 = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.cos(pSPhi + dPhi * j1)
                yRMinP1T1 = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.sin(pSPhi + dPhi * j1)
                zRMinP1T1 =           pRmin * _np.sin(dTheta * i1)

                xRMinP1T2 = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.cos(pSPhi + dPhi * j1)
                yRMinP1T2 = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.sin(pSPhi + dPhi * j1)
                zRMinP1T2 =           pRmin * _np.sin(dTheta * i2)

                xRMinP2T2 = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.cos(pSPhi + dPhi * j2)
                yRMinP2T2 = (pRtor + (pRmin * _np.cos(dTheta * i2))) * _np.sin(pSPhi + dPhi * j2)
                zRMinP2T2 =           pRmin * _np.sin(dTheta * i2)

                xRMinP2T1 = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.cos(pSPhi + dPhi * j2)
                yRMinP2T1 = (pRtor + (pRmin * _np.cos(dTheta * i1))) * _np.sin(pSPhi + dPhi * j2)
                zRMinP2T1 =           pRmin * _np.sin(dTheta * i1)

                if 0 < pRmin < pRmax:
                    vertices_inner = []
                    vertices_inner.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                    vertices_inner.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2]))
                    vertices_inner.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                    vertices_inner.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1]))
                    # vertices_inner.reverse()
                    polygons.append(_Polygon(vertices_inner))

                if pDPhi != 2*_np.pi :
                    if j1 == 0 :
                        end= []
                        if pRmin != 0 :
                            end.append(_Vertex([xRMinP1T1, yRMinP1T1, zRMinP1T1]))
                        end.append(_Vertex([xRMinP1T2, yRMinP1T2, zRMinP1T2]))
                        end.append(_Vertex([xRMaxP1T2, yRMaxP1T2, zRMaxP1T2]))
                        end.append(_Vertex([xRMaxP1T1, yRMaxP1T1, zRMaxP1T1]))
                        end.reverse()
                        polygons.append(_Polygon(end))

                    if j1 == nslice-1 :
                        end= []
                        if pRmin != 0 :
                            end.append(_Vertex([xRMinP2T1, yRMinP2T1, zRMinP2T1]))
                        end.append(_Vertex([xRMinP2T2, yRMinP2T2, zRMinP2T2]))
                        end.append(_Vertex([xRMaxP2T2, yRMaxP2T2, zRMaxP2T2]))
                        end.append(_Vertex([xRMaxP2T1, yRMaxP2T1, zRMaxP2T1]))
                        #end.reverse()
                        polygons.append(_Polygon(end))


        mesh    = _CSG.fromPolygons(polygons)

        return mesh
