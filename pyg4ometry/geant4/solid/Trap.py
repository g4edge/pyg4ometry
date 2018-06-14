from SolidBase import SolidBase as _SolidBase
from Wedge     import Wedge as _Wedge
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon


import numpy as _np


class Trap(_SolidBase):
    def __init__(self, name, pDz,
                 pTheta, pDPhi,
                 pDy1, pDx1,
                 pDx2, pAlp1,
                 pDy2, pDx3,
                 pDx4, pAlp2,
                 register=True):
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
        if register:
            _registry.addSolid(self)

    def pycsgmesh(self):

        def listSub(lista, listb):
            result = [a_i - b_i for a_i, b_i in zip(lista, listb)]
            return result

        def listAdd(lista, listb):
            result = [a_i + b_i for a_i, b_i in zip(lista, listb)]
            return result

        hlZ  = self.pDz

        X1   = self.pDx1 #at -pDz
        X2   = self.pDx2
        Y1   = self.pDy1 #at -pDz

        Y2   = self.pDy2
        X3   = self.pDx3
        X4   = self.pDx4

        dX  = 2*_np.sin(self.pTheta)*self.pDz
        dY  = 2*_np.sin(self.pDPhi)*self.pDz

        poly0 = [[-X2,-Y1,-hlZ],[-X1,Y1,-hlZ],[X1,Y1,-hlZ],[X2,-Y1,-hlZ]]
        poly1 = [[-X3,-Y2,hlZ],[-X4,Y2,hlZ],[X4,Y2,hlZ],[X3,-Y2,hlZ]]

        A0=0.0
        A1=0.0

        #Accumulate signed area of top and bottom face quadrilaterals
        for j in range(len(poly0)-1):
            i0  = j
            i1  = i0 + 1
            A0 += (1./2.)*(poly0[i0][0]*poly0[i1][1]-poly0[i1][0]*poly0[i0][1])
            A1 += (1./2.)*(poly1[i0][0]*poly1[i1][1]-poly1[i1][0]*poly1[i0][1])

        Xc0 = 0.0
        Yc0 = 0.0
        Xc1 = 0.0
        Yc1 = 0.0

        #Obtain centroids of top and bottom quadrilaterals
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


        #Slant faces
        for i in range(len(poly0)):
            vert = poly0[i]
            y    = vert[1]
            z    = vert[2]
            x = vert[0] + y*_np.tan(self.pAlp1)

            poly0[i] = [x,y,z]

        for i in range(len(poly1)):
            vert = poly1[i]
            y    = vert[1]
            z    = vert[2]
            x = vert[0] + y*_np.tan(self.pAlp2)

            poly1[i] = [x,y,z]

        #Translate to orginal coordinates
        poly0  = [listAdd(vert, C0) for vert in poly0]
        poly1  = [listAdd(vert, C1) for vert in poly1]

        dXY    = [dX/2, dY/2, 0]
        poly1  = [listAdd(vert, dXY) for vert in poly1]
        poly0  = [listSub(vert, dXY) for vert in poly0]

        polygons = []

        #Top face
        polygons.extend([_Polygon([_Vertex(_Vector(poly1[3][0], poly1[3][1], poly1[3][2]), None),
                                   _Vertex(_Vector(poly1[2][0], poly1[2][1], poly1[2][2]), None),
                                   _Vertex(_Vector(poly1[1][0], poly1[1][1], poly1[1][2]), None),
                                   _Vertex(_Vector(poly1[0][0], poly1[0][1], poly1[0][2]), None)])])

        #Bottom face
        polygons.extend([_Polygon([_Vertex(_Vector(poly0[0][0], poly0[0][1], poly0[0][2]), None),
                                   _Vertex(_Vector(poly0[1][0], poly0[1][1], poly0[1][2]), None),
                                   _Vertex(_Vector(poly0[2][0], poly0[2][1], poly0[2][2]), None),
                                   _Vertex(_Vector(poly0[3][0], poly0[3][1], poly0[3][2]), None)])])

        #Side faces
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


        self.mesh  = _CSG.fromPolygons(polygons)

        return self.mesh
