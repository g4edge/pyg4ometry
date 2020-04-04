import operator
import cgal
import numpy

class CSG(object) :

    def __init__(self):
        self.polygons = []
        self.verts    = []
        self.polys    = []
        self.count    = []

    @classmethod
    def fromPolygons(self,polygons):
        c = CSG()
        c.polygons = polygons
        c.verts, c.polys, c.count = c.toVerticesAndPolygons()

        c.verts     = numpy.array(c.verts)
        c.npolyvert = []
        for p in c.polys :
            c.npolyvert.append(len(p))
        c.npolyvert = numpy.array(c.npolyvert)
        c.polys     = numpy.array(c.polys)

        vertspp = (c.verts.__array_interface__['data'][0] + numpy.arange(c.verts.shape[0]) * c.verts.strides[0]).astype(numpy.uintp)
        polyspp = (c.polys.__array_interface__['data'][0] + numpy.arange(c.polys.shape[0]) * c.polys.strides[0]).astype(numpy.uintp)

        c.polyhedron = cgal.vertexfacet_polyhedron(len(c.verts),
                                                   len(c.polys),
                                                   vertspp,
                                                   c.npolyvert,
                                                   polyspp)
        return c

    def toPolygons(self):
        return self.polygons

    def polygonCount(self):
        return len(self.polygons)

    def toVerticesAndPolygons(self):
        """
        Return list of vertices, polygons (cells), and the total
        number of vertex indices in the polygon connectivity list
        (count).
        """
        offset = 1.234567890 #gives unique key
        verts = []
        polys = []
        vertexIndexMap = {}
        count = 0
        for poly in self.polygons:
            verts = poly.vertices
            cell = []
            for v in poly.vertices:
                p = v.pos
                # use string key to remove degeneracy associated
                # very close points. The format %.10e ensures that
                # points differing in the 11 digits and higher are
                # treated as the same. For instance 1.2e-10 and
                # 1.3e-10 are essentially the same.
                vKey = '%.10e,%.10e,%.10e' % (p[0] + offset,
                                              p[1] + offset,
                                              p[2] + offset)
                if not vKey in vertexIndexMap:
                    vertexIndexMap[vKey] = len(vertexIndexMap)
                index = vertexIndexMap[vKey]
                cell.append(index)
                count += 1
            polys.append(cell)
        # sort by index
        sortedVertexIndex = sorted(vertexIndexMap.items(),
                                   key=operator.itemgetter(1))
        verts = []
        for v, i in sortedVertexIndex:
            p = []
            for c in v.split(','):
                p.append(float(c) - offset)
            verts.append(tuple(p))
        return verts, polys, count

    def union(self,csg):
        pass

    def subtract(self,csg):
        pass

    def intersect(self,csg):
        pass

