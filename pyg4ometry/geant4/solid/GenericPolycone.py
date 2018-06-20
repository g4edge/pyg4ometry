from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

import numpy as _np
from copy import deepcopy as _dc

class GenericPolycone(_SolidBase):
    def __init__(self, name, pSPhi, pDPhi, pNSide, pNRZ, pR, pZ,
                 nslice=16, register=True):
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
        if register:
            if register:
                _registry.addSolid(self)

    def pycsgmesh(self):
        polygons = []
        polygonsT = []
        polygonsB = []

        anglerange=self.pDPhi-self.pSPhi
        dPhi  = 2*_np.pi/self.nslice
        stacks  = self.pNRZ
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
            return self.pSPhi+(anglerange/slices)*(i)

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
        for i in range(self.pNRZ):
            appendVertex(verticesB,self.pSPhi,self.pZ[i],self.pR[i])
        polygons.append(_Polygon(verticesB))

	    #Top
        verticesT = []
        for i in range(self.pNRZ):
            appendVertex(verticesT,self.pDPhi,self.pZ[i],self.pR[i])

		#Midsection
        for l in range(1, slices+1):
            maxn = self.pNRZ
            for n in range(maxn):
                n_up = (n+1)%maxn
                polygons.append(_Polygon([_Vertex(defineVertex(GetAngle(l), self.pZ[n], self.pR[n]), None),
                                          _Vertex(defineVertex(GetAngle(l), self.pZ[n_up], self.pR[n_up]), None),
                                          _Vertex(defineVertex(GetAngle(l-1), self.pZ[n_up], self.pR[n_up]), None),
                                          _Vertex(defineVertex(GetAngle(l-1), self.pZ[n], self.pR[n]), None)]))
        polygons.append(_Polygon(verticesT))
        self.mesh     = _CSG.fromPolygons(polygons)
        return self.mesh
