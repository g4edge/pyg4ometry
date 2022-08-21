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

class TwistedTubs(_SolidBase):
    """
    Creates a twisted tube segement. Note that only 1 constructor is supprted.
    
    :param name:         of solid
    :type name:          str
    :param endinnerrad:  inner radius at the end of the segment
    :type endinnerrad:   float, Constant, Quantity, Variable, Expression
    :param endinnerrad:  outer radius at the end of the segment
    :type endinnerrad:   float, Constant, Quantity, Variable, Expression
    :param zlen:         length of the tube segement
    :type zlen:          float, Constant, Quantity, Variable, Expression
    :param twistedangle: twist angle
    :type twistedangle:  float, Constant, Quantity, Variable, Expression
    :param registry:     for storing solid
    :type registry:      Registry
    :param lunit:        length unit (nm,um,mm,m,km) for solid
    :type lunit:         str
    :param aunit:        angle unit (rad,deg) for solid
    :type aunit:         str    
    :param nslice:       number of phi elements for meshing
    :type nstack:        int    
    :param nstack:       number of theta elements for meshing
    :type nstack:        int    

    """
    def __init__(self, name, endinnerrad, endouterrad, zlen, phi, twistedangle,
                 registry, lunit="mm", aunit="rad",
                 nslice=None, nstack=None, addRegistry=True):
        super(TwistedTubs, self).__init__(name, 'TwistedTubs', registry)

        self.endinnerrad  = endinnerrad
        self.endouterrad  = endouterrad
        self.zlen         = zlen
        self.phi          = phi
        self.twistedangle = twistedangle
        self.lunit        = lunit
        self.aunit        = aunit
        self.nslice       = nslice if nslice else _config.SolidDefaults.TwistedTubs.nslice
        self.nstack       = nstack if nstack else _config.SolidDefaults.TwistedTubs.nstack

        self.dependents = []

        self.varNames = ["endinnerrad", "endouterrad", "zlen", "phi", "twistedangle"]
        self.varUnits = ["lunit", "lunit", "lunit", "aunit", "aunit"]

        if addRegistry:
            registry.addSolid(self)
        # self.checkParameters()

    def __repr__(self):
        return "TwistedTubs : {} {} {} {} {} {} {}".format(self.name,
                                                     self.endinnerrad, self.endouterrad,
                                                     self.zlen, self.twistedangle,
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


    def mesh(self):
        _log.info("polycone.antlr>")
        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        endinnerrad = self.evaluateParameter(self.endinnerrad)*luval
        endouterrad = self.evaluateParameter(self.endouterrad)*luval

        zlen         = self.evaluateParameter(self.zlen)*luval
        phi          = self.evaluateParameter(self.phi)*auval 
        twistedangle = self.evaluateParameter(self.twistedangle)*auval

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

            vertices.append(_Vertex(c+_Vector(xr,yr,z)))

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

                    polygons.append(_Polygon(verticesA))
                    polygons.append(_Polygon(verticesB))

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
            polygons.append(_Polygon(vertices_t))

            appendVertex(vertices_b, i2 * dPhi + pSPhi, -zlen/2., endinnerrad + offs, -twistedangle/2.)
            appendVertex(vertices_b, i0 * dPhi + pSPhi, -zlen/2., endinnerrad + offs, -twistedangle/2.)
            appendVertex(vertices_b, i0 * dPhi + pSPhi, -zlen/2., endouterrad + offs, -twistedangle/2.)
            appendVertex(vertices_b, i2 * dPhi + pSPhi, -zlen/2., endouterrad + offs, -twistedangle/2.)
            polygons.append(_Polygon(vertices_b))

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

                polygons.append(_Polygon(vertices_A1))
                polygons.append(_Polygon(vertices_A2))

                vertices_B1 = []
                vertices_B2 = []
                appendVertex(vertices_B1, pSPhi + slices*dPhi, sz + i0*dz, endouterrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_B1, pSPhi + slices*dPhi, sz + i0*dz, endinnerrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_B1, pSPhi + slices*dPhi, sz + i2*dz, endinnerrad + offs, stwist + i2*dtwist)

                appendVertex(vertices_B2, pSPhi + slices*dPhi, sz + i0*dz, endouterrad + offs, stwist + i0*dtwist)
                appendVertex(vertices_B2, pSPhi + slices*dPhi, sz + i2*dz, endinnerrad + offs, stwist + i2*dtwist)
                appendVertex(vertices_B2, pSPhi + slices*dPhi, sz + i2*dz, endouterrad + offs, stwist + i2*dtwist)

                polygons.append(_Polygon(vertices_B1))
                polygons.append(_Polygon(vertices_B2))

        mesh     = _CSG.fromPolygons(polygons)
        return mesh
