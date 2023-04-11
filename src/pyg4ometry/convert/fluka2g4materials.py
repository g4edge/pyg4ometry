import pyg4ometry.geant4 as _g4
from pyg4ometry.exceptions import FLUKAError as _FLUKAError

_periodicTable = None

# http://www.fluka.org/content/manuals/online/5.2.html
# See also fluka/material.py
FLUKA_BUILTIN_TO_G4_MATERIAL_MAP = {
    # Elements
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
    "NICKEL": "G4_Ni",
    # Compounds
    "WATER": "G4_WATER",
    "POLYSTYR": "G4_POLYSTYRENE",
    "PLASCINT": "G4_PLASTIC_SC_VINYLTOLUENE",
    "PMMA": "G4_PLEXIGLASS",
    "BONECOMP": "G4_BONE_COMPACT_ICRU",
    "BONECORT": "G4_BONE_CORTICAL_ICRP", # This has slightly different density?
    "MUSCLESK": "G4_MUSCLE_SKELETAL_ICRP", # So does this..
    "MUSCLEST": "G4_MUSCLE_STRIATED_ICRU",
    "ADTISSUE": "G4_ADIPOSE_TISSUE_ICRP", # and this
    "KAPTON": "G4_KAPTON",
    "POLYETHY": "G4_POLYETHYLENE",
    "AIR": "G4_AIR"
}

# Need this to build up the set element instances (distinct from
# materials in Geant4)
_FLUKA_ELEMENT_SYMBOLS = {"HYDROGEN": "H",
                          "HELIUM": "He",
                          "BERYLLIU": "Be",
                          "CARBON": "B",
                          "NITROGEN": "N",
                          "OXYGEN": "O",
                          "MAGNESIU": "Mg",
                          "ALUMINUM": "Al",
                          "IRON": "Fe",
                          "COPPER": "Cu",
                          "SILVER": "Ag",
                          "SILICON": "Si",
                          "GOLD": "Au",
                          "MERCURY": "Hg",
                          "LEAD": "Pb",
                          "TANTALUM": "Ta",
                          "SODIUM": "Na",
                          "ARGON": "Ar",
                          "CALCIUM": "Ca",
                          "TIN": "Sn",
                          "TUNGSTEN": "W",
                          "TITANIUM": "Ti",
                          "NICKEL": "Ni"}


def _getPeriodicTable():
    global _periodicTable
    if _periodicTable is None:
        import pandas as pd
        import pkg_resources
        csv = pkg_resources.resource_filename(__name__, "periodic-table.csv")
        _periodicTable = pd.read_csv(csv)
    return _periodicTable

