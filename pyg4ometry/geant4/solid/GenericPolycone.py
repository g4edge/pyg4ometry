from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import logging as _log
import numpy as _np
from copy import deepcopy as _dc

class GenericPolycone(_SolidBase):
    def __init__(self, name, pSPhi, pDPhi, pNSide, pNRZ, pR, pZ,
                 nslice=16, registry=None):
        """
        Constructs a solid of rotation using an arbitrary 2D surface defined by a series of (r,z) coordinates.

        Inputs:
        name = name
        pSPhi = Angle Phi at start of rotation
        pDPhi = Angle Phi at end of rotation
        pNSide = Number of sides to polygon
        pNRZ = number of (r,z) coordinate points given
        pR = r coordinate list
		pZ = z coordinate list
        """
        self.type    = 'GenericPolycone'
        self.name    = name
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pNSide    = pNSide
        self.pNRZ = pNRZ
        self.pR   = pR
        self.pZ   = pZ
        self.nslice  = nslice

        self.dependents = []

        if register:
            _registry.addSolid(self)

    def pycsgmesh(self):
        _log.info("polycone.antlr>")
        pSPhi = float(self.pSPhi)
        pDPhi = float(self.pDPhi)
        pNSide = int(self.pNSide)
        pNRZ = int(self.pNRZ)
        pR = [float(val) for val in self.pR]
        pZ = [float(val) for val in self.pZ]

        _log.info("polycone.pycsgmesh>")
        polygons = []
        polygonsT = []
        polygonsB = []

        anglerange=pDPhi-pSPhi
        dPhi  = 2*_np.pi/self.nslice
        stacks  = pNRZ
        slices  = self.nslice

        def defineVertex(theta, z, r):
            c = _Vector([0,0,0])
            x = r*_np.cos(theta)
            y = r*_np.sin(theta)

            d = _Vector(
                x,
                y,
                z)
            return d
        def GetAngle(i):
            return pSPhi+(anglerange/slices)*(i)

        def appendVertex(vertices, theta, z, r, norm=[]):
            c = _Vector([0,0,0])
            x = r*_np.cos(theta)
            y = r*_np.sin(theta)

            d = _Vector(
                x,
                y,
                z)

            if not norm:
                n = d
            else:
                n = _Vector(norm)
            vertices.append(_Vertex(c.plus(d), None))

		#Bottom
        verticesB = []
        for i in range(pNRZ):
            appendVertex(verticesB,pSPhi,pZ[i],pR[i])
        polygons.append(_Polygon(verticesB))

	    #Top
        verticesT = []
        for i in range(pNRZ):
            appendVertex(verticesT,pDPhi,pZ[i],pR[i])

		#Midsection
        for l in range(1, slices+1):
            maxn = pNRZ
            for n in range(maxn):
                n_up = (n+1)%maxn
                polygons.append(_Polygon([_Vertex(defineVertex(GetAngle(l), pZ[n], pR[n]), None),
                                          _Vertex(defineVertex(GetAngle(l), pZ[n_up], pR[n_up]), None),
                                          _Vertex(defineVertex(GetAngle(l-1), pZ[n_up], pR[n_up]), None),
                                          _Vertex(defineVertex(GetAngle(l-1), pZ[n], pR[n]), None)]))
        polygons.append(_Polygon(verticesT))
        mesh     = _CSG.fromPolygons(polygons)
        return mesh
