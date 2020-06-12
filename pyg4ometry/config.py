class meshingType :
    pycsg    = 1
    cgal_sm  = 2
    cgal_np  = 3

# meshing = meshingType.cgal_sm
meshing = meshingType.pycsg

def backendName():
    if meshing == 1:
        return "pycsg"
    if meshing == 2:
        return "cgal_sm"
    if meshing == 3:
        return "cgal_np"


