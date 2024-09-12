class P:
    """
    Plane (general)
    """

    def __init__(self, A, B, C, D, reg=None, surfaceNumber=None):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"P: {self.A} {self.B} {self.C} {self.D}"


class PX:
    """
    Plane (normal to x-axis)
    """

    def __init__(self, D, reg=None, surfaceNumber=None):
        self.D = D
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"PX: {self.D}"


class PY:
    """
    Plane (normal to y-axis)
    """

    def __init__(self, D, reg=None, surfaceNumber=None):
        self.D = D
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"PY: {self.D}"


class PZ:
    """
    Plane (normal to z-axis)
    """

    def __init__(self, D, reg=None, surfaceNumber=None):
        self.D = D
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"PZ: {self.D}"


class SO:
    """
    Sphere (centered at origin)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"SO: {self.R}"


class S:
    """
    Sphere (general)
    """

    def __init__(self, x, y, z, R, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"S: {self.x} {self.y} {self.z} {self.R}"


class SX:
    """
    Sphere (centered on x-axis)
    """

    def __init__(self, x, R, reg=None, surfaceNumber=None):
        self.x = x
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"SX: {self.x} {self.R}"


class SY:
    """
    Sphere (centered on y-axis)
    """

    def __init__(self, y, R, reg=None, surfaceNumber=None):
        self.y = y
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"SY: {self.y} {self.R}"


class SZ:
    """
    Sphere (centered on z-axis)
    """

    def __init__(self, z, R, reg=None, surfaceNumber=None):
        self.z = z
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"SZ: {self.z} {self.R}"


class C_X:
    """
    Cylinder (parallel to x-axis)
    """

    def __init__(self, y, z, R, reg=None, surfaceNumber=None):
        self.y = y
        self.z = z
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"C_X: {self.y} {self.z} {self.R}"


class C_Y:
    """
    Cylinder (parallel to y-axis)
    """

    def __init__(self, x, z, R, reg=None, surfaceNumber=None):
        self.x = x
        self.z = z
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"C_Y: {self.x} {self.z} {self.R}"


class C_Z:
    """
    Cylinder (parallel to z-axis)
    """

    def __init__(self, x, y, R, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"C_Z: {self.x} {self.y} {self.R}"


class CX:
    """
    Cylinder (on x-axis)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"CX: {self.R}"


class CY:
    """
    Cylinder (on y-axis)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"CY: {self.R}"


class CZ:
    """
    Cylinder (on z-axis)
    """

    def __init__(self, R, reg=None, surfaceNumber=None):
        self.R = R
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"CZ: {self.R}"


""" surface: Cone

:param sign: choice positive slope or negative slope.

The quadratic equation for a cone describes a cone of two sheets. One sheet is a
cone of positive slope, and the other has a negative slope. The parameter sign
provides the option to select either of the two sheets. The +1 or the -1 entry on
the cone surface card causes the one sheet cone treatment to be used. If the sign
of the entry is positive, the specified sheet is the one that extends to infinity
in the positive direction of the coordinate axis to which the cone axis is parallel.
The converse is true for a negative entry.
"""


class K_X:
    """
    Cone (parallel to x-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, y, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"K_X: {self.x} {self.y} {self.z} {self.t_sqr} {self.sign}"


class K_Y:
    """
    Cone (parallel to y-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, y, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"K_Y: {self.x} {self.y} {self.z} {self.t_sqr} {self.sign}"


class K_Z:
    """
    Cone (parallel to z-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, y, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"K_Z: {self.x} {self.y} {self.z} {self.t_sqr} {self.sign}"


class KX:
    """
    Cone (on x-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, x, t_sqr, sign, reg=None, surfaceNumber=None):
        self.x = x
        self.t_sqr = t_sqr
        self.sign = sign
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"KX: {self.x} {self.t_sqr} {self.sign}"


class KY:
    """
    Cone (on y-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, y, t_sqr, sign, reg=None, surfaceNumber=None):
        self.y = y
        self.t_sqr = t_sqr
        self.sign = sign
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"KY: {self.y} {self.t_sqr} {self.sign}"


class KZ:
    """
    Cone (on z-axis)

    :param t_sqr: t squared.
    :param sign: Choice positive slope or negative slope.
    """

    def __init__(self, z, t_sqr, sign, reg=None, surfaceNumber=None):
        self.z = z
        self.t_sqr = t_sqr
        self.sign = sign
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"KZ: {self.z} {self.t_sqr} {self.sign}"


class SQ:
    """
    Ellipsoid, Hyperboloid, Paraboloid
    (axes parallel to x-, y-, or z-axis)
    """

    def __init__(self, A, B, C, D, E, F, G, x, y, z, reg=None, surfaceNumber=None):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.E = E
        self.F = F
        self.G = G
        self.x = x
        self.y = y
        self.z = z
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"SQ: {self.A} {self.B} {self.C} {self.D} {self.E}"
            f" {self.F} {self.G} {self.x} {self.y} {self.z}"
        )


class GQ:
    """
    Cylinder, Cone, Ellipsoid, Hyperboloid, Paraboloid
    (axes not parallel to x-, y-, or z-axis)
    """

    def __init__(self, A, B, C, D, E, F, G, H, J, K, reg=None, surfaceNumber=None):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.E = E
        self.F = F
        self.G = G
        self.H = H
        self.J = J
        self.K = K
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"GQ: {self.A} {self.B} {self.C} {self.D} {self.E}"
            f" {self.F} {self.G} {self.H} {self.J} {self.K}"
        )


