from SolidBase import SolidBase as _SolidBase
from Wedge     import Wedge     as _Wedge
from pyg4ometry.pycsg.core import CSG     as _CSG
from pyg4ometry.pycsg.geom import Vector  as _Vector
from pyg4ometry.pycsg.geom import Vertex  as _Vertex
from pyg4ometry.pycsg.geom import Polygon as _Polygon
import logging as _log

import numpy as _np


class Trap(_SolidBase):
    def __init__(self, name, pDz,
                 pTheta, pDPhi,
                 pDy1, pDx1,
                 pDx2, pAlp1,
                 pDy2, pDx3,
                 pDx4, pAlp2,
                 registry,
                 lunit="mm", aunit="rad",
                 addRegistry=True):
        """
        Constructs a general trapezoid.

        Inputs:
          name:   string, name of the volume
          pDz:    float, half length along z
          pTheta: float, polar angle of the line joining the centres of the faces at -/+pDz
          pPhi:   float, azimuthal angle of the line joining the centres of the faces at -/+pDz
          pDy1:   float, half-length at -pDz
          pDx1:   float, half length along x of the side at y=-pDy1
          pDx2:   float, half length along x of the side at y=+pDy1
          pAlp1:  float, angle wrt the y axis from the centre of the side (lower endcap)
          pDy2:   float, half-length at +pDz
          pDx3:   float, half-length of the side at y=-pDy2 of the face at +pDz
          pDx4:   float, half-length of the side at y=+pDy2 of the face at +pDz

          pAlp2:  float, angle wrt the y axis from the centre of the side (upper endcap)
        """

        self.type    = "Trap"
        self.name    = name
        self.pDz     = pDz
        self.pTheta  = pTheta
        self.pDPhi   = pDPhi
        self.pDy1    = pDy1
        self.pDx1    = pDx1
        self.pDx2    = pDx2
        self.pAlp1   = pAlp1
        self.pDy2    = pDy2
        self.pDx3    = pDx3
        self.pDx4    = pDx4
        self.pAlp2   = pAlp2
        self.lunit   = lunit
        self.aunit   = aunit

        self.dependents = []

        self.varNames = ["pDz", "pTheta", "pDPhi","pDy1","pDx1","pDx2","pAlp1","pDy2","pDx3","pDx4","pAlp2","lunit","aunit"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

    def __repr__(self):
        return "Trap : {} {} {} {} {} {} {} {} {} {} {} {}".format(self.name, self.pDz,
                                                                   self.pTheta, self.pDPhi,
                                                                   self.pDy1, self.pDx1,
                                                                   self.pDx2, self.pAlp1,
                                                                   self.pDy2, self.pDx3,
                                                                   self.pDx4, self.pAlp2)

    def pycsgmesh(self):

        def listSub(lista, listb):
            result = [a_i - b_i for a_i, b_i in zip(lista, listb)]
            return result

        def listAdd(lista, listb):
            result = [a_i + b_i for a_i, b_i in zip(lista, listb)]
            return result

        _log.info("trap.antlr>")
        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        pDz  = self.evaluateParameter(self.pDz)*luval/2.

        pDx1   = self.evaluateParameter(self.pDx1)*luval/2. #at -pDz
        pDx2   = self.evaluateParameter(self.pDx2)*luval/2.
        pDy1   = self.evaluateParameter(self.pDy1)*luval/2. #at -pDz

        pDy2   = self.evaluateParameter(self.pDy2)*luval/2.
        pDx3   = self.evaluateParameter(self.pDx3)*luval/2.
        pDx4   = self.evaluateParameter(self.pDx4)*luval/2.

        pTheta = self.evaluateParameter(self.pTheta)*auval
        pDPhi  = self.evaluateParameter(self.pDPhi)*auval

        pAlp1  = self.evaluateParameter(self.pAlp1)*auval
        pAlp2  = self.evaluateParameter(self.pAlp2)*auval

        _log.info("trap.pycsgmesh>")
        dX  = 2*_np.sin(pTheta)*pDz
        dY  = 2*_np.sin(pDPhi)*pDz

        poly0 = [[-pDx2,-pDy1,-pDz],[-pDx1,pDy1,-pDz],[pDx1,pDy1,-pDz],[pDx2,-pDy1,-pDz]]
        poly1 = [[-pDx3,-pDy2,pDz],[-pDx4,pDy2,pDz],[pDx4,pDy2,pDz],[pDx3,-pDy2,pDz]]

        A0=0.0
        A1=0.0

        # Accumulate signed area of top and bottom face quadrilaterals
        for j in range(len(poly0)-1):
            i0  = j
            i1  = i0 + 1
            A0 += (1./2.)*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1])
            A1 += (1./2.)*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1])

        Xc0 = 0.0
        Yc0 = 0.0
        Xc1 = 0.0
        Yc1 = 0.0

        # Obtain centroids of top and bottom quadrilaterals
        for j in range(len(poly0)-1):
            i0 = j
            i1 = i0+1
            Xc0   += (1/(6*A0))*(poly0[i0][0]+poly0[i1][0])*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1])
            Yc0   += (1/(6*A0))*(poly0[i0][1]+poly0[i1][1])*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1])
            Xc1   += (1/(6*A1))*(poly1[i0][0]+poly1[i1][0])*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1])
            Yc1   += (1/(6*A1))*(poly1[i0][1]+poly1[i1][1])*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1])

        C0  = [Xc0, Yc0, 0]
        C1  = [Xc1, Yc1, 0]

        #Center in X-Y plane
        poly0  = [listSub(vert, C0) for vert in poly0]
        poly1  = [listSub(vert, C1) for vert in poly1]


        # Slant faces
        for i in range(len(poly0)):
            vert = poly0[i]
            y    = vert[1]
            z    = vert[2]
            x = vert[0] + y*_np.tan(pAlp1)

            poly0[i] = [x,y,z]

        for i in range(len(poly1)):
            vert = poly1[i]
            y    = vert[1]
            z    = vert[2]
            x = vert[0] + y*_np.tan(pAlp2)

            poly1[i] = [x,y,z]

        # Translate to orginal coordinates
        poly0  = [listAdd(vert, C0) for vert in poly0]
        poly1  = [listAdd(vert, C1) for vert in poly1]

        dXY    = [dX/2, dY/2, 0]
        poly1  = [listAdd(vert, dXY) for vert in poly1]
        poly0  = [listSub(vert, dXY) for vert in poly0]

        polygons = []

        # Top face
        polygons.extend([_Polygon([_Vertex(_Vector(poly1[3][0], poly1[3][1], poly1[3][2]), None),
                                   _Vertex(_Vector(poly1[2][0], poly1[2][1], poly1[2][2]), None),
                                   _Vertex(_Vector(poly1[1][0], poly1[1][1], poly1[1][2]), None),
                                   _Vertex(_Vector(poly1[0][0], poly1[0][1], poly1[0][2]), None)])])

        # Bottom face
        polygons.extend([_Polygon([_Vertex(_Vector(poly0[0][0], poly0[0][1], poly0[0][2]), None),
                                   _Vertex(_Vector(poly0[1][0], poly0[1][1], poly0[1][2]), None),
                                   _Vertex(_Vector(poly0[2][0], poly0[2][1], poly0[2][2]), None),
                                   _Vertex(_Vector(poly0[3][0], poly0[3][1], poly0[3][2]), None)])])

        # Side faces
        polygons.extend([_Polygon([_Vertex(_Vector(poly1[1][0], poly1[1][1], poly1[1][2]), None),
                                   _Vertex(_Vector(poly0[1][0], poly0[1][1], poly0[1][2]), None),
                                   _Vertex(_Vector(poly0[0][0], poly0[0][1], poly0[0][2]), None),
                                   _Vertex(_Vector(poly1[0][0], poly1[0][1], poly1[0][2]), None)])])
        polygons.extend([_Polygon([_Vertex(_Vector(poly1[2][0], poly1[2][1], poly1[2][2]), None),
                                   _Vertex(_Vector(poly0[2][0], poly0[2][1], poly0[2][2]), None),
                                   _Vertex(_Vector(poly0[1][0], poly0[1][1], poly0[1][2]), None),
                                   _Vertex(_Vector(poly1[1][0], poly1[1][1], poly1[1][2]), None)])])
        polygons.extend([_Polygon([_Vertex(_Vector(poly1[3][0], poly1[3][1], poly1[3][2]), None),
                                   _Vertex(_Vector(poly0[3][0], poly0[3][1], poly0[3][2]), None),
                                   _Vertex(_Vector(poly0[2][0], poly0[2][1], poly0[2][2]), None),
                                   _Vertex(_Vector(poly1[2][0], poly1[2][1], poly1[2][2]), None)])])
        polygons.extend([_Polygon([_Vertex(_Vector(poly1[0][0], poly1[0][1], poly1[0][2]), None),
                                   _Vertex(_Vector(poly0[0][0], poly0[0][1], poly0[0][2]), None),
                                   _Vertex(_Vector(poly0[3][0], poly0[3][1], poly0[3][2]), None),
                                   _Vertex(_Vector(poly1[3][0], poly1[3][1], poly1[3][2]), None)])])


        mesh  = _CSG.fromPolygons(polygons)

        return mesh
