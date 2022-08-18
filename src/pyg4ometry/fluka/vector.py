import numpy as _np
import pyg4ometry.transformation as _trf


class Three(_np.ndarray):
    def __new__(cls, *coordinates):
        # If an array-like of 3:
        if (_np.shape(coordinates) == (1, 3)):
            obj = _np.asarray(coordinates[0], dtype=float).view(cls)
        elif _np.shape(coordinates) == (3,): # If supplied as x, y, z
            obj = _np.asarray(coordinates, dtype=float).view(cls)
        else:
            raise TypeError("Unknown construction: %s" % (coordinates,))
        return obj

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    def parallel_to(self, other, tolerance=1e-10):
        """
        Check if instance is parallel to some other vector, v
        """
        return _np.linalg.norm(_np.cross(self, other)) < tolerance

    def unit(self):
        """
        Get this as a unit vector.
        """
        return self/_np.linalg.norm(self)

    def length(self):
        """
        vector length (l2 norm)

        """
        return _np.linalg.norm(self)

    def dot(self, other):
        return _np.dot(self,other)

    def cross(self, other):
        return _np.cross(self,other)

    def __eq__(self, other):
        try:
            return (self.x == other.x
                    and self.y == other.y
                    and self.z == other.z)
        except AttributeError:
            pass
        try:
            return (self.x == other[0]
                    and self.y == other[1]
                    and self.z == other[2]
                    and len(self) == len(other))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        try:
            return Three(self.x + other.x,
                         self.y + other.y,
                         self.z + other.z)
        except AttributeError:
            pass
        try:
            return Three(self.x + other[0],
                         self.y + other[1],
                         self.z + other[2])
        except (AttributeError, IndexError, TypeError):
            pass
        return Three(self.x + other,
                     self.y + other,
                     self.z + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        try:
            return Three(self.x - other.x,
                         self.y - other.y,
                         self.z - other.z)
        except AttributeError:
            pass
        try:
            return Three(self.x - other[0],
                         self.y - other[1],
                         self.z - other[2])
        except (AttributeError, IndexError):
            pass
        return Three(self.x - other,
                     self.y - other,
                     self.z - other)


    def __rsub__(self, other):
        return self - other

    def __iadd__(self, other):
        temp = self + other
        self.x = temp.x
        self.y = temp.y
        self.z = temp.z
        return self

    def __isub__(self, other):
        temp = self - other
        self.x = temp.x
        self.y = temp.y
        self.z = temp.z
        return self


class AABB(object):
    def __init__(self, lower, upper):
        self.lower = Three(lower)
        self.upper = Three(upper)
        self.size = self.upper - self.lower
        self.centre = self.upper - 0.5 * self.size

        for i, j in zip(lower, upper):
            if i >= j:
                raise ValueError("Lower extent must be less than upper.")

    def __repr__(self):
        return ("<AABB: Lower({lower.x}, {lower.y}, {lower.z}),"
                " Upper({upper.x}, {upper.y}, {upper.z})>".format(
                    upper=self.upper, lower=self.lower))

    def __eq__(self, other):
        return self.lower == other.lower and self.upper == other.upper

    def cornerDistance(self):
        # distance from centre to one of the corners.
        size = self.size
        return ((0.5 * size.x)**2 + (0.5 * size.y)**2 + (0.5 * size.z)**2)**0.5

    @classmethod
    def fromMesh(cls, csgmesh):
        vertices = csgmesh.toVerticesAndPolygons()[0]
        x = [v[0] for v in vertices]
        y = [v[1] for v in vertices]
        z = [v[2] for v in vertices]
        return cls([min(x), min(y), min(z)],
                   [max(x), max(y), max(z)])

    def intersects(self, other):
        return not (self.upper.x < other.lower.x
                        or self.lower.x > other.upper.x
                        or self.upper.y < other.lower.y
                        or self.lower.y > other.upper.y
                        or self.upper.z < other.lower.z
                        or self.lower.z > other.upper.z)

    def coplanarIntersects(self, other):
        return not (self.upper.x <= other.lower.x
                        or self.lower.x >= other.upper.x
                        or self.upper.y <= other.lower.y
                        or self.lower.y >= other.upper.y
                        or self.upper.z <= other.lower.z
                        or self.lower.z >= other.upper.z)

    def envelops(self, other):
        return (self.upper.x > other.upper.x
                    and self.lower.x < other.lower.x
                    and self.upper.y > other.lower.y
                    and self.lower.y < other.lower.y
                    and self.upper.z > other.upper.z
                    and self.lower.z < other.lower.z)

    def intersect(self, other):
        lower = [max(a, b) for a, b in zip(self.lower, other.lower)]
        upper = [min(a, b) for a, b in zip(self.upper, other.upper)]
        return AABB(lower, upper)

    def union(self, other):
        lower = [min(a, b) for a, b in zip(self.lower, other.lower)]
        upper = [max(a, b) for a, b in zip(self.upper, other.upper)]
        return AABB(lower, upper)

    def isNull(self):
        return any(self.lower >= self.upper)


def areAABBsOverlapping(first, second):
    """Check if two AABB instances are overlapping."""
    return first.intersects(second)

def pointOnLineClosestToPoint(point, point_on_line, direction):
    """
    Line is defined in terms of two vectors:  a point on the line and
    the direction of the line.

    point is the point with which the distance to the line is to be
    minimised.

    """
    # Algorithm pinched from:

    # Get another point on the line:
    p0 = Three(point)
    p1 = Three(point_on_line)
    a = Three(direction)

    # In the name of rapidity, implementation pinched from:
    # https://math.stackexchange.com/questions/13176/how-to-find-a-point-on-a-line-closest-to-another-given-point
    t = ((- a.x * (p1.x - p0.x) - a.y * (p1.y - p0.y) - a.z * (p1.z - p0.z))
         / (a.x * a.x + a.y * a.y + a.z * a.z))
    pt = p1 + t * a

    return pt

def pointOnPlaneClosestToPoint(planeNormal, planePoint, point):
    """Get point on plane which is closest to point not on the plane."""
    planeNormal = planeNormal / _np.linalg.norm(planeNormal)
    distance = _np.dot((planePoint - point), planeNormal)
    return point + distance * planeNormal

def areParallelOrAntiParallel(v1, v2):
    v1 = v1 / _np.linalg.norm(v1)
    v2 = v2 / _np.linalg.norm(v2)
    return _np.isclose(v1, v2).all() or _np.isclose(v1, -v2).all()