class TX:
    """
    Elliptical or Circular Torus
    (axis is parallel to x-, y-, or z-axis)
    rotationally symmetric about axes parallel to the x-axes
    """

    def __init__(self, x, y, z, A, B, C, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.A = A
        self.B = B
        self.C = C
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"TX: {self.x} {self.y} {self.z} {self.A} {self.B} {self.C}"


class TY:
    """
    Elliptical or Circular Torus
    (axis is parallel to x-, y-, or z-axis)
    rotationally symmetric about axes parallel to the y-axes
    """

    def __init__(self, x, y, z, A, B, C, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.A = A
        self.B = B
        self.C = C
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"TY: {self.x} {self.y} {self.z} {self.A} {self.B} {self.C}"


class TZ:
    """
    Elliptical or Circular Torus
    (axis is parallel to x-, y-, or z-axis)
    rotationally symmetric about axes parallel to the z-axes
    """

    def __init__(self, x, y, z, A, B, C, reg=None, surfaceNumber=None):
        self.x = x
        self.y = y
        self.z = z
        self.A = A
        self.B = B
        self.C = C
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"TZ: {self.x} {self.y} {self.z} {self.A} {self.B} {self.C} "


class BOX:
    """
    Macrobody: Box
    arbitrarily oriented orthogonal box
    all corner angels are 90 degrees

    :param vx, vy, vz: The x,y,z coordinates of a corner of the box.
    :param a1x, a1y, a1z: Vector of 1st side from the specified corner coordinates.
    :param a2x, a2y, a2z: Vector of 2nd side from the specified corner coordinates.
    :param a3x, a3y, a3z: Vector of 3rd side from the specified corner coordinates.
    """

    def __init__(
        self, vx, vy, vz, a1x, a1y, a1z, a2x, a2y, a2z, a3x, a3y, a3z, reg=None, surfaceNumber=None
    ):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.a1x = a1x
        self.a1y = a1y
        self.a1z = a1z
        self.a2x = a2x
        self.a2y = a2y
        self.a2z = a2z
        self.a3x = a3x
        self.a3y = a3y
        self.a3z = a3z
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"BOX: {self.vx} {self.vy} {self.vz} {self.a1x} {self.a1y} {self.a1z} "
            f" {self.a2x} {self.a2y} {self.a2z} {self.a3x} {self.a3y} {self.a3z}"
        )


class RPP:
    """
    Macrobody: Rectangular Parallelepiped
    RPP surfaces will only be normal to the x-, y-, and z-axes
    x,y,z values are relative to the origin

    :param xmin, xmax: Termini of box sides normal to the x-axis.
    :param ymin, ymax: Termini of box sides normal to the y-axis.
    :param zmin, zmax: Termini of box sides normal to the z-axis.
    """

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax, reg=None, surfaceNumber=None):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"RPP: {self.xmin} {self.xmax} {self.ymin} "
            f" {self.ymin} {self.ymax} {self.zmin} {self.zmax}"
        )


