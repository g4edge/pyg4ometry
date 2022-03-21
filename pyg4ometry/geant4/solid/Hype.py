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
                 outerStereo, lenZ, registry, lunit="mm", aunit="rad",
                 nslice=None, nstack=None, addRegistry=True):
        super(Hype, self).__init__(name, 'Hype', registry)

        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.innerStereo = innerStereo
        self.outerStereo = outerStereo
        self.lenZ        = lenZ
        self.lunit       = lunit
        self.aunit       = aunit
        self.nslice      = nslice if nslice else _config.SolidDefaults.Hype.nslice
        self.nstack      = nstack if nstack else _config.SolidDefaults.Hype.nstack

        self.dependents = []

        self.varNames = ["innerRadius", "outerRadius", "innerStereo", "outerStereo", "lenZ"]
        self.varUnits = ["lunit", "lunit", "aunit", "aunit", "lunit"]

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Hype : {} {} {} {} {} {}".format(self.name, self.innerRadius, self.outerRadius,
                                                 self.innerStereo, self.outerStereo, self.lenZ)

    def checkParameters(self):
        if float(self.innerRadius) > float(self.outerRadius):
            raise ValueError("Inner radius must be less than outer radius.")

    def mesh(self):
        _log.info('hype.pycsgmesh> antlr')


        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        innerRadius = self.evaluateParameter(self.innerRadius)*luval
        outerRadius = self.evaluateParameter(self.outerRadius)*luval
        innerStereo = self.evaluateParameter(self.innerStereo)*auval
        outerStereo = self.evaluateParameter(self.outerStereo)*auval
        LenZ = self.evaluateParameter(self.lenZ)*luval
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

                vertices_outer.append(_Vertex([x1_rot_outer, y1_rot_outer, z1_outer]))
                vertices_outer.append(_Vertex([x2_rot_outer, y2_rot_outer, z2_outer]))
                vertices_outer.append(_Vertex([x3_rot_outer, y3_rot_outer, z3_outer]))
                vertices_outer.append(_Vertex([x4_rot_outer, y4_rot_outer, z4_outer]))

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

                    vertices_inner.append(_Vertex([x1_rot_inner, y1_rot_inner, z1_inner]))
                    vertices_inner.append(_Vertex([x2_rot_inner, y2_rot_inner, z2_inner]))
                    vertices_inner.append(_Vertex([x3_rot_inner, y3_rot_inner, z3_inner]))
                    vertices_inner.append(_Vertex([x4_rot_inner, y4_rot_inner, z4_inner]))
                    vertices_inner.reverse()
                    polygons.append(_Polygon(vertices_inner))

                    if i1 == 0:

                        verticesTop = []

                        verticesTop.append(_Vertex([x1_rot_inner, y1_rot_inner, z1_inner]))
                        verticesTop.append(_Vertex([x1_rot_outer, y1_rot_outer, z1_outer]))
                        verticesTop.append(_Vertex([x4_rot_outer, y4_rot_outer, z4_outer]))
                        verticesTop.append(_Vertex([x4_rot_inner, y4_rot_inner, z4_inner]))

                        polygons.append(_Polygon(verticesTop))

                    if i2 == stacks:

                        verticesBottom = []

                        verticesBottom.append(_Vertex([x3_rot_inner, y3_rot_inner, z3_inner]))
                        verticesBottom.append(_Vertex([x3_rot_outer, y3_rot_outer, z3_outer]))
                        verticesBottom.append(_Vertex([x2_rot_outer, y2_rot_outer, z2_outer]))
                        verticesBottom.append(_Vertex([x2_rot_inner, y2_rot_inner, z2_inner]))

                        polygons.append(_Polygon(verticesBottom))

                if innerRadius == 0:

                    if i1 == 0:

                        verticesTop = []

                        verticesTop.append(_Vertex([x4_rot_outer, y4_rot_outer, z4_outer]))
                        verticesTop.append(_Vertex([0, 0, -halfLenZ]))
                        verticesTop.append(_Vertex([x1_rot_outer, y1_rot_outer, z1_outer]))

                        polygons.append(_Polygon(verticesTop))

                    if i2 == stacks:

                        verticesBottom = []

                        verticesBottom.append(_Vertex([x2_rot_outer, y2_rot_outer, z2_outer]))
                        verticesBottom.append(_Vertex([0, 0, halfLenZ]))
                        verticesBottom.append(_Vertex([x3_rot_outer, y3_rot_outer, z3_outer]))

                        polygons.append(_Polygon(verticesBottom))

        mesh = _CSG.fromPolygons(polygons)
        return mesh
