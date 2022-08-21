from . import config
from . import compare
from . import convert
from . import exceptions
from . import fluka
from . import freecad
from . import gdml
from . import io
from . import geant4
from . import pycgal
try :
    from . import pyoce
except ImportError:
    print("Failed to import open cascade")
#try:
#    from . import gui
#except ImportError:
#    import warnings
#    warnings.warn("Failed to import pyg4ometry.gui subpackage.")
#    del warnings
from . import stl
from . import transformation
from . import visualisation
from . import features
from . import bdsim
from . import cli

__version__ = "1.0.1"