class SPH:
    """
    Macrobody: Sphere

    :param vx, vy, vz: The x,y,z coordinates of the center of the sphere.
    :param r: Radius of sphere.
    """

    def __init__(self, vx, vy, vz, r, reg=None, surfaceNumber=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.r = r
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"SPH: {self.vx} {self.vy} {self.vz} {self.r}"


class RCC:
    """
    Macrobody: Right Circular Cylinder

    :param vx, vy, vz: The x,y,z coordinates at the center of the base for the right circular cylinder.
    :param hx, hy, hz: Right circular cylinder axis vector, which provides both the orientation and the \
    height of the cylinder.
    :param r: Radius of right circular cylinder.
    """

    def __init__(self, vx, vy, vz, hx, hy, hz, r, reg=None, surfaceNumber=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.r = r
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"RCC: {self.vx} {self.vy} {self.vz} {self.hx} {self.hy} {self.hz} {self.r}"


class RHP_HEX:
    """
    Macrobody: Right Hexagonal Prism

    :param vx, vy, vz: The x,y,z coordinates of the bottom of the hexagonal prism.
    :param h1, h2, h3: Vector from the bottom to the top of the hexagonal prism. \
    For a z-hex with height h, h1, h2, and h3= 0 0 h.
    :param r1, r2, r3: Vector from the axis to the center of the 1st facet. \
    For a pitch 2p facet normal to y-axis, r1, r2, and r3= 0 p 0.
    :param s1, s2, s3: Vector to center of the 2nd facet.
    :param t1, t2, t3: Vector to center of the 3rd facet.
    """

    def __init__(
        self,
        vx,
        vy,
        vz,
        h1,
        h2,
        h3,
        r1,
        r2,
        r3,
        s1,
        s2,
        s3,
        t1,
        t2,
        t3,
        reg=None,
        surfaceNumber=None,
    ):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"RHP_HEX: {self.vx} {self.vy} {self.vz}"
            f" {self.h1} {self.h2} {self.h3}"
            f" {self.r1} {self.r2} {self.r3}"
            f" {self.s1} {self.s2} {self.s3}"
            f" {self.t1} {self.t2} {self.t3}"
        )


class REC:
    """
    Macrobody: Right Elliptical Cylinder

    :param vx, vy, vz: The x,y,z coordinates of the cylinder bottom.
    :param hx, hy, hz: Cylinder axis height vector.
    :param v1x, v1y, v1z: Ellipse major axis vector (normal to hx hy hz).
    :param v1x, v1y, v1z: Ellipse minor axis vector (orthogonal to vectors h and v1).
    """

    def __init__(
        self, vx, vy, vz, hx, hy, hz, v1x, v1y, v1z, v2x, v2y, v2z, reg=None, surfaceNumber=None
    ):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.v1x = v1x
        self.v1y = v1y
        self.v1z = v1z
        self.v2x = v2x
        self.v2y = v2y
        self.v2z = v2z
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"REC: {self.vx} {self.vy} {self.vz}"
            f" {self.hx} {self.hy} {self.hz}"
            f" {self.v1x} {self.v1y} {self.v1z}"
            f" {self.v2x} {self.v2y} {self.v2z}"
        )


class TRC:
    """
    Macrobody: Truncated Right-Angle Cone

    :param vx, vy, vz: the x,y,z coordinates of the cone bottom
    :param hx, hy, hz: cone axis height vector
    :param r1: radius of lower cone base
    :param r2: radius of upper cone base, where r1>r2
    """

    def __init__(self, vx, vy, vz, hx, hy, hz, r1, r2, reg=None, surfaceNumber=None):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.r1 = r1
        self.r2 = r2
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"TRC: {self.vx} {self.vy} {self.vz}"
            f" {self.hx} {self.hy} {self.hz}"
            f" {self.r1} {self.r2}"
        )


