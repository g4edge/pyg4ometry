import pyg4ometry


def make_square(sizex=1, sizey=1, offsetx=0, offsety=0):
    pa = pyg4ometry.pycgal.Polygon_2.Polygon_2_EPECK()
    p1 = pyg4ometry.pycgal.Point_2.Point_2_EPECK(offsetx, offsety)
    p2 = pyg4ometry.pycgal.Point_2.Point_2_EPECK(offsetx, sizey + offsety)
    p3 = pyg4ometry.pycgal.Point_2.Point_2_EPECK(sizex + offsetx, sizey + offsety)
    p4 = pyg4ometry.pycgal.Point_2.Point_2_EPECK(sizex + offsetx, offsety)

    pa.push_back(p1)
    pa.push_back(p2)
    pa.push_back(p3)
    pa.push_back(p4)

    return pa


def test_polygon_2_union():
    pa = make_square(1, 1, 0, 0)
    pb = make_square(1, 1, 0.5, 0.5)

    pr = pyg4ometry.pycgal.Polygon_with_holes_2.Polygon_with_holes_2_EPECK()

    pyg4ometry.pycgal.CGAL.join(pa, pb, pr)

    assert pr


def test_polygon_2_intersection():
    pa = make_square(1, 1, 0, 0)
    pb = make_square(1, 1, 0.5, 0.5)

    pr = pyg4ometry.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK()

    pyg4ometry.pycgal.CGAL.intersection(pa, pb, pr)

    assert pr


def test_polygon_2_difference():
    pa = make_square(1, 1, 0, 0)
    pb = make_square(1, 1, 0.5, 0.5)

    pr = pyg4ometry.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK()

    pyg4ometry.pycgal.CGAL.difference(pa, pb, pr)

    assert pr


def test_polygon_2_difference_hole():
    pa = make_square(5, 5, 0, 0)
    pb = make_square(2, 2, 1, 1)

    pr = pyg4ometry.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK()

    pyg4ometry.pycgal.CGAL.difference(pa, pb, pr)

    assert pr

    pa = pr[0]
    pb = make_square(1, 10, 2, -3)

    pr = pyg4ometry.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK()

    pyg4ometry.pycgal.CGAL.difference(pa, pb, pr)

    assert pr
