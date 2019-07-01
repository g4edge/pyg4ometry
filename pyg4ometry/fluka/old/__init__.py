"""pyfluka - Among among other things, this can be used to store a Fluka model
to be stored as a python object.  In addition to basic introspection
features, it also supports the conversion of the regions to GDML
volumes.

Notes:

- The only geometry format currently supported is the free, space-delimited
format.
- The only format currently supported for non-geometry cards is fixed format.

"""
from .model import Model
from . import geometry, materials, model
