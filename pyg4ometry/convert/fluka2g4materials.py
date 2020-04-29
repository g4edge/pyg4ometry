import pandas as pd

from pyg4ometry.geant4 import MaterialPredefined, MaterialSingleElement
from pyg4ometry.fluka.material import BuiltIn, Element, Compound

FLUKA_BUILTIN_TO_G4_MATERIAL_MAP = {
    "BLCKHOLE": "G4_Galactic",
    "VACUUM": "G4_Galactic",
    "HYDROGEN": "G4_H",
    "HELIUM": "G4_He",
    "BERYLLIU": "G4_Be",
    "CARBON": "G4_B",
    "NITROGEN": "G4_N",
    "OXYGEN": "G4_O",
    "MAGNESIU": "G4_Mg",
    "ALUMINUM": "G4_Al",
    "IRON": "G4_Fe",
    "COPPER": "G4_Cu",
    "SILVER": "G4_Ag",
    "SILICON": "G4_Si",
    "GOLD": "G4_Au",
    "MERCURY": "G4_Hg",
    "LEAD": "G4_Pb",
    "TANTALUM": "G4_Ta",
    "SODIUM": "G4_Na",
    "ARGON": "G4_Ar",
    "CALCIUM": "G4_Ca",
    "TIN": "G4_Sn",
    "TUNGSTEN": "G4_W",
    "TITANIUM": "G4_Ti",
    "NICKEL": "G4_Ni"
}


def addFlukaMaterialsToG4Registry(freg, greg):
    """Convert the materials defined in a FlukaRegistry, and populate
    the provided geant4 registry with said materials."""

    mnl = _MassNumberLookup()

    fluka = freg.materialDict

    for name, material in fluka.iteritems():
        if isinstance(material, BuiltIn):
            MaterialPredefined(FLUKA_BUILTIN_TO_G4_MATERIAL_MAP[name],
                               registry=greg)
        elif isinstance(material, Element):
            name = material.name
            atomicNumber = material.atomicNumber
            density = material.density
            massNumber = material.massNumber
            if massNumber is None:
                massNumber = mnl.getMassNumberFromAtomicNumber(atomicNumber)
            MaterialSingleElement(name, atomicNumber, massNumber,
                                  density, registry=greg)
        elif isinstance(material, Compound):
            pass

    return greg

class _MassNumberLookup(object):
    def __init__(self):
        self.table = pd.read_csv("periodic-table.csv")

    def getMassNumberFromAtomicNumber(self, z):
        t = self.table
        return int(round(t["AtomicMass"][t["AtomicNumber"] == z].values))

            
