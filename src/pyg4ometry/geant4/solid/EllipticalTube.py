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

import logging as _log

import numpy as _np

class EllipticalTube(_SolidBase):
    """
    Constructs a tube of elliptical cross-section.
    
    :param name: name of the solid
    :type name:  str
    :param pDx:  length in x
    :type pDx:   float, Constant, Quantity, Variable, Expression
    :param pDy:  length in y
    :type pDy:   float, Constant, Quantity, Variable, Expression
    :param pDz:  length in z
    :type pDz:   float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry: Registry
    :param lunit: length unit (nm,um,mm,m,km) for solid
    :type lunit: str
    :param nslice: number of phi elements for meshing
    :type nslice: int  
    :param nstack: number of theta elements for meshing
    :type nstack: int     
    
    """
    def __init__(self, name, pDx, pDy, pDz, registry, lunit="mm",
                 nstack=None, nslice=None, addRegistry=True):
        super(EllipticalTube, self).__init__(name, 'EllipticalTube', registry)

        self.pDx    = pDx
        self.pDy    = pDy
        self.pDz    = pDz
        self.lunit  = lunit
        self.nslice = nslice if nslice else _config.SolidDefaults.EllipticalTube.nslice
        self.nstack = nstack if nstack else _config.SolidDefaults.EllipticalTube.nstack

        self.dependents = []

        self.varNames = ["pDx", "pDy", "pDz"]
        self.varUnits = ["lunit", "lunit", "lunit"]

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "EllipticalTube : {} {} {} {}".format(self.name, self.pDx,
                                                     self.pDy, self.pDz)

    def mesh(self):
        """new meshing based of Tubs meshing"""

        _log.info('ellipticaltube.antlr>')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)

        pDx = self.evaluateParameter(self.pDx)*luval/2.0
        pDy = self.evaluateParameter(self.pDy)*luval/2.0
        pDz = self.evaluateParameter(self.pDz)*luval/2.0

        _log.info('ellipticaltube.pycsgmesh>')

        polygons = []

        sz      = -pDz
        dTheta  = 2*_np.pi/self.nslice
        slices  = self.nslice

        pRMin = 0
        
        for i in range(0,self.nslice,1) :

            i1 = i
            i2 = i+1

            p1 = dTheta*i1 # + pSPhi
            p2 = dTheta*i2 #+ pSPhi

            ###########################
            # tube ends
            ##########################s
            vEnd = []
            vEnd.append(_Vertex([0, 0,pDz]))
            vEnd.append(_Vertex([pDx*_np.cos(p1), pDy*_np.sin(p1),pDz]))
            vEnd.append(_Vertex([pDx*_np.cos(p2), pDy*_np.sin(p2),pDz]))
            polygons.append(_Polygon(vEnd))

            vEnd = []
            vEnd.append(_Vertex([0, 0,-pDz]))
            vEnd.append(_Vertex([pDx*_np.cos(p2), pDy*_np.sin(p2),-pDz]))
            vEnd.append(_Vertex([pDx*_np.cos(p1), pDy*_np.sin(p1),-pDz]))
            polygons.append(_Polygon(vEnd))

            ###########################
            # Curved cylinder faces
            ###########################
            vCurv = []
            vCurv.append(_Vertex([pDx * _np.cos(p1), pDy * _np.sin(p1), -pDz]))
            vCurv.append(_Vertex([pDx * _np.cos(p2), pDy * _np.sin(p2), -pDz]))
            vCurv.append(_Vertex([pDx * _np.cos(p2), pDy * _np.sin(p2), pDz]))
            vCurv.append(_Vertex([pDx * _np.cos(p1), pDy * _np.sin(p1), pDz]))
            polygons.append(_Polygon(vCurv))


        mesh = _CSG.fromPolygons(polygons)

        return mesh
