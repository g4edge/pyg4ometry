try:
    from ._version import version as __version__
    from ._version import version_tuple
except ImportError:
    __version__ = "unknown version"
    version_tuple = (0, 0, "unknown version")

import logging

_log = logging.getLogger(__name__)

from . import config
from . import compare
from . import convert
from . import exceptions
from . import fluka
from . import mcnp
from . import gdml
from . import io
from . import geant4
from . import pycgal

try:
    from . import pyoce
except ImportError:
    _log.error("Failed to import opencascade")
from . import stl
from . import transformation
from . import visualisation
from . import features
from . import bdsim
from . import cli
from . import misc
from . import analysis
from . import montecarlo
from . import usd
