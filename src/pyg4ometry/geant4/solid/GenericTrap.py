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

class GenericTrap(_SolidBase):
    """
    Constructs an arbitrary trapezoid using two quadrilaterals sitting
    on two parallel planes. Vertices 1-4 define the quadrilateral at -dz and
    vertices 5-8 define the quadrilateral at +dz. This solid is called Arb8
    in GDML notation.
    
    :param name:     string, name of the volume
    :param v1x:      vertex 1 x position
    :param v1y:      vertex 1 y position
    :param v2x:      vertex 2 x position
    :param v2y:      vertex 2 y position
    :param v3x:      vertex 3 x position
    :param v3y:      vertex 3 y position
    :param v4x:      vertex 4 x position
    :param v4y:      vertex 4 y position
    :param v5x:      vertex 5 x position
    :param v5y:      vertex 5 y position
    :param v6x:      vertex 6 x position
    :param v6y:      vertex 6 y position
    :param v7x:      vertex 7 x position
    :param v7y:      vertex 7 y position
    :param v8x:      vertex 8 x position
    :param v8y:      vertex 8 y position
    :param dz:       half length along z
    :param registry: for storing solid
    :type registry:  Registry
    """
    def __init__(self, name, v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y,
                 v5x, v5y, v6x, v6y, v7x, v7y, v8x, v8y, dz,
                 registry, nstack=20, lunit="mm", addRegistry=True):
        super(GenericTrap, self).__init__(name, 'GenericTrap', registry)

        self.dz = dz
        self.lunit = lunit
        self.nstack = nstack

        vars_in = locals()
        for i in range(1, 9):
            setattr(self, "v{}x".format(i), vars_in["v{}x".format(i)])
            setattr(self, "v{}y".format(i), vars_in["v{}y".format(i)])

        self.dependents = []

        self.varNames = ["v1x", "v1y", "v2x", "v2y", "v3x", "v3y", "v4x", "v4y",
                         "v5x", "v5y", "v6x", "v6y", "v7x", "v7y", "v8x", "v8y", "dz"]
        self.varUnits = ["lunit" for _ in self.varNames]

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Generic Trapezoid : {}".format(self.name)

    def polygon_area(self,vertices):
        # Using the shoelace formula
        xy = _np.array(vertices).T
        x = xy[0]
        y = xy[1]
        signed_area = 0.5*(_np.dot(x,_np.roll(y,1))-_np.dot(y,_np.roll(x,1)))
        if not signed_area:
            return 0
            print("vertices: ",vertices)
            raise ValueError("GenericTrap: '{}' Zero area quadrilateral not allowed.".format(self.name))        # TODO TODO
        return signed_area

    def get_vertex(self, index):
        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        uval = _Units.unit(self.lunit)

        sign_z = -1 if index <= 4 else 1
        vertex = (self.evaluateParameter(getattr(self, "v{}x".format(index))*uval),
                  self.evaluateParameter(getattr(self, "v{}y".format(index))*uval),
                  sign_z*float(self.dz)*uval)
        return vertex

    def makeLayers(self, verts_bot, verts_top):

        import pyg4ometry.gdml.Units as _Units #TODO move circular import
        uval = _Units.unit(self.lunit)

        layers = []

        z1 = 2*float(self.dz)*uval
        z0 = -float(self.dz)*uval

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

                verts_i.append(_Vertex(_Vector(x, y, z)))

            layers.append(verts_i)

        return layers



    def mesh(self):
        _log.info('arb8.mesh> antlr')

        verts_top = []
        verts_bot = []
        for i in range(1,9):
            vert = self.get_vertex(i)
            if i <=4:
                verts_bot.append(vert)
            else:
                verts_top.append(vert)

        # Correct ordering ensures correct surface normals
        if self.polygon_area(verts_top) > 0:
            verts_top = list(reversed(verts_top))

        if self.polygon_area(verts_bot) > 0:
            verts_bot = list(reversed(verts_bot))

        all_verts = self.makeLayers(verts_bot, verts_top)

        _log.info('arb8.mesh> mesh')
        polygons = []

        # Mesh top and bottom pieces
        polygons.append(_Polygon([all_verts[0][3], all_verts[0][2],
                                  all_verts[0][1], all_verts[0][0]])) # Bot

        polygons.append(_Polygon([all_verts[-1][0], all_verts[-1][1],
                                  all_verts[-1][2], all_verts[-1][3]])) # Top

        # Mesh the sides
        for i0 in range(len(all_verts)-1):
            i1 = i0 + 1
            vts_l = all_verts[i0]
            vts_u = all_verts[i1]

            for k0 in range(4): # 4 vertexes
                k1 = (k0+1) % 4
                polygons.append(_Polygon([vts_l[k0], vts_l[k1], vts_u[k1], vts_u[k0]]))

        mesh  = _CSG.fromPolygons(polygons)
        return mesh
