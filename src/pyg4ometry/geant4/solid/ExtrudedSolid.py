from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.core import PolygonProcessing as _PolygonProcessing
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

import pyg4ometry.pycgal as _pycgal

import numpy as _np

import logging as _log

class ExtrudedSolid(_SolidBase):
    """
    Construct an extruded solid

    :param name: of solid
    :type name: str
    :param pPolygon: x-y coordinates of vertices for the polygon.
    :type pPolygon: list of lists
    :param pZslices: z-coordinates of a slice, slice offsets in x-y and scaling
    :type pZslices: list of lists
    :param registry:       for storing solid
    :type registry:        Registry
    :param lunit:          length unit (nm,um,mm,m,km) for solid
    :type lunit:           str
    
    Example: Triangular prism with 2 slices
    pPoligon = [[x1,y1],[x2,y2],[x3,y3]] - vertices of polygon in clockwise order
    zSlices  = [[z1,[offsx1, offsy1],scale1],[z2,[offsx2, offsy2],scale2]]
    """
    def __init__(self, name, pPolygon, pZslices, registry, lunit="mm", addRegistry=True):
        super(ExtrudedSolid, self).__init__(name, 'ExtrudedSolid', registry)

        self.lunit = lunit

        self.dependents = []

        self.varNames = ["pPolygon", "pZslices"]
        self.varUnits = ["lunit", "lunit"]

        for varName in self.varNames:
            self._addProperty(varName)
            setattr(self, varName, locals()[varName])

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Extruded solid: {}".format(self.name)

    def polygon_area(self,vertices):
        # Using the shoelace formula
        xy = _np.array(vertices).T
        x = xy[0]
        y = xy[1]
        signed_area = 0.5*(_np.dot(x,_np.roll(y,1))-_np.dot(y,_np.roll(x,1)))
        return signed_area

    def evaluateParameterWithUnits(self, varName):
        import pyg4ometry.gdml.Units as _Units
        luval = _Units.unit(self.lunit)

        if varName == 'pPolygon' :
            pPolygons = self.evaluateParameter(self.pPolygon)
            vertices  = [[pPolygon[0]*luval, pPolygon[1]*luval] for pPolygon in pPolygons]
            return vertices
        elif varName == 'pZslices' :
            pZslices = self.evaluateParameter(self.pZslices)
            slices = [ [zslice[0]*luval, [zslice[1][0]*luval, zslice[1][1]*luval], zslice[2]] for zslice in pZslices ]
            return slices
        else :
            raise RuntimeError(f'ExtrudedSolid.evaluateParameterWithUnits : unknown variable: {varName}')

    def mesh(self):
        _log.info('xtru.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import

        luval = _Units.unit(self.lunit)

        pZslices = self.evaluateParameter(self.pZslices)
        pPolygon = self.evaluateParameter(self.pPolygon)

        zpos     = [zslice[0]*luval for zslice in pZslices]
        x_offs   = [zslice[1][0]*luval for zslice in pZslices]
        y_offs   = [zslice[1][1]*luval for zslice in pZslices]
        scale    = [zslice[2] for zslice in pZslices]
        vertices = [[pPolygon[0]*luval, pPolygon[1]*luval] for pPolygon in pPolygon]
        nslices  = len(pZslices)

        _log.info('xtru.pycsgmesh> mesh')
        polygons  = []
        polygonsT = []
        polygonsB = []

        if self.polygon_area(vertices) < 0:
            vertices = list(reversed(vertices))


        topPolyList = [[scale[-1]*vert[0]+x_offs[-1],
                        scale[-1]*vert[1]+y_offs[-1]] for vert in list(reversed(vertices))]


        topPolyListConvex = _PolygonProcessing.decomposePolygon2d(topPolyList)

        for topPoly in topPolyListConvex :
            topPolyPolygon = _Polygon([_Vertex(_Vector(vert[0],vert[1],zpos[-1])) for vert in topPoly])
            polygonsT.append(topPolyPolygon)


        bottomPolyList = [[scale[0]*vert[0]+x_offs[0],
                           scale[0]*vert[1]+y_offs[0]] for vert in list(reversed(vertices))]

        bottomPolyListConvex = _PolygonProcessing.decomposePolygon2d(bottomPolyList)

        for bottomPoly in bottomPolyListConvex :
            bottomPoly = list(bottomPoly) # TODO reversed here because of needing counterclockwise in 2D convex decomp in CGAL
            bottomPoly.reverse()

            bottomPolyPolygon = _Polygon([_Vertex(_Vector(vert[0],vert[1],zpos[0])) for vert in bottomPoly])
            polygonsB.append(bottomPolyPolygon)

        # It appears we must append the top and bottom faces and then tile the sides
        polygons.extend(polygonsT)
        polygons.extend(polygonsB)

        maxn = len(vertices)

        for l in range(0, nslices-1):
            l_curr = l
            l_next = l + 1

            for n in range(maxn):
                n_next = (n+1) % maxn

                vert = vertices[nslices - n]
                vert_next = vertices[nslices - n - 1]

                poly = _Polygon([_Vertex(_Vector(scale[l_curr]*vert[0]+x_offs[l_curr],
                                                 scale[l_curr]*vert[1]+y_offs[l_curr],
                                                 zpos[l_curr])),

                                 _Vertex(_Vector(scale[l_curr]*vert_next[0]+x_offs[l_curr],
                                                 scale[l_curr]*vert_next[1]+y_offs[l_curr],
                                                 zpos[l_curr])),

                                 _Vertex(_Vector(scale[l_next]*vert_next[0]+x_offs[l_next],
                                                 scale[l_next]*vert_next[1]+y_offs[l_next],
                                                 zpos[l_next])),

                                 _Vertex(_Vector(scale[l_next]*vert[0]+x_offs[l_next],
                                                 scale[l_next]*vert[1]+y_offs[l_next],
                                                 zpos[l_next]))])

                polygons.append(poly)


        mesh = _CSG.fromPolygons(polygons)

        return mesh