class ELL:
    """
    Macrobody: Ellipsoid

    :param v1x, v1y, v1z: /
        if rm>0, the coordinates of the 1st focus /
        if rm<0, the coordinates of the center of the ellipsoid
    :param v2x, v2y, v2z:
        if rm>0, the coordinates of the 2nd focus /
        if rm<0, major axis vector (vector from the center of the ellipsoid through a focus to the vertex; /
        length = major radius)
    :param rm:
        if rm>0, major radius length /
        if rm<0, minor radius length
    """

    def __init__(self, v1x, v1y, v1z, v2x, v2y, v2z, rm, reg=None, surfaceNumber=None):
        self.v1x = v1x
        self.v1y = v1y
        self.v1z = v1z
        self.v2x = v2x
        self.v2y = v2y
        self.v2z = v2z
        self.rm = rm
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return f"ELL: {self.v1x} {self.v1y} {self.v1z} {self.v2x} {self.v2y} {self.v2z} {self.rm}"


class WED:
    """
    Macrobody: Wedge

    :param vx, vy, vz: the x,y,z coordinates of wedge vertex
    :param v1x, v1y, v1z: vector of 1st side of triangular base
    :param v2x, v2y, v2z: vector of 2nd side of triangular base
    :param v3x, v3y, v3z: height vector
    """

    def __init__(
        self, vx, vy, vz, v1x, v1y, v1z, v2x, v2y, v2z, v3x, v3y, v3z, reg=None, surfaceNumber=None
    ):
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.vx = v1x
        self.vy = v1y
        self.vz = v1z
        self.vx = v2x
        self.vy = v2y
        self.vz = v2z
        self.vx = v3x
        self.vy = v3y
        self.vz = v3z
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"WED: {self.vx} {self.vy} {self.vz}"
            f" {self.v1x} {self.v1y} {self.v1z}"
            f" {self.v2x} {self.v2y} {self.v2z}"
            f" {self.v3x} {self.v3y} {self.v3z}"
        )


class ARB:
    """
    Macrobody: Arbitrary Polyhedron

    :param ax, ay, az, bx, by, bz, cx, cy, cz, dx, dy, dz, /
    ex, ey, ez, fx, fy, fz, gx, gy, gz, hx, hy, hz: /
    The x-, y-, z-coordinates of the 1st through 8th corners of the polyhedron. \
    There must be eight x,y,z triplets to describe the eight corners of the polyhedron.
    :param n1, n2, n3, n4, n5, n6: /
    Four-digit numbers describing a side of the polyhedron in terms of its corresponding corners. /
    E.g., n1=1278 is a plane/side bounded by corners 1, 2, 7, and 8 (a, b, g, and h).
    """

    def __init__(
        self,
        ax,
        ay,
        az,
        bx,
        by,
        bz,
        cx,
        cy,
        cz,
        dx,
        dy,
        dz,
        ex,
        ey,
        ez,
        fx,
        fy,
        fz,
        gx,
        gy,
        gz,
        hx,
        hy,
        hz,
        n1,
        n2,
        n3,
        n4,
        n5,
        n6,
        surfaceNumber=None,
        reg=None,
    ):
        self.ax = ax
        self.ay = ay
        self.az = az
        self.bx = bx
        self.by = by
        self.bz = bz
        self.cx = cx
        self.cy = cy
        self.cz = cz
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.ex = ex
        self.ey = ey
        self.ez = ez
        self.fx = fx
        self.fy = fy
        self.fz = fz
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.hx = hx
        self.hy = hy
        self.hz = hz
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.n5 = n5
        self.n6 = n6
        self.surfaceNumber = surfaceNumber
        if reg:
            reg.addSurface(self)

    def __repr__(self):
        return (
            f"ARB: {self.ax} {self.ay} {self.az}"
            f" {self.bx} {self.by} {self.bz}"
            f" {self.cx} {self.cy} {self.cz}"
            f" {self.dx} {self.dy} {self.dz}"
            f" {self.ex} {self.ey} {self.ez}"
            f" {self.fx} {self.fy} {self.fz}"
            f" {self.gx} {self.gy} {self.gz}"
            f" {self.hx} {self.hy} {self.hz}"
            f" {self.n1} {self.n2} {self.n3}"
            f" {self.n4} {self.n5} {self.n6}"
        )
