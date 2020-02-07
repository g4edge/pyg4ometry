"""The Lattice class is defined in this module for handling LATTICEs
in FLUKA geometries.

"""

from .card import Card
from .directive import Transform

class Lattice(object):
    def __init__(self, cellRegion, rotoTranslation,
                 invertRotoTranslation=False, flukaregistry=None):
        self.cellRegion = cellRegion
        self.rotoTranslation = rotoTranslation
        self.invertRotoTranslation = invertRotoTranslation

        if flukaregistry is not None:
            flukaregistry.addLattice(self)

    def flukaFreeString(self, delim=", "):
        return Card("LATTICE", what1=self.cellRegion.name,
                    sdum=self.rotoTranslation.name).toFreeString(delim=delim)

    def getTransform(self):
        return Transform(rotoTranslation=self.rotoTranslation,
                         invertRotoTranslation=self.invertRotoTranslation)
