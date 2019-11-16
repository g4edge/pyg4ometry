import pyfluka.geometry as geo

def box_zone_from_xzp_xyp_yzp(xcentre=0, ycentre=0, zcentre=0,
                              xsize=20, ysize=20, zsize=20):


    yzp1 = geo.YZP("yzp1", xcentre + xsize/2.0)
    yzp2 = geo.YZP("yzp1", xcentre - xsize/2.0)

    xzp1 = geo.XZP("xzp1", ycentre + ysize/2.0)
    xzp2 = geo.XZP("xzp1", ycentre - ysize/2.0)

    xyp1 = geo.XYP("xyp1", zcentre + zsize/2.0)
    xyp2 = geo.XYP("xyp1", zcentre - zsize/2.0)

    zone =  geo.Zone([("+", yzp1),
                      ("-", yzp2),
                      ("+", xzp1),
                      ("-", xzp2),
                      ("+", xyp1),
                      ("-", xyp2)])
    return zone


def finite_cylinder_parallel_to_x_axis(xcentre=0,
                                       ycentre=0,
                                       zcentre=0,
                                       length=5,
                                       radius=2.5):
    # Construct a finite cylinder parallel to the x-axis from an
    # infinite cylinder parallel to the x-axis (XCC) and two
    # half-spaces, each facing perpendicular to the x-axis.
    xcc = geo.XCC("xcc", ycentre, zcentre, radius)
    yzp1 = geo.YZP("upper_cut", xcentre + length / 2.0)
    yzp2 = geo.YZP("lower_cut", xcentre - length / 2.0)

    zone = geo.Zone([("+", xcc),
                     ("+", yzp1),
                     ("-", yzp2)])
    return zone


def finite_cylinder_parallel_to_y_axis(xcentre=0,
                                       ycentre=0,
                                       zcentre=0,
                                       length=5,
                                       radius=2.5):
    # Construct a finite cylinder parallel to the y-axis from an
    # infinite cylinder parallel to the y-axis (YCC) and two
    # half-spaces, each facing perpendicular to the y-axis.
    ycc = geo.YCC("ycc", zcentre, xcentre, radius)
    xzp1 = geo.XZP("upper_cut", ycentre + length / 2.0)
    xzp2 = geo.XZP("lower_cut", ycentre - length / 2.0)

    zone = geo.Zone([("+", ycc),
                     ("+", xzp1),
                     ("-", xzp2)])
    return zone

def finite_cylinder_parallel_to_z_axis(xcentre=0,
                                       ycentre=0,
                                       zcentre=0,
                                       length=5,
                                       radius=2.5):
    # Construct a finite cylinder parallel to the z-axis from an
    # infinite cylinder parallel to the z-axis (ZCC) and two
    # half-spaces, each facing perpendicular to the z-axis.
    zcc = geo.ZCC("zcc", xcentre, ycentre, radius)
    xyp1 = geo.XYP("upper_cut", zcentre + length / 2.0)
    xyp2 = geo.XYP("lower_cut", zcentre - length / 2.0)

    zone = geo.Zone([("+", zcc),
                     ("+", xyp1),
                     ("-", xyp2)])
    return zone

def world_volume_hole():
    pass

def omitted_subtraction():
    pass
