class meshingType :
    pycsg    = 1
    cgal_sm  = 2
    cgal_np  = 3

meshing = meshingType.cgal_sm


def backedName():
    if meshing == 1:
        return "pycsg"
    if meshing == 2:
        return "cgal_sm"
    if meshing == 3:
        return "cgal_np"


