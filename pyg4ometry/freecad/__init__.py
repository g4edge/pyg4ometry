useFreeCAD = True

try:
    from .Reader import *
except ImportError:
    useFreeCAD = False
    pass
    # print 'Cannot load freecad'
