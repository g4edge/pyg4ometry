from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from Plane import Plane as _Plane
from ..Registry import registry as _registry
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

from copy import deepcopy as _dc
import logging as _log

import numpy as _np

class Hype(_SolidBase):
    def __init__(self, name, innerRadius, outerRadius, innerStereo,
                 outerStereo, halfLenZ, registry = None, nslice=16, nstack=16):
        """
        Constructs a tube with hyperbolic profile.

        Inputs:
          name:        string, name of the volume
          innerRadius: float, inner radius
          outerRadius: float, outer radius
          innerStereo: float, inner stereo angle
          outerStereo: float, outer stereo angle
          halfLenZ:    float, half length along z
        """
        self.type        = 'Hype'
        self.name        = name
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.innerStereo = innerStereo
        self.outerStereo = outerStereo
        self.halfLenZ    = halfLenZ
        self.nslice      = nslice
        self.nstack      = nstack

        self.dependents = []
        # self.checkParameters()
        if registry:
            registry.addSolid(self)

    def __repr__(self):
        return "Hype : {} {} {} {} {} {}".format(self.name, self.innerRadius, self.outerRadius,
                                                 self.innerStereo, self.outerStereo, self.halfLenZ)

    def checkParameters(self):
        if float(self.innerRadius) > float(self.outerRadius):
            raise ValueError("Inner radius must be less than outer radius.")

    def pycsgmesh(self):
        _log.info('hype.pycsgmesh> antlr')
        innerRadius = float(self.innerRadius)
        outerRadius = float(self.outerRadius)
        innerStereo = float(self.innerStereo)
        outerStereo = float(self.outerStereo)
        halfLenZ = float(self.halfLenZ)

        _log.info('hype.pycsgmesh> mesh')

        safety = 1.e-6
        dz     = 2*(halfLenZ+safety)/self.nstack #make a little bigger as safety for subtractions
        sz     = -halfLenZ-safety
        dTheta = 2*_np.pi/self.nslice
        stacks = self.nstack
        slices = self.nslice
        rinout  = [innerRadius, outerRadius] if innerRadius else [outerRadius]
        stinout = [innerStereo, outerStereo] if innerRadius else [outerStereo]

        polygons = []

        def appendVertex(vertices, theta, z, r, stereo):
            c     = _Vector([0,0,0])
            x     = _np.sqrt(r**2+(_np.tan(stereo)*z)**2)
            y     = 0
            x_rot = _np.cos(theta)*x - _np.sin(theta)*y
            y_rot = _np.sin(theta)*x + _np.cos(theta)*y

            d = _Vector(
                x_rot,
                y_rot,
                z)

            vertices.append(_Vertex(c.plus(d), None))

        meshinout = []
        for i in range(len(rinout)):
            for j0 in range(stacks):
                j1 = j0 + 0.5
                j2 = j0 + 1
                for i0 in range(slices):

                    i1 = i0 + 0.5
                    i2 = i0 + 1

                    verticesN = []
                    appendVertex(verticesN, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesN, i2 * dTheta, j2 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesN, i0 * dTheta, j2 * dz + sz, rinout[i], stinout[i])
                    polygons.append(_Polygon(_dc(verticesN)))
                    verticesW = []
                    appendVertex(verticesW, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesW, i0 * dTheta, j2 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesW, i0 * dTheta, j0 * dz + sz, rinout[i], stinout[i])
                    polygons.append(_Polygon(_dc(verticesW)))
                    verticesS = []
                    appendVertex(verticesS, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesS, i0 * dTheta, j0 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesS, i2 * dTheta, j0 * dz + sz, rinout[i], stinout[i])
                    polygons.append(_Polygon(_dc(verticesS)))
                    verticesE = []
                    appendVertex(verticesE, i1 * dTheta, j1 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesE, i2 * dTheta, j0 * dz + sz, rinout[i], stinout[i])
                    appendVertex(verticesE, i2 * dTheta, j2 * dz + sz, rinout[i], stinout[i])
                    polygons.append(_Polygon(_dc(verticesE)))

            for i0 in range(slices):
                i1 = i0 + 0.5
                i2 = i0 + 1
                vertices_t = []
                vertices_b = []

                # top face
                vertices_t.append(_Vertex(_Vector([0,0, stacks * dz + sz]), None))
                appendVertex(vertices_t, i0 * dTheta, stacks * dz + sz, rinout[i], stinout[i])
                appendVertex(vertices_t, i2 * dTheta, stacks * dz + sz, rinout[i], stinout[i])
                polygons.append(_Polygon(_dc(vertices_t)))

                # bottom face
                vertices_b.append(_Vertex(_Vector([0,0, -halfLenZ]), None))
                appendVertex(vertices_b, i2 * dTheta, sz, rinout[i], stinout[i])
                appendVertex(vertices_b, i0 * dTheta, sz, rinout[i], stinout[i])
                polygons.append(_Polygon(_dc(vertices_b)))

            mesh      = _CSG.fromPolygons(polygons)
            meshinout.append(mesh)
            polygons = []

        for i in range(len(meshinout)):
            wzlength     = 3*halfLenZ
            topNorm      = _Vector(0,0,1)
            botNorm      = _Vector(0,0,-1)
            pTopCut      = _Plane("pTopCut", topNorm, halfLenZ, wzlength).pycsgmesh()
            pBottomCut   = _Plane("pBottomCut", botNorm, -halfLenZ, wzlength).pycsgmesh()
            meshinout[i] = meshinout[i].subtract(pBottomCut).subtract(pTopCut)

        if innerRadius:
            mesh = meshinout[1].subtract(meshinout[0])
        else:
            mesh = meshinout[0]

        return mesh
