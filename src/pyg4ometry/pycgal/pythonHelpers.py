import matplotlib.pyplot as _plt
import pyg4ometry as _pyg4

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

def draw_polygon_2(p2):
    '''
    Draw a CGAL polygon for debugging etc

    :param p2: Polygon_2 for plotting
    :type p2: Polygon_2, Polygon_with_holes_2, List_Polygon_with_holes_2
    '''

    if type(p2) == _pyg4.pycgal.Polygon_2.Polygon_2_EPECK or \
       type(p2) == _pyg4.pycgal.Polygon_2.Polygon_2_EPICK:
        _draw_polygon_2(p2)
    elif type(p2) == _pyg4.pycgal.Polygon_with_holes_2.Polygon_with_holes_2_EPECK or \
         type(p2) == _pyg4.pycgal.Polygon_with_holes_2.Polygon_with_holes_2_EPICK :
        _draw_polygon_2(p2.outer_boundary())
        for h in p2.holes() :
            _draw_polygon_2(h)

    elif type(p2) == _pyg4.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPECK or \
         type(p2) == _pyg4.pycgal.Polygon_with_holes_2.List_Polygon_with_holes_2_EPICK :
        for p in p2 :
            draw_polygon_2(p)