class _FlukaToG4MaterialConverter:
    def __init__(self, freg, greg):
        self.periodicTable = _PeriodicTable()
        self.freg = freg
        self.greg = greg
        self.g4materials = {}
        self.g4elements = {}
        self.g4elementKeysMangled = {}
        self.addPredefinedElements()

        self.convertAll()

    def addPredefinedElements(self):
        # The Concept of materials and elements are distinct in G4,
        # whereas in FLUKA they can be used interchangeably.
        for flukaName, symbol in _FLUKA_ELEMENT_SYMBOLS.items():
            z, a = self.periodicTable.atomicNumberAndMassFromSymbol(symbol)
            elementName = self._mangleElementName(flukaName)
            m = _g4.ElementSimple(elementName, symbol, z, a, registry=self.greg)
            self.g4elements[flukaName] = m # this has to be the name as it would be in the input for composing compounds
            self.g4elementKeysMangled[elementName] = m

    def convertAll(self):
        # delayed import as possibly heavy
        from pyg4ometry.fluka import material as _fluMat
        
        for name, material in self.freg.materials.items():
            if isinstance(material, _fluMat.BuiltIn):
                self.convertBuiltin(name, material)
            elif isinstance(material, _fluMat.Material):
                self.convertElement(name, material)
            elif isinstance(material, _fluMat.Compound):
                self.convertCompound(material)
            else:
                raise TypeError(f"Unknown material type {material}")

    def convertBuiltin(self, name, flukaMaterial):
        assert name == flukaMaterial.name
        g4material = _g4.MaterialPredefined(FLUKA_BUILTIN_TO_G4_MATERIAL_MAP[name], registry=self.greg)
        self.g4materials[name] = g4material

    def convertElement(self, name, flukaElement):
        assert name == flukaElement.name
        name = flukaElement.name
        atomicNumber = flukaElement.atomicNumber
        density = flukaElement.density
        atomicMass = self.periodicTable.atomicMassFromZ(atomicNumber)
        massNumber = self.periodicTable.atomicMassFromZ(atomicNumber)
        # We make both an Element instance and a Material
        # instance in case the element is to be used as an atomic
        # fraction, or as a plain material.
        elementName = self._mangleElementName(name)
        # In fluka there's no distinct element vs material, and you can redefine a predefined
        # material such as an element with a different density. So, to compose it we use the
        # converted predefined element (by mangled name) and then define the material as required
        # which will be unique as we've only predefined elements.
        if elementName not in self.g4elementKeysMangled:
            g4element = _g4.ElementSimple(elementName, elementName, atomicNumber,
                                          massNumber, registry=self.greg)
            self.g4elementKeysMangled[elementName] = g4element
        else:
            g4element = self.g4elementKeysMangled[elementName]
        g4material = _g4.MaterialSingleElement(name, atomicNumber, atomicMass,
                                               density, registry=self.greg)
        
        self.g4elements[name] = g4element
        self.g4materials[name] = g4material

    def convertCompound(self, flukaCompound):
        name = flukaCompound.name
        fractionType = flukaCompound.fractionType
        if fractionType == "atomic":
            self.convertAtomicFractionCompound(name, flukaCompound)
        elif fractionType == "mass":
            self.convertMassFractionCompound(name, flukaCompound)
        elif fractionType == "volume":
            self.convertVolumeFractionCompound(name, flukaCompound)

    def _makeBaseCompoundMaterial(self, name, flukaCompound):
        assert name == flukaCompound.name
        return _g4.MaterialCompound(name,
                                   flukaCompound.density,
                                   len(flukaCompound.fractions),
                                   registry=self.greg)

    def convertMassFractionCompound(self, name, flukaCompound):
        assert flukaCompound.fractionType == "mass"
        assert flukaCompound.name == name
        total = flukaCompound.totalWeighting()
        g4material = self._makeBaseCompoundMaterial(name, flukaCompound)

        for part, weight in flukaCompound.fractions:
            partName = part.name
            massFraction = weight / total
            g4part = self.g4materials[partName]
            g4material.add_material(g4part, massFraction)
        self.g4materials[name] = g4material

    def convertVolumeFractionCompound(self, name, flukaCompound):
        assert flukaCompound.fractionType == "volume"
        assert flukaCompound.name == name
        total = flukaCompound.totalWeighting(densityWeighted=True)
        g4material = self._makeBaseCompoundMaterial(name, flukaCompound)

        for part, weight in flukaCompound.fractions:
            partName = part.name
            massFraction = weight * part.density / total
            g4part = self.g4materials[partName]
            g4material.add_material(g4part, massFraction)
        self.g4materials[name] = g4material

    def convertAtomicFractionCompound(self, name, flukaCompound):
        assert flukaCompound.fractionType == "atomic"
        assert flukaCompound.name == name
        g4material = self._makeBaseCompoundMaterial(name, flukaCompound)
        totalAtomicWeight = self._totalMassWeightedFractionOfCompound(
            flukaCompound) 

        pt = self.periodicTable
        for part, fraction in flukaCompound.fractions:
            partName = part.name
            partAtomicWeight = pt.atomicMassFromZ(part.atomicNumber)
            massfraction = fraction * partAtomicWeight / totalAtomicWeight
            g4element = self.g4elements[partName]
            g4material.add_element_massfraction(g4element, massfraction)
        self.g4materials[name] = g4material

    def _totalMassWeightedFractionOfCompound(self, compound):
        total = 0
        for part, fraction in compound.fractions:
            total += (self.periodicTable.atomicMassFromZ(part.atomicNumber)
                      * fraction)
        return total

    @staticmethod
    def _mangleElementName(name):
        return f"{name}_element"

def makeFlukaToG4MaterialsMap(freg, greg):
    """Convert the materials defined in a FlukaRegistry, and populate
    the provided geant4 registry with said materials."""
    g = _FlukaToG4MaterialConverter(freg, greg)
    return g.g4materials

class _PeriodicTable(object):
    def __init__(self):
        self.table = _getPeriodicTable()

    def massNumberFromZ(self, z):
        t = self.table
        nNeutrons = t["NumberofNeutrons"][t["AtomicNumber"] == z].values
        if not nNeutrons:
            raise _FLUKAError("Unable to determine mass number for Z = {}".format(z))
        return int(nNeutrons) + z

    def atomicMassFromZ(self, z):
        t = self.table
        mask = t["AtomicNumber"] == z
        return float(t["AtomicMass"][mask])

    def atomicNumberAndMassFromSymbol(self, symbol):
        t = self.table
        mask = t["Symbol"] == symbol
        massNumber = int(t.AtomicMass[mask])
        atomicNumber = int(t.AtomicNumber[mask])

        return atomicNumber, massNumber
