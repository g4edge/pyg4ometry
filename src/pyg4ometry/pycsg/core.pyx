# cython: language_level=3

import operator
from .geom import *
import numpy as _np
from hashlib import md5 as _md5
from functools import reduce

from .geom import Vertex as _Vertex
from .geom import Vector as _Vector

class CSG(object):
    """
    Constructive Solid Geometry (CSG) is a modeling technique that uses Boolean
    operations like union and intersection to combine 3D solids. This library
    implements CSG operations on meshes elegantly and concisely using BSP trees,
    and is meant to serve as an easily understandable implementation of the
    algorithm. All edge cases involving overlapping coplanar polygons in both
    solids are correctly handled.
    
    Example usage::
    
        from csg.core import CSG
        
        cube = CSG.cube();
        sphere = CSG.sphere({'radius': 1.3});
        polygons = cube.subtract(sphere).toPolygons();
    
    ## Implementation Details
    
    All CSG operations are implemented in terms of two functions, `clipTo()` and
    `invert()`, which remove parts of a BSP tree inside another BSP tree and swap
    solid and empty space, respectively. To find the union of `a` and `b`, we
    want to remove everything in `a` inside `b` and everything in `b` inside `a`,
    then combine polygons from `a` and `b` into one solid::
    
        a.clipTo(b);
        b.clipTo(a);
        a.build(b.allPolygons());
    
    The only tricky part is handling overlapping coplanar polygons in both trees.
    The code above keeps both copies, but we need to keep them in one tree and
    remove them in the other tree. To remove them from `b` we can clip the
    inverse of `b` against `a`. The code for union now looks like this::
    
        a.clipTo(b);
        b.clipTo(a);
        b.invert();
        b.clipTo(a);
        b.invert();
        a.build(b.allPolygons());
    
    Subtraction and intersection naturally follow from set operations. If
    union is `A | B`, subtraction is `A - B = ~(~A | B)` and intersection is
    `A & B = ~(~A | ~B)` where `~` is the complement operator.
    
    ## License
    
    Copyright (c) 2011 Evan Wallace (http://madebyevan.com/), under the MIT license.
    
    Python port Copyright (c) 2012 Tim Knip (http://www.floorplanner.com), under the MIT license.
    Additions by Alex Pletzer (Pennsylvania State University)
    """
    def __init__(self):
        self.polygons = []

    def __hash__(self):
        verts = _np.array(self.toVerticesAndPolygons()[0])
        as_string = _np.array2string(verts)
        checksum = int(_md5(as_string.encode()).hexdigest(), 16)

        return checksum

    @classmethod
    def fromPolygons(cls, polygons, testGeom = False):
        csg = CSG()
        csg.polygons = polygons
        return csg
    
    def clone(self):
        csg = CSG()
        csg.polygons = list([p.clone() for p in self.polygons])
        return csg
        
    def toPolygons(self):
        return self.polygons

    def isNull(self):
        return len(self.toPolygons()) == 0

    def polygonCount(self):
        '''Return number of polygons in CSG solid'''
        return len(self.polygons)

    def vertexCount(self):
        '''Return number of vertices in CSG solid'''
        vCount = 0
        for p in self.polygons :
            vCount += len(p.vertices)

        return vCount

    def refine(self):
        """
        Return a refined CSG. To each polygon, a middle point is added to each edge and to the center 
        of the polygon
        """
        newCSG = CSG()
        for poly in self.polygons:

            verts = poly.vertices
            numVerts = len(verts)

            if numVerts == 0:
                continue

            midPos = reduce(operator.add, [v.pos for v in verts]) / float(numVerts)
            midNormal = None
            if verts[0].normal is not None:
                midNormal = poly.plane.normal
            midVert = Vertex(midPos, midNormal)

            newVerts = verts + \
                       [verts[i].interpolate(verts[(i + 1)%numVerts], 0.5) for i in range(numVerts)] + \
                       [midVert]

            i = 0
            vs = [newVerts[i], newVerts[i+numVerts], newVerts[2*numVerts], newVerts[2*numVerts-1]]
            newPoly = Polygon(vs, poly.shared)
            newPoly.shared = poly.shared
            newPoly.plane = poly.plane
            newCSG.polygons.append(newPoly)

            for i in range(1, numVerts):
                vs = [newVerts[i], newVerts[numVerts+i], newVerts[2*numVerts], newVerts[numVerts+i-1]]
                newPoly = Polygon(vs, poly.shared)
                newCSG.polygons.append(newPoly)
                
        return newCSG

    def translate(self, disp):
        """
        Translate Geometry.
           disp: displacement (array of floats)
        """
        d = Vector(disp[0], disp[1], disp[2])
        for poly in self.polygons:
            for v in poly.vertices:
                v.pos = v.pos.plus(d)
                # no change to the normals


    def scale(self, scale):
        """
        Translate Geometry.
           scale: displacement (array of floats)
        """
        d = Vector(scale[0], scale[1], scale[2])
        for poly in self.polygons:
            for v in poly.vertices:
                v.pos = v.pos.scale(d)
                # no change to the normals

    def rotate(self, axis, angleDeg):
        """
        Rotate geometry.
           axis: axis of rotation (array of floats)
           angleDeg: rotation angle in degrees
        """
        ax = Vector(axis[0], axis[1], axis[2]).unit()
        cosAngle = _np.cos(_np.pi * angleDeg / 180.)
        sinAngle = _np.sin(_np.pi * angleDeg / 180.)

        def newVector(v):
            vA = v.dot(ax)
            vPerp = v.minus(ax.times(vA))
            vPerpLen = vPerp.length()
            if vPerpLen == 0:
                # vector is parallel to axis, no need to rotate
                return v
            u1 = vPerp.unit()
            u2 = u1.cross(ax)
            vCosA = vPerpLen*cosAngle
            vSinA = vPerpLen*sinAngle
            return ax.times(vA).plus(u1.times(vCosA).plus(u2.times(vSinA)))

        for poly in self.polygons:
            for vert in poly.vertices:
                vert.pos = newVector(vert.pos)
                normal = vert.normal
                if normal.length() > 0:
                    vert.normal = newVector(vert.normal)
    
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
        sortedVertexIndex = sorted(list(vertexIndexMap.items()),
                                   key=operator.itemgetter(1))
        verts = []
        for v, i in sortedVertexIndex:
            p = []
            for c in v.split(','):
                p.append(float(c) - offset)
            verts.append(tuple(p))
        return verts, polys, count

    def saveVTK(self, filename):
        """
        Save polygons in VTK file.
        """
        with open(filename, 'w') as f:
            f.write('# vtk DataFile Version 3.0\n')
            f.write('pycsg output\n')
            f.write('ASCII\n')
            f.write('DATASET POLYDATA\n')
        
            verts, cells, count = self.toVerticesAndPolygons()

            f.write('POINTS {0} float\n'.format(len(verts)))
            for v in verts:
                f.write('{0} {1} {2}\n'.format(v[0], v[1], v[2]))
            numCells = len(cells)
            f.write('POLYGONS {0} {1}\n'.format(numCells, count + numCells))
            for cell in cells:
                f.write('{0} '.format(len(cell)))
                for index in cell:
                    f.write('{0} '.format(index))
                f.write('\n')

    def union(self, csg):
        """
        Return a new CSG solid representing space in either this solid or in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.union(B)
        
            +-------+            +-------+
            |       |            |       |
            |   A   |            |       |
            |    +--+----+   =   |       +----+
            +----+--+    |       +----+       |
                 |   B   |            |       |
                 |       |            |       |
                 +-------+            +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.clipTo(b)
        b.clipTo(a)
        b.invert()
        b.clipTo(a)
        b.invert()
        a.build(b.allPolygons());
        return CSG.fromPolygons(a.allPolygons())

    def __add__(self, csg):
        return self.union(csg)
        
    def subtract(self, csg):
        """
        Return a new CSG solid representing space in this solid but not in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.subtract(B)
        
            +-------+            +-------+
            |       |            |       |
            |   A   |            |       |
            |    +--+----+   =   |    +--+
            +----+--+    |       +----+
                 |   B   |
                 |       |
                 +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.invert()
        a.clipTo(b)
        b.clipTo(a)
        b.invert()
        b.clipTo(a)
        b.invert()
        a.build(b.allPolygons())
        a.invert()
        return CSG.fromPolygons(a.allPolygons())

    def __sub__(self, csg):
        return self.subtract(csg)
        
    def intersect(self, csg):
        """
        Return a new CSG solid representing space both this solid and in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.intersect(B)
        
            +-------+
            |       |
            |   A   |
            |    +--+----+   =   +--+
            +----+--+    |       +--+
                 |   B   |
                 |       |
                 +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.invert()
        b.clipTo(a)
        b.invert()
        a.clipTo(b)
        b.clipTo(a)
        a.build(b.allPolygons())
        a.invert()
        return CSG.fromPolygons(a.allPolygons())

    def coplanarIntersection(self, csg):
        # print 'pycsg.core.coplanarIntersection>'

        absp = BSPNode(self.clone().polygons)
        bbsp = BSPNode(csg.clone().polygons)

        apolygons = absp.allPolygons()
        bpolygons = bbsp.allPolygons()

        polygons = []

        def coplanarPolys(apoly,bpoly) :
            COPLANAR = 0  # all the vertices are within EPSILON distance from plane
            FRONT = 1  # all the vertices are in front of the plane
            BACK = 2  # all the vertices are at the back of the plane

            aplane = apoly.plane
            bplane = bpoly.plane

            if abs(aplane.normal.dot(bplane.normal)-1) < 1e-5 and abs(aplane.w-bplane.w) < 1e-7  :
                return True
            elif abs(aplane.normal.dot(bplane.normal)+1) < 1e-5 and abs(aplane.w+bplane.w) < 1e-7 :
                return True
            else :
                return False

        def polyVertsInside(apoly, bpoly):

            aplane = apoly.plane

            vertsInside = []
            for i in range(len(bpoly.vertices)):
                ploc = 0

                for j in range(len(apoly.vertices)):
                    if j == len(apoly.vertices) - 1:
                        av = apoly.vertices[0].pos - apoly.vertices[j].pos
                    else:
                        av = apoly.vertices[j + 1].pos - apoly.vertices[j].pos
                    avunit = av.unit()
                    anormal = aplane.normal.cross(avunit)

                    # distance inside place
                    t = anormal.dot(bpoly.vertices[i].pos) - apoly.vertices[j].pos.dot(anormal)

                    # check if inside
                    if t >= 0:
                        ploc += 1

                if ploc == len(apoly.vertices):
                    vertsInside.append(bpoly.vertices[i].pos)

            return vertsInside

        def polyEdgeIntersection(apoly, bpoly) :

            vertsInter = []

            for i in range(len(bpoly.vertices)) :
                if i == len(bpoly.vertices) - 1:
                    bv = bpoly.vertices[0].pos - bpoly.vertices[i].pos
                else:
                    bv = bpoly.vertices[i + 1].pos - bpoly.vertices[i].pos
                bvunit = bv.unit()
                b0 = bpoly.vertices[i].pos

                for j in range(len(apoly.vertices)) :
                    if j == len(apoly.vertices) - 1:
                        av = apoly.vertices[0].pos - apoly.vertices[j].pos
                    else:
                        av = apoly.vertices[j + 1].pos - apoly.vertices[j].pos
                    avunit = av.unit()
                    a0 = apoly.vertices[j].pos

                    aPlaneNormal   = avunit.cross(apoly.plane.normal)

                    denom = bvunit.dot(aPlaneNormal)
                    if denom != 0 :
                        soln   = -(b0 - a0).dot(aPlaneNormal)/denom
                        inter  =  soln*bvunit+b0
                        adist  = (inter-a0).dot(avunit)
                        bdist  = (inter-b0).dot(bvunit)
                        andist = (inter-a0).dot(apoly.plane.normal)

                        if adist >= 0 and adist < av.length() and bdist < bv.length() and soln > 0:
                            vertsInter.append(_Vector(inter))

            return vertsInter

        def convexHull(positions,normal) :

            if len(positions) < 3 :
                return None

            hull = []

            q_now  = positions[0]
            q_next = positions[1]

            nhull = 0
            while nhull < len(positions) :

                hull.append(q_now)
                nhull = nhull + 1

                for p in positions :
                    try :
                        p1 = (q_next-q_now).unit()
                    except ZeroDivisionError :
                        return None
                    try :
                        p2 = (p-q_now).unit()
                    except ZeroDivisionError :
                        return None
                    if p1.cross(p2).dot(normal) < 0 :
                        q_next = p

                q_now = q_next
                q_next = positions[0]

            v = []
            for p in hull :
                v.append(_Vertex(p))

            # print v
            return Polygon(v)

        for i in range(0,len(apolygons),1):                     # loop over all A polygons
            apoly  = apolygons[i]
            for j in range(0,len(bpolygons),1):                 # loop over all B polygons
                bpoly = bpolygons[j]

                copl  = coplanarPolys(apoly,bpoly)

                if not copl :
                    continue

                aInsideB = polyVertsInside(apoly,bpoly)
                bInsideA = polyVertsInside(bpoly,apoly)
                aInterB  = polyEdgeIntersection(apoly,bpoly)

                #if len(aInsideB) != 0 and len(bInsideA) != 0 and len(aInterB) != 0 :
                #    print len(aInsideB), len(bInsideA), len(aInterB)

                #if len(aInsideB)+len(bInsideA)+len(aInterB) != 0 :
                #    print len(aInsideB),len(bInsideA),len(aInterB)

                points = []
                points.extend(aInsideB)
                points.extend(bInsideA)
                points.extend(aInterB)

                polygon  = convexHull(points,bpoly.plane.normal)
                if polygon :
                    polygons.append(polygon)
                #else :
                #    polygons.append(bpoly)
        return CSG.fromPolygons(polygons)

    def coplanar(self, csg):

        absp = BSPNode(self.clone().polygons)
        bbsp = BSPNode(csg.clone().polygons)

        apolygons = absp.allPolygons()
        bpolygons = bbsp.allPolygons()


        COPLANAR = 0 # all the vertices are within EPSILON distance from plane
        FRONT    = 1 # all the vertices are in front of the plane
        BACK     = 2 # all the vertices are at the back of the plane

        a = []

        #for apoly in apolygons :
        #    aplane = apoly.plane
        #    print 'aplane ', aplane.normal, aplane.w
        #
        #    for i in  range(0,len(apoly.vertices)) :
        #        print 'apoly ', apoly.vertices[i]

        #for bpoly in bpolygons :
        #    bplane = bpoly.plane
        #    print 'bplane ', bplane.normal, bplane.w

        #    for i in  range(0,len(bpoly.vertices)) :
        #        print 'bpoly ', bpoly.vertices[i]

        # loop over all A polygons
        for apoly in apolygons :
            aplane = apoly.plane
            for bpoly in bpolygons :
                bplane = bpoly.plane

                # check if B polygon is coplanar
                polygonType = 0
                for i in range(len(bpoly.vertices)) :
                    t = aplane.normal.dot(bpoly.vertices[i].pos) - aplane.w
                    loc = -1

                    if t < -1e-8 :
                        loc = BACK
                    elif t > 1e-8 :
                        loc = FRONT
                    else :
                        loc = COPLANAR
                    polygonType |= loc

                # if coplanar do a interior/exterior check
                if polygonType == COPLANAR :

                    aAdd = False

                    for i in range(len(bpoly.vertices)) :
                        ploc = 0

                        if i == len(bpoly.vertices)-1 :
                            bv = bpoly.vertices[0].pos   - bpoly.vertices[i].pos
                        else :
                            bv = bpoly.vertices[i+1].pos - bpoly.vertices[i].pos


                        # project b edge (bv) onto apoly plane
                        bvOnA = bv-aplane.normal*aplane.normal.dot(bv)
                        bpOnA = aplane.normal.dot(bpoly.vertices[i].pos)

                        for j in range(len(apoly.vertices)) :
                            if j == len(apoly.vertices)-1 :
                                av = apoly.vertices[0].pos   - apoly.vertices[j].pos
                            else :
                                av = apoly.vertices[j+1].pos - apoly.vertices[j].pos
                            avunit  = av.unit()
                            anormal = aplane.normal.cross(avunit)

                            # distance inside place
                            t  = anormal.dot(bpoly.vertices[i].pos) - apoly.vertices[j].pos.dot(anormal)

                            # check if inside
                            if t >= 0 :
                                ploc += 1

                            # test for intersection between bvOnA and av


                            # print 'apoly verticies t',i,j,t, aplane.normal, aplane.w, avunit, anormal, apoly.vertices[j].pos.dot(anormal), apoly.vertices[j], bpoly.vertices[i].pos, ploc

                        # print 'ploc, len',ploc,len(apoly.vertices)

                        if ploc == len(apoly.vertices) :
                            aAdd = True
                            break



                    if aAdd:
                        # print 'adding'
                        a.append(bpoly)


        return CSG.fromPolygons(a)

    def __mul__(self, csg):
        return self.intersect(csg)
        
    def inverse(self):
        """
        Return a new CSG solid with solid and empty space switched. This solid is
        not modified.
        """
        csg = self.clone()
        list(map(lambda p: p.flip(), csg.polygons))
        return csg

    def getNumberPolys(self):
        return len(self.polygons)

    @classmethod
    def cube(cls, center=[0,0,0], radius=[1,1,1]):
        """
        Construct an axis-aligned solid cuboid. Optional parameters are `center` and
        `radius`, which default to `[0, 0, 0]` and `[1, 1, 1]`. The radius can be
        specified using a single number or a list of three numbers, one for each axis.
        
        Example code::
        
            cube = CSG.cube(
              center=[0, 0, 0],
              radius=1
            )
        """
        c = Vector(0, 0, 0)
        r = [1, 1, 1]
        if isinstance(center, list): c = Vector(center)
        if isinstance(radius, list): r = radius
        else: r = [radius, radius, radius]

        polygons = list([Polygon( 
                list([Vertex(
                        Vector(
                            c.x + r[0] * (2 * bool(i & 1) - 1),
                            c.y + r[1] * (2 * bool(i & 2) - 1),
                            c.z + r[2] * (2 * bool(i & 4) - 1)
                        ), 
                        None
                    ) for i in v[0]])) for v in [
                        [[0, 4, 6, 2], [-1, 0, 0]],
                        [[1, 3, 7, 5], [+1, 0, 0]],
                        [[0, 1, 5, 4], [0, -1, 0]],
                        [[2, 6, 7, 3], [0, +1, 0]],
                        [[0, 2, 3, 1], [0, 0, -1]],
                        [[4, 5, 7, 6], [0, 0, +1]]
                    ]])
        return CSG.fromPolygons(polygons)
        
    @classmethod
    def sphere(cls, **kwargs):
        """ Returns a sphere.
            
            Kwargs:
                center (list): Center of sphere, default [0, 0, 0].
                
                radius (float): Radius of sphere, default 1.0.
                
                slices (int): Number of slices, default 16.
                
                stacks (int): Number of stacks, default 8.
        """
        center = kwargs.get('center', [0.0, 0.0, 0.0])
        if isinstance(center, float):
            center = [center, center, center]
        c = Vector(center)
        r = kwargs.get('radius', 1.0)
        if isinstance(r, list) and len(r) > 2:
            r = r[0]
        slices = kwargs.get('slices', 16)
        stacks = kwargs.get('stacks', 8)
        polygons = []
        def appendVertex(vertices, theta, phi):
            d = Vector(
                _np.cos(theta) * _np.sin(phi),
                _np.cos(phi),
                _np.sin(theta) * _np.sin(phi))
            vertices.append(Vertex(c.plus(d.times(r)), d))
            
        dTheta = _np.pi * 2.0 / float(slices)
        dPhi = _np.pi / float(stacks)

        j0 = 0
        j1 = j0 + 1
        for i0 in range(0, slices):
            i1 = i0 + 1
            #  +--+
            #  | /
            #  |/
            #  +
            vertices = []
            appendVertex(vertices, i0 * dTheta, j0 * dPhi)
            appendVertex(vertices, i1 * dTheta, j1 * dPhi)
            appendVertex(vertices, i0 * dTheta, j1 * dPhi)
            polygons.append(Polygon(vertices))

        j0 = stacks - 1
        j1 = j0 + 1
        for i0 in range(0, slices):
            i1 = i0 + 1
            #  +
            #  |\
            #  | \
            #  +--+
            vertices = []
            appendVertex(vertices, i0 * dTheta, j0 * dPhi)
            appendVertex(vertices, i1 * dTheta, j0 * dPhi)
            appendVertex(vertices, i0 * dTheta, j1 * dPhi)
            polygons.append(Polygon(vertices))
            
        for j0 in range(1, stacks - 1):
            j1 = j0 + 0.5
            j2 = j0 + 1
            for i0 in range(0, slices):
                i1 = i0 + 0.5
                i2 = i0 + 1
                #  +---+
                #  |\ /|
                #  | x |
                #  |/ \|
                #  +---+
                verticesN = []
                appendVertex(verticesN, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesN, i2 * dTheta, j2 * dPhi)
                appendVertex(verticesN, i0 * dTheta, j2 * dPhi)
                polygons.append(Polygon(verticesN))
                verticesS = []
                appendVertex(verticesS, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesS, i0 * dTheta, j0 * dPhi)
                appendVertex(verticesS, i2 * dTheta, j0 * dPhi)
                polygons.append(Polygon(verticesS))
                verticesW = []
                appendVertex(verticesW, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesW, i0 * dTheta, j2 * dPhi)
                appendVertex(verticesW, i0 * dTheta, j0 * dPhi)
                polygons.append(Polygon(verticesW))
                verticesE = []
                appendVertex(verticesE, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesE, i2 * dTheta, j0 * dPhi)
                appendVertex(verticesE, i2 * dTheta, j2 * dPhi)
                polygons.append(Polygon(verticesE))
                
        return CSG.fromPolygons(polygons)
    
    @classmethod
    def cylinder(cls, **kwargs):
        """ Returns a cylinder.
            
            Kwargs:
                start (list): Start of cylinder, default [0, -1, 0].
                
                end (list): End of cylinder, default [0, 1, 0].
                
                radius (float): Radius of cylinder, default 1.0.
                
                slices (int): Number of slices, default 16.
        """
        s = kwargs.get('start', Vector(0.0, -1.0, 0.0))
        e = kwargs.get('end', Vector(0.0, 1.0, 0.0))
        if isinstance(s, list):
            s = Vector(*s)
        if isinstance(e, list):
            e = Vector(*e)
        r = kwargs.get('radius', 1.0)
        slices = kwargs.get('slices', 16)
        ray = e.minus(s)

        axisZ = ray.unit()
        isY = (_np.fabs(axisZ.y) > 0.5)
        axisX = Vector(float(isY), float(not isY), 0).cross(axisZ).unit()
        axisY = axisX.cross(axisZ).unit()
        start = Vertex(s, axisZ.negated())
        end = Vertex(e, axisZ.unit())
        polygons = []
        
        def point(stack, angle, normalBlend):
            out = axisX.times(_np.cos(angle)).plus(
                axisY.times(_np.sin(angle)))
            pos = s.plus(ray.times(stack)).plus(out.times(r))
            normal = out.times(1.0 - _np.fabs(normalBlend)).plus(
                axisZ.times(normalBlend))
            return Vertex(pos, normal)
            
        dt = _np.pi * 2.0 / float(slices)
        for i in range(0, slices):
            t0 = i * dt
            i1 = (i + 1) % slices
            t1 = i1 * dt
            polygons.append(Polygon([start.clone(), 
                                     point(0., t0, -1.), 
                                     point(0., t1, -1.)]))
            polygons.append(Polygon([point(0., t1, 0.), 
                                     point(0., t0, 0.),
                                     point(1., t0, 0.), 
                                     point(1., t1, 0.)]))
            polygons.append(Polygon([end.clone(), 
                                     point(1., t1, 1.), 
                                     point(1., t0, 1.)]))
        
        return CSG.fromPolygons(polygons)

    @classmethod
    def cone(cls, **kwargs):
        """ Returns a cone.
            
            Kwargs:
                start (list): Start of cone, default [0, -1, 0].
                
                end (list): End of cone, default [0, 1, 0].
                
                radius (float): Maximum radius of cone at start, default 1.0.
                
                slices (int): Number of slices, default 16.
        """
        s = kwargs.get('start', Vector(0.0, -1.0, 0.0))
        e = kwargs.get('end', Vector(0.0, 1.0, 0.0))
        if isinstance(s, list):
            s = Vector(*s)
        if isinstance(e, list):
            e = Vector(*e)
        r = kwargs.get('radius', 1.0)
        slices = kwargs.get('slices', 16)
        ray = e.minus(s)
        
        axisZ = ray.unit()
        isY = (_np.fabs(axisZ.y) > 0.5)
        axisX = Vector(float(isY), float(not isY), 0).cross(axisZ).unit()
        axisY = axisX.cross(axisZ).unit()
        startNormal = axisZ.negated()
        start = Vertex(s, startNormal)
        polygons = []
        
        taperAngle = _np.atan2(r, ray.length())
        sinTaperAngle = _np.sin(taperAngle)
        cosTaperAngle = _np.cos(taperAngle)
        def point(angle):
            # radial direction pointing out
            out = axisX.times(_np.cos(angle)).plus(
                axisY.times(_np.sin(angle)))
            pos = s.plus(out.times(r))
            # normal taking into account the tapering of the cone
            normal = out.times(cosTaperAngle).plus(axisZ.times(sinTaperAngle))
            return pos, normal

        dt = _np.pi * 2.0 / float(slices)
        for i in range(0, slices):
            t0 = i * dt
            i1 = (i + 1) % slices
            t1 = i1 * dt
            # coordinates and associated normal pointing outwards of the cone's
            # side
            p0, n0 = point(t0)
            p1, n1 = point(t1)
            # average normal for the tip
            nAvg = n0.plus(n1).times(0.5)
            # polygon on the low side (disk sector)
            polyStart = Polygon([start.clone(), 
                                 Vertex(p0, startNormal), 
                                 Vertex(p1, startNormal)])
            polygons.append(polyStart)
            # polygon extending from the low side to the tip
            polySide = Polygon([Vertex(p0, n0), Vertex(e, nAvg), Vertex(p1, n1)])
            polygons.append(polySide)

        return CSG.fromPolygons(polygons)

def do_intersect(first, second):
    return not first.intersect(second).isNull()
