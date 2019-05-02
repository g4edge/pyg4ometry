from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon
import logging as _log

import numpy as _np
from copy import deepcopy as _dc

class TwistedTubs(_SolidBase):
    def __init__(self, name, endinnerrad, endouterrad, zlen, phi, twistedangle,
                 registry=None, nslice=16, nstack=16):
        """
        Creates a twisted tube segement. Note that only 1 constructor is supprted.

        Inputs:
          name:         string, name of the volume
          endinnerrad:  float, inner radius at the end of the segment
          endinnerrad:  float, outer radius at the end of the segment
          zlen:         float, length of the tube segement
          twsitedandhe: float, twist angle
        """

        self.type         = 'TwistedTubs'
        self.name         = name
        self.endinnerrad  = endinnerrad
        self.endouterrad  = endouterrad
        self.zlen         = zlen
        self.phi          = phi
        self.twistedangle = twistedangle
        self.nslice       = nslice
        self.nstack       = nstack

        self.dependents = []

        # self.checkParameters()
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "TwistedTubs : {} {} {} {} {}".format(self.name, self.name,
                                                     self.endinnerrad, self.endouterrad,
                                                     self.zlen, self.twsitedangle,
                                                     self.nslice, self.nstack)

    def makeLayers(self, verts_bot, verts_top):

        layers = []

        z1 = 2*float(self.dz)
        z0 = -float(self.dz)

        for i in range(self.nstack+1):
            z = z0 + i*z1/self.nstack
            dz = (z - z0) / (z1 - z0)

            verts_i = []
            for k in range(4):
                v_bot = verts_bot[k]
                v_top = verts_top[k]

                # Linearly interpolate
                x = v_bot[0] + (dz * (v_top[0] - v_bot[0]))
                y = v_bot[1] + (dz * (v_top[1] - v_bot[1]))

                verts_i.append(_Vertex(_Vector(x, y, z), None))

            layers.append(verts_i)

        return layers


    def pycsgmesh(self):
        _log.info("polycone.antlr>")
        endinnerrad = float(self.endinnerrad)
        endouterrad = float(self.endouterrad)
        zlen = float(self.zlen)
        phi  = float(self.phi)
        twistedangle = float(self.twistedangle)

        _log.info("polycone.basicmesh>")
        polygons = []

        stacks  = self.nstack
        slices  = self.nslice

        pSPhi =  3*_np.pi/2.
        dPhi  = phi/slices
        sz = -zlen/2.
        dz = zlen/stacks
        stwist = -twistedangle/2.
        dtwist = twistedangle/stacks

        def appendVertex(vertices, theta, z, r, rotangle=0):
            # Generate points on a circle
            c = _Vector([0,0,0])
            x = r*_np.cos(theta)
            y = r*_np.sin(theta)

            # Rotate the points
            xr = x*_np.cos(rotangle) - y*_np.sin(rotangle)
            yr = x*_np.sin(rotangle) + y*_np.cos(rotangle)

            vertices.append(_Vertex(c.plus(_Vector(xr,yr,z)), None))

        offs = 1.e-25 #Small offset to avoid point degenracy when the radius is zero. TODO: make more robust

        # Mesh the sides
        rinout    = [endinnerrad, endouterrad]
        for R in rinout:
            for j0 in range(stacks):
                j1 = j0 + 0.5
                j2 = j0 + 1
                for i0 in range(slices):
                    i1 = i0 + 0.5
                    i2 = i0 + 1
                    k0 = i0 if R == endouterrad else i2  #needed to ensure the surface normals on the inner and outer surface are obeyed
                    k1 = i2 if R == endouterrad else i0

                    verticesA = []
                    appendVertex(verticesA, k0 * dPhi + pSPhi, sz + j0*dz, R + offs, stwist + j0*dtwist)
                    appendVertex(verticesA, k1 * dPhi + pSPhi, sz + j0*dz, R + offs, stwist + j0*dtwist)
                    appendVertex(verticesA, k1 * dPhi + pSPhi, sz + j2*dz, R + offs, stwist + j2*dtwist)
                    verticesB = []
                    appendVertex(verticesB, k1 * dPhi + pSPhi, sz + j2*dz, R + offs, stwist + j2*dtwist)
                    appendVertex(verticesB, k0 * dPhi + pSPhi, sz + j2*dz, R + offs, stwist + j2*dtwist)
                    appendVertex(verticesB, k0 * dPhi + pSPhi, sz + j0*dz, R + offs, stwist + j0*dtwist)

                    polygons.append(_Polygon(_dc(verticesA)))
                    polygons.append(_Polygon(_dc(verticesB)))

        # Mesh the top and bottom end pieces
        for i0 in range(slices):
            i1 = i0 + 0.5
            i2 = i0 + 1
            vertices_t = []
            vertices_b = []

            appendVertex(vertices_t, i0 * dPhi + pSPhi, zlen/2., endinnerrad + offs, twistedangle/2.)
            appendVertex(vertices_t, i2 * dPhi + pSPhi, zlen/2., endinnerrad + offs, twistedangle/2.)
            appendVertex(vertices_t, i2 * dPhi + pSPhi, zlen/2., endouterrad + offs, twistedangle/2.)
            appendVertex(vertices_t, i0 * dPhi + pSPhi, zlen/2., endouterrad + offs, twistedangle/2.)
            polygons.append(_Polygon(_dc(vertices_t)))

            appendVertex(vertices_b, i2 * dPhi + pSPhi, -zlen/2., endinnerrad + offs, -twistedangle/2.)
            appendVertex(vertices_b, i0 * dPhi + pSPhi, -zlen/2., endinnerrad + offs, -twistedangle/2.)
            appendVertex(vertices_b, i0 * dPhi + pSPhi, -zlen/2., endouterrad + offs, -twistedangle/2.)
            appendVertex(vertices_b, i2 * dPhi + pSPhi, -zlen/2., endouterrad + offs, -twistedangle/2.)
            polygons.append(_Polygon(_dc(vertices_b)))

        # Mesh the segment endpieces (if not 2pi angle)
        if phi != 2*_np.pi:
            for i0 in range(stacks):
                i1 = i0 + 0.5
                i2 = i0 + 1

                vertices_A1 = []
                vertices_A2 = []
                appendVertex(vertices_A1, pSPhi, sz + i0*dz, endinnerrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_A1, pSPhi, sz + i0*dz, endouterrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_A1, pSPhi, sz + i2*dz, endinnerrad + offs, stwist + i2*dtwist)

                appendVertex(vertices_A2, pSPhi, sz + i2*dz, endinnerrad + offs, stwist + i2*dtwist)
                appendVertex(vertices_A2, pSPhi, sz + i0*dz, endouterrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_A2, pSPhi, sz + i2*dz, endouterrad + offs, stwist + i2*dtwist)

                polygons.append(_Polygon(_dc(vertices_A1)))
                polygons.append(_Polygon(_dc(vertices_A2)))

                vertices_B1 = []
                vertices_B2 = []
                appendVertex(vertices_B1, pSPhi + slices*dPhi, sz + i0*dz, endouterrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_B1, pSPhi + slices*dPhi, sz + i0*dz, endinnerrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_B1, pSPhi + slices*dPhi, sz + i2*dz, endinnerrad + offs, stwist + i2*dtwist)

                appendVertex(vertices_B2, pSPhi + slices*dPhi, sz + i0*dz, endouterrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_B2, pSPhi + slices*dPhi, sz + i2*dz, endinnerrad + offs, stwist + i2*dtwist)
                appendVertex(vertices_B2, pSPhi + slices*dPhi, sz + i2*dz, endouterrad + offs, stwist + i2*dtwist)

                polygons.append(_Polygon(_dc(vertices_B1)))
                polygons.append(_Polygon(_dc(vertices_B2)))

        mesh     = _CSG.fromPolygons(polygons)
        return mesh
