from SolidBase import SolidBase as _SolidBase
from Wedge     import Wedge     as _Wedge
from pyg4ometry.geant4.Registry import registry as _registry
from pyg4ometry.pycsg.core import CSG     as _CSG
from pyg4ometry.pycsg.geom import Vector  as _Vector
from pyg4ometry.pycsg.geom import Vertex  as _Vertex
from pyg4ometry.pycsg.geom import Polygon as _Polygon


import numpy as _np


class Trap(_SolidBase):
    def __init__(self, name, pDz,
                 pTheta, pDPhi,
                 pDy1, pDx1,
                 pDx2, pAlp1,
                 pDy2, pDx3,
                 pDx4, pAlp2,
                 registry=None):
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
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return 'Trap: '+self.name+' '+str(self.pDz)+' '+str(self.pTheta)+' '+str(self.pDPhi)+' '+str(self.pDy1)+' '+str(self.pDx1)+' '+str(self.pDx2)+' '+str(self.pAlp1)+' '+str(self.pDy2)+' '+str(self.pDx3)+' '+str(self.pDx4)+' '+str(self.pAlp2)

    def pycsgmesh(self):

        def listSub(lista, listb):
            result = [a_i - b_i for a_i, b_i in zip(lista, listb)]
            return result

        def listAdd(lista, listb):
            result = [a_i + b_i for a_i, b_i in zip(lista, listb)]
            return result

        pDz  = float(self.pDz)

        pDx1   = float(self.pDx1) #at -pDz
        pDx2   = float(self.pDx2)
        pDy1   = float(self.pDy1) #at -pDz

        pDy2   = float(self.pDy2)
        pDx3   = float(self.pDx3)
        pDx4   = float(self.pDx4)

        pTheta = float(self.pTheta)
        pDPhi  = float(self.pDPhi)
        
        pAlp1  = float(self.pAlp1)
        pAlp2  = float(self.pAlp2)

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
