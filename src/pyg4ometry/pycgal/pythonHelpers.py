import matplotlib.pyplot as _plt
from .. import pycgal as _pycgal


def polygon_to_numpy(polygon):
    ptns = []

    for i in range(polygon.size()):
        v = polygon.vertex(i)
        ptns.append([v.x(), v.y()])

    return ptns


def _draw_polygon_2(p2):
    x = []
    y = []

    for i in range(0, p2.size(), 1):
        p = p2.vertex(i)
        x.append(p.x())
        y.append(p.y())

    # add first point again to close plot
    x.append(p2.vertex(0).x())
    y.append(p2.vertex(0).y())

    _plt.plot(x, y)


def draw_polygon_2_list(pl):
    for p in pl:
        poly2 = _pycgal.Polygon_2.Polygon_2_EPECK()
        for v in p:
            poly2.push_back(_pycgal.Point_2.Point_2_EPECK(v[0], v[1]))

        draw_polygon_2(poly2)


def draw_polygon_2(p2):
    """
    Draw a CGAL polygon for debugging etc

    :param p2: Polygon_2 for plotting
    :type p2: Polygon_2, Polygon_with_holes_2, List_Polygon_with_holes_2
    """

    if (
        type(p2) == _pycgal.Polygon_2.Polygon_2_EPECK
        or type(p2) == _pycgal.Polygon_2.Polygon_2_EPICK
    ):
        _draw_polygon_2(p2)
    elif (
        type(p2) == _pycgal.Polygon_with_holes_2.Polygon_with_holes_2_EPECK
        or type(p2) == _pycgal.Polygon_with_holes_2.Polygon_with_holes_2_EPICK
    ):
        _draw_polygon_2(p2.outer_boundary())
        for h in p2.holes():
            _draw_polygon_2(h)
    elif (
        type(p2) == _pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK
        or type(p2) == _pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPICK
    ):
        for p in p2:
            draw_polygon_2(p)
    elif (
        type(p2) == _pycgal.Partition_traits_2_Polygon_2.Partition_traits_2_Polygon_2_EPECK
        or type(p2) == _pycgal.Partition_traits_2_Polygon_2.Partition_traits_2_Polygon_2_EPICK
    ):
        _draw_polygon_2(p2)
    else:
        print("Unknown polygon type", type(p2))
