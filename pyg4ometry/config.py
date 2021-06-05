class meshingType :
    pycsg    = 1
    cgal_sm  = 2
    cgal_np  = 3

meshing = meshingType.cgal_sm
# meshing = meshingType.pycsg

def backendName():
    if meshing == 1:
        return "pycsg"
    if meshing == 2:
        return "cgal_sm"
    if meshing == 3:
        return "cgal_np"


# Global settings for default meshing settings for solids
# nslice and and nstacks determine the discretisation of curved solids.
# Solids that are curved in the x-y plane (e.g. Tubs) only need nslice. Solids that are
# curved both planes x-y and x-z planes (e.g. Sphere) need both nslice and nstack.

def setGlobalMeshSliceAndStack(value):
    for key in SolidDefaults.__dict__:
        solid = SolidDefaults.__dict__[key]
        if hasattr(solid, "nstack"):
            setattr(solid, "nstack", value)
        if hasattr(solid, "nslice"):
            setattr(solid, "nslice", value)


class SolidDefaults:
    class Tubs:
        nslice = 16

    class Cons:
        nslice = 16

    class CutTubs:
        nslice = 16

    class Ellipsoid:
        nslice = 8
        nstack = 8

    class EllipticalCone:
        nslice = 16
        nstack = 16

    class EllipticalTube:
        nslice = 20
        nstack = 10

    class GenericPolycone:
        nslice = 16

    class Hype:
        nslice = 16
        nstack = 16

    class Orb:
        nslice = 16
        nstack = 16

    class Paraboloid:
        nslice = 16
        nstack = 8

    class Polycone:
        nslice = 16

    class Sphere:
        nslice = 10
        nstack = 10

    class Torus:
        nslice = 50
        nstack = 10

    class TwistedBox:
        nstack = 20

    class TwistedTrap:
        nstack = 20

    class TwistedTrd:
        nstack = 20

    class TwistedTubs:
        nslice = 20
        nstack = 20

    class Wedge:
        nslice = 16





