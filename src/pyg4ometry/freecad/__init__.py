useFreeCAD = True

try:
    from .Reader import *
except ImportError:
    useFreeCAD = False
    # print 'Cannot load freecad'
