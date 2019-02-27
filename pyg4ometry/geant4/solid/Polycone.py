from SolidBase             import SolidBase     as _SolidBase
from pyg4ometry.pycsg.core import CSG           as _CSG
from pyg4ometry.pycsg.geom import Vector        as _Vector
from pyg4ometry.pycsg.geom import Vertex        as _Vertex
from pyg4ometry.pycsg.geom import Polygon       as _Polygon
from pyg4ometry.geant4.Registry import registry as _registry
from Wedge                 import Wedge         as _Wedge

import logging as _log
import numpy as _np
from copy import deepcopy as _dc


class Polycone(_SolidBase):
    def __init__(self, name, pSPhi, pDPhi, pZpl, pRMin, pRMax,
                 registry=None, nslice=16):
        """
        Constructs a solid of rotation using an arbitrary 2D surface.

        Inputs:
          name:   string, name of the volume
          pSPhi:  float, starting rotation angle in radians
          pDPhi:  float, total rotation angle in radius
          pZPlns: list, z-positions of planes used
          pRInr : list, inner radii of surface at each z-plane
          pROut : list, outer radii of surface at each z-plane

          Optional registration as this solid is used as a temporary solid
          in Polyhedra and needn't be always registered.
        """
        self.type    = 'Polycone'
        self.name    = name
        self.pSPhi   = pSPhi
        self.pDPhi   = pDPhi
        self.pZpl    = pZpl
        self.pRMin   = pRMin
        self.pRMax   = pRMax
        self.nslice  = nslice

        self.dependents = []

        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return 'Polycone : '+self.name+' '+str(self.pSPhi)+' '+str(self.pDPhi)+' '+str(self.pZpl)+' '+str(self.pRMin)+' '+str(self.pRMax)

    def pycsgmesh(self):

        _log.info("polycone.pycsgmesh>")
        basicmesh = self.basicmesh()
        mesh = self.csgmesh(basicmesh)

        return mesh

    def basicmesh(self):
        _log.info("polycone.antlr>")
        pSPhi = float(self.pSPhi)
        pDPhi = float(self.pDPhi)

        pZpl = [float(val) for val in self.pZpl]
        pRMin = [float(val) for val in self.pRMin]
        pRMax = [float(val) for val in self.pRMax]

        _log.info("polycone.basicmesh>")
        polygons = []

        dPhi  = 2*_np.pi/self.nslice
        stacks  = len(pZpl)
        slices  = self.nslice

        def appendVertex(vertices, theta, z, r, norm=[]):
            c = _Vector([0,0,0])
            x = r*_np.cos(theta)
            y = r*_np.sin(theta)

            d = _Vector(x,y,z)

            if not norm:
                n = d
            else:
                n = _Vector(norm)
            vertices.append(_Vertex(c.plus(d), None))

        rinout    = [pRMin, pRMax]
        meshinout = []

        offs = 1.e-25 #Small offset to avoid point degenracy when the radius is zero. TODO: make more robust
        for R in rinout:
            for j0 in range(stacks-1):
                j1 = j0 + 0.5
                j2 = j0 + 1
                r0 = R[j0] + offs
                r2 = R[j2] + offs
                for i0 in range(slices):
                    i1 = i0 + 0.5
                    i2 = i0 + 1
                    k0 = i0 if R == pRMax else i2  #needed to ensure the surface normals on the inner and outer surface are obeyed
                    k1 = i2 if R == pRMax else i0
                    vertices = []
                    appendVertex(vertices, k0 * dPhi + pSPhi, pZpl[j0], r0)
                    appendVertex(vertices, k1 * dPhi + pSPhi, pZpl[j0], r0)
                    appendVertex(vertices, k1 * dPhi + pSPhi, pZpl[j2], r2)
                    appendVertex(vertices, k0 * dPhi + pSPhi, pZpl[j2], r2)

                    polygons.append(_Polygon(_dc(vertices)))

        for i0 in range(slices):
            i1 = i0 + 0.5
            i2 = i0 + 1
            vertices_t = []
            vertices_b = []

            if pRMin[-1] or pRMax[-1]:
                appendVertex(vertices_t, i2 * dPhi + pSPhi, pZpl[-1], pRMin[-1]+offs)
                appendVertex(vertices_t, i0 * dPhi + pSPhi, pZpl[-1], pRMin[-1]+offs)
                appendVertex(vertices_t, i0 * dPhi + pSPhi, pZpl[-1], pRMax[-1]+offs)
                appendVertex(vertices_t, i2 * dPhi + pSPhi, pZpl[-1], pRMax[-1]+offs)
                polygons.append(_Polygon(_dc(vertices_t)))

            if pRMin[0] or pRMax[0]:
                appendVertex(vertices_b, i0 * dPhi + pSPhi, pZpl[0], pRMin[0]+offs)
                appendVertex(vertices_b, i2 * dPhi + pSPhi, pZpl[0], pRMin[0]+offs)
                appendVertex(vertices_b, i2 * dPhi + pSPhi, pZpl[0], pRMax[0]+offs)
                appendVertex(vertices_b, i0 * dPhi + pSPhi, pZpl[0], pRMax[0]+offs)
                polygons.append(_Polygon(_dc(vertices_b)))

        basicmesh     = _CSG.fromPolygons(polygons)
        return basicmesh

    def csgmesh(self, basicmesh):
        _log.info("polycone.antlr>")
        pSPhi = float(self.pSPhi)
        pDPhi = float(self.pDPhi)
        pZpl = [float(val) for val in self.pZpl]
        pRMax = [float(val) for val in self.pRMax]

        _log.info("polycone.csgmesh>")
        wrmax    = 3*max([abs(r) for r in pRMax]) #ensure intersection wedge is much bigger than solid
        wzlength = 3*max([abs(z) for z in pZpl])

        if pDPhi != 2*_np.pi:
            pWedge = _Wedge("wedge_temp",wrmax, pSPhi, pDPhi+pSPhi, wzlength).pycsgmesh()
            mesh = basicmesh.intersect(pWedge)

        return mesh
