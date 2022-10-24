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

class Paraboloid(_SolidBase):
    """
    Constructs a paraboloid with possible cuts along the z axis.
    
    :param name:     of solid 
    :type name:      str
    :param pDz:      length along z
    :type pDz:       float, Constant, Quantity, Variable, Expression
    :param pR1:      radius at -Dz/2
    :type pR1:       float, Constant, Quantity, Variable, Expression
    :param pR2:      radius at +Dz/2 (pR2 > pR1)
    :type pR2:       float, Constant, Quantity, Variable, Expression
    :param registry: for storing solid
    :type registry:  Registry
    :param lunit:    length unit (nm,um,mm,m,km) for solid
    :type lunit:     str    
    :param nslice:   number of phi elements for meshing
    :type nslice:    int  
    :param nstack:   number of theta elements for meshing
    :type nstack:    int       
    
    """
    def __init__(self, name, pDz, pR1, pR2, registry, lunit="mm",
                 nslice=16, nstack=8, addRegistry=True):
        super(Paraboloid, self).__init__(name, 'Paraboloid', registry)

        self.pDz    = pDz
        self.pR1    = pR1
        self.pR2    = pR2
        self.lunit  = lunit
        self.nstack = nstack
        self.nslice = nslice

        self.dependents = []

        self.varNames = ["pDz", "pR1", "pR2"]
        self.varUnits = ["lunit", "lunit", "lunit"]

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Paraboloid : {} {} {} {}".format(self.name, self.pDz,
                                                 self.pR1, self.pR2)

    def mesh(self):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import

        _log.info("paraboloid.antlr>")

        uval = _Units.unit(self.lunit)
        pDz    = self.evaluateParameter(self.pDz)/2.0*uval
        pR1    = self.evaluateParameter(self.pR1)*uval
        pR2    = self.evaluateParameter(self.pR2)*uval

        _log.info("paraboloid.pycsgmesh>")
        polygons = []

        sz      = -pDz
        dz      = 2*pDz/self.nstack
        dTheta  = 2*_np.pi/self.nslice
        stacks  = self.nstack
        slices  = self.nslice

        k1 = (pR2 ** 2 - pR1 ** 2)/(2*pDz)
        k2 = (pR1**2 + pR2**2)/2.0

        for i in range(0,slices):

            i1 = i
            i2 = i + 1

            for j in range(0,stacks):
                j1 = j
                j2 = j + 1

                z1 = j1 * dz + sz
                rho1 = _np.sqrt(k1*z1 + k2)
                x1 = rho1 * _np.cos(dTheta * i1)
                y1 = rho1 * _np.sin(dTheta * i1)

                z2 = j2 * dz + sz
                rho2 = _np.sqrt(k1*z2 + k2)
                x2 = rho2 * _np.cos(dTheta * i1)
                y2 = rho2 * _np.sin(dTheta * i1)

                z3 = j2 * dz + sz
                rho3 = _np.sqrt(k1*z3 + k2)
                x3 = rho3 * _np.cos(dTheta * i2)
                y3 = rho3 * _np.sin(dTheta * i2)

                z4 = j1 * dz + sz
                rho4 = _np.sqrt(k1*z4 + k2)
                x4 = rho4 * _np.cos(dTheta * i2)
                y4 = rho4 * _np.sin(dTheta * i2)

                vertices = []

                if rho1 != 0 :
                    vertices.append(_Vertex([x1, y1, z1]))
                vertices.append(_Vertex([x2, y2, z2]))
                vertices.append(_Vertex([x3, y3, z3]))
                vertices.append(_Vertex([x4, y4, z4]))
                polygons.append(_Polygon(vertices))

                if rho1 != 0 and j == 0 :
                    end = []
                    end.append(_Vertex([ 0, 0,-pDz]))
                    end.append(_Vertex([x1,y1,-pDz]))
                    end.append(_Vertex([x4,y4,-pDz]))
                    polygons.append(_Polygon(end))

                if j == stacks-1 :
                    end = []
                    end.append(_Vertex([ 0, 0,pDz]))
                    end.append(_Vertex([x2,y2,pDz]))
                    end.append(_Vertex([x3,y3,pDz]))
                    end.reverse()
                    polygons.append(_Polygon(end))


        mesh  = _CSG.fromPolygons(polygons)

        return mesh
