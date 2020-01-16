from SolidBase import SolidBase as _SolidBase
from Wedge import Wedge as _Wedge
from Plane import Plane as _Plane
from ...pycsg.core import CSG as _CSG
from ...pycsg.geom import Vector as _Vector
from ...pycsg.geom import Vertex as _Vertex
from ...pycsg.geom import Polygon as _Polygon

from copy import deepcopy as _dc
import logging as _log

import numpy as _np

class Hype(_SolidBase):
    """
    Constructs a tube with hyperbolic profile.
    
    :param name:        of solid
    :type name:         str
    :param innerRadius: inner radius
    :type innerRadius:  float, Constant, Quantity, Variable, Expression
    :param outerRadius: outer radius
    :type outerRadius:  float, Constant, Quantity, Variable, Expression
    :param innerStereo: inner stereo angle
    :type innerStereo:  float, Constant, Quantity, Variable, Expression
    :param outerStereo: outer stereo angle
    :type outerStereo:  float, Constant, Quantity, Variable, Expression
    :param lenZ:        length along z
    :param registry:    for storing solid
    :type registry:     Registry
    :param lunit:       length unit (nm,um,mm,m,km) for solid
    :type lunit:        str
    :param aunit:       angle unit (rad,deg) for solid
    :type aunit:        str    
    :param nslice:      number of phi elements for meshing
    :type nslice:       int  
    :param nstack:      number of theta elements for meshing
    :type nstack:       int             
    """


    def __init__(self, name, innerRadius, outerRadius, innerStereo,
                 outerStereo, lenZ, registry, lunit="mm",
                 aunit="rad",nslice=16, nstack=16, addRegistry=True):
        self.type        = 'Hype'
        self.name        = name
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.innerStereo = innerStereo
        self.outerStereo = outerStereo
        self.lenZ        = lenZ
        self.lunit       = lunit
        self.aunit       = aunit
        self.nslice      = nslice
        self.nstack      = nstack

        self.dependents = []

        self.varNames = ["innerRadius", "outerRadius", "innerStereo","outerStereo","lenZ"]

        if addRegistry:
            registry.addSolid(self)

        self.registry = registry

        self.checkParameters()

    def __repr__(self):
        return "Hype : {} {} {} {} {} {}".format(self.name, self.innerRadius, self.outerRadius,
                                                 self.innerStereo, self.outerStereo, self.lenZ)

    def checkParameters(self):
        if float(self.innerRadius) > float(self.outerRadius):
            raise ValueError("Inner radius must be less than outer radius.")

    '''
    def pycsgmeshOld(self):
        _log.info('hype.pycsgmesh> antlr')


        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        innerRadius = self.evaluateParameter(self.innerRadius)*luval
        outerRadius = self.evaluateParameter(self.outerRadius)*luval
        innerStereo = self.evaluateParameter(self.innerStereo)*auval
        outerStereo = self.evaluateParameter(self.outerStereo)*auval
        halfLenZ    = self.evaluateParameter(self.lenZ)/2.0*luval

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

    '''
    def pycsgmesh(self):
        _log.info('hype.pycsgmesh> antlr')


        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        innerRadius = self.evaluateParameter(self.innerRadius)*luval
        outerRadius = self.evaluateParameter(self.outerRadius)*luval
        innerStereo = self.evaluateParameter(self.innerStereo)*auval
        outerStereo = self.evaluateParameter(self.outerStereo)*auval
        LenZ = self.evaluateParameter(self.lenZ)
        halfLenZ    = self.evaluateParameter(self.lenZ)/2.0*luval

        _log.info('hype.pycsgmesh> mesh')

        dz     = LenZ/self.nstack
        sz     = -halfLenZ
        dTheta = 2*_np.pi/self.nslice
        stacks = self.nstack
        slices = self.nslice

        polygons = []


        for j0 in range(slices):

            j1 = j0
            j2 = j0 + 1

            for i0 in range(stacks):

                i1 = i0
                i2 = i0 + 1

                z1_outer = i1 * dz + sz
                r1_outer = _np.sqrt(outerRadius**2 + (z1_outer*_np.tan(outerStereo)) ** 2)
                x1_rot_outer = _np.cos(dTheta * j1) * r1_outer
                y1_rot_outer = _np.sin(dTheta * j1) * r1_outer

                z2_outer = i2 * dz + sz
                r2_outer = _np.sqrt(outerRadius**2 + (z2_outer*_np.tan(outerStereo)) ** 2)
                x2_rot_outer = _np.cos(dTheta * j1) * r2_outer
                y2_rot_outer = _np.sin(dTheta * j1) * r2_outer

                z3_outer = i2 * dz + sz
                r3_outer = _np.sqrt(outerRadius**2 + (z3_outer*_np.tan(outerStereo)) ** 2)
                x3_rot_outer = _np.cos(dTheta * j2) * r3_outer
                y3_rot_outer = _np.sin(dTheta * j2) * r3_outer

                z4_outer = i1 * dz + sz
                r4_outer = _np.sqrt(outerRadius**2 + (z4_outer*_np.tan(outerStereo)) ** 2)
                x4_rot_outer = _np.cos(dTheta * j2) * r4_outer
                y4_rot_outer = _np.sin(dTheta * j2) * r4_outer


                vertices_outer = []

                vertices_outer.append(_Vertex([x1_rot_outer, y1_rot_outer, z1_outer], None))
                vertices_outer.append(_Vertex([x2_rot_outer, y2_rot_outer, z2_outer], None))
                vertices_outer.append(_Vertex([x3_rot_outer, y3_rot_outer, z3_outer], None))
                vertices_outer.append(_Vertex([x4_rot_outer, y4_rot_outer, z4_outer], None))

                polygons.append(_Polygon(vertices_outer))

                if innerRadius != 0:

                    z1_inner = i1 * dz + sz
                    r1_inner = _np.sqrt(innerRadius**2 + (z1_inner*_np.tan(innerStereo)) ** 2)
                    x1_rot_inner = _np.cos(dTheta * j1) * r1_inner
                    y1_rot_inner = _np.sin(dTheta * j1) * r1_inner

                    z2_inner = i2 * dz + sz
                    r2_inner = _np.sqrt(innerRadius**2 + (z2_inner*_np.tan(innerStereo)) ** 2)
                    x2_rot_inner = _np.cos(dTheta * j1) * r2_inner
                    y2_rot_inner = _np.sin(dTheta * j1) * r2_inner

                    z3_inner = i2 * dz + sz
                    r3_inner = _np.sqrt(innerRadius**2 + (z3_inner*_np.tan(innerStereo)) ** 2)
                    x3_rot_inner = _np.cos(dTheta * j2) * r3_inner
                    y3_rot_inner = _np.sin(dTheta * j2) * r3_inner

                    z4_inner = i1 * dz + sz
                    r4_inner = _np.sqrt(innerRadius**2 + (z4_inner*_np.tan(innerStereo)) ** 2)
                    x4_rot_inner = _np.cos(dTheta * j2) * r4_inner
                    y4_rot_inner = _np.sin(dTheta * j2) * r4_inner

                    vertices_inner = []

                    vertices_inner.append(_Vertex([x1_rot_inner, y1_rot_inner, z1_inner], None))
                    vertices_inner.append(_Vertex([x2_rot_inner, y2_rot_inner, z2_inner], None))
                    vertices_inner.append(_Vertex([x3_rot_inner, y3_rot_inner, z3_inner], None))
                    vertices_inner.append(_Vertex([x4_rot_inner, y4_rot_inner, z4_inner], None))

                    polygons.append(_Polygon(vertices_inner))

                    if i1 == 0:

                        verticesTop = []

                        verticesTop.append(_Vertex([x1_rot_inner, y1_rot_inner, z1_inner], None))
                        verticesTop.append(_Vertex([x1_rot_outer, y1_rot_outer, z1_outer], None))
                        verticesTop.append(_Vertex([x4_rot_outer, y4_rot_outer, z4_outer], None))
                        verticesTop.append(_Vertex([x4_rot_inner, y4_rot_inner, z4_inner], None))

                        polygons.append(_Polygon(verticesTop))

                    if i2 == stacks:

                        verticesBottom = []

                        verticesBottom.append(_Vertex([x3_rot_inner, y3_rot_inner, z3_inner], None))
                        verticesBottom.append(_Vertex([x3_rot_outer, y3_rot_outer, z3_outer], None))
                        verticesBottom.append(_Vertex([x2_rot_outer, y2_rot_outer, z2_outer], None))
                        verticesBottom.append(_Vertex([x2_rot_inner, y2_rot_inner, z2_inner], None))

                        polygons.append(_Polygon(verticesBottom))

                if innerRadius == 0:

                    if i1 == 0:

                        verticesTop = []

                        verticesTop.append(_Vertex([x4_rot_outer, y4_rot_outer, z4_outer], None))
                        verticesTop.append(_Vertex([0, 0, -halfLenZ], None))
                        verticesTop.append(_Vertex([x1_rot_outer, y1_rot_outer, z1_outer], None))

                        polygons.append(_Polygon(verticesTop))

                    if i2 == stacks:

                        verticesBottom = []

                        verticesBottom.append(_Vertex([x2_rot_outer, y2_rot_outer, z2_outer], None))
                        verticesBottom.append(_Vertex([0, 0, halfLenZ], None))
                        verticesBottom.append(_Vertex([x3_rot_outer, y3_rot_outer, z3_outer], None))

                        polygons.append(_Polygon(verticesBottom))

        mesh = _CSG.fromPolygons(polygons)
        return mesh