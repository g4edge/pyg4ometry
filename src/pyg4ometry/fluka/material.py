from itertools import zip_longest as _zip_longest

from .card import Card as _Card

# http://www.fluka.org/content/manuals/online/5.2.html
# name, atomic mass, atomic number, density in g/cm3
_PREDEFINED_ELEMENTS = [("BLCKHOLE",  0, 0, 0),
                        ("VACUUM",    0, 0, 0),
                        ("HYDROGEN",  1.00794, 1., 0.0000837),
                        ("HELIUM",    4.002602, 2., 0.000166),
                        ("BERYLLIU",  9.012182, 4., 1.848),
                        ("CARBON",    12.0107, 6., 2.000),
                        ("NITROGEN",  14.0067, 7., 0.00117),
                        ("OXYGEN",    15.9994, 8., 0.00133),
                        ("MAGNESIU",  24.3050, 12., 1.740),
                        ("ALUMINUM",  26.981538, 13., 2.699),
                        ("IRON",      55.845, 26., 7.874),
                        ("COPPER",    63.546, 29., 8.960),
                        ("SILVER",    107.8682, 47., 10.500),
                        ("SILICON",   28.0855, 14., 2.329),
                        ("GOLD",      196.96655, 79., 19.320),
                        ("MERCURY",   200.59, 80., 13.546),
                        ("LEAD",      207.2, 82., 11.350),
                        ("TANTALUM",  180.9479, 73., 16.654),
                        ("SODIUM",    22.989770, 11., 0.971),
                        ("ARGON",     39.948, 18., 0.00166),
                        ("CALCIUM",   40.078, 20., 1.550),
                        ("TIN",       118.710, 50., 7.310),
                        ("TUNGSTEN",  183.84, 74., 19.300),
                        ("TITANIUM",  47.867, 22., 4.540),
                        ("NICKEL",    58.6934, 28., 8.902)]

# Name, density
_PREDEFINED_COMPOUNDS =  [("WATER", 1.0),
                          ("POLYSTYR", 1.06),
                          ("PLASCINT", 1.032),
                          ("PMMA", 1.19),
                          ("BONECOMP", 1.85),
                          ("BONECORT", 1.85),
                          ("MUSCLESK", 1.04),
                          ("MUSCLEST", 1.04),
                          ("ADTISSUE", 0.92),
                          ("KAPTON", 1.42),
                          ("POLYETHY", 0.94),
                          ("AIR", 0.00120479)]

def predefinedMaterialNames():
    names = [i[0] for i in _PREDEFINED_ELEMENTS]
    names.extend(i[0] for i in _PREDEFINED_COMPOUNDS)
    return names

class BuiltIn(object):
    def __init__(self, name, *,
                 atomicNumber=None,
                 atomicMass=None,
                 density=None,
                 flukaregistry=None):
        self.name = name
        self.atomicNumber = atomicNumber
        self.atomicMass = atomicMass
        self.density = density
        if flukaregistry is not None:
            flukaregistry.addMaterial(self)

    def __repr__(self):
        return "<Builtin: {}>".format(self.name)

    def flukaFreeString(self, delim=""):
        return ""

def defineBuiltInFlukaMaterials(flukaregistry=None):
    out = {}
    for name, atomicMass, atomicNumber, density in _PREDEFINED_ELEMENTS:
        out[name] = BuiltIn(name,
                            atomicNumber=atomicNumber,
                            atomicMass=atomicMass,
                            density=density,
                            flukaregistry=flukaregistry)
    for name, density in _PREDEFINED_COMPOUNDS:
        out[name] = BuiltIn(name, density=density, flukaregistry=flukaregistry)
    return out

class _MatProp(object):
    def isGas(self):
        return self.density < 0.01 or self.pressure

    def makeMatPropCard(self):
        return _Card("MAT-PROP", what1=self.pressure, what4=self.name)

class Material(_MatProp):
    """A FLUKA material consisting of a single element.  This corresponds
    to the case in FLUKA of a single MATERIAL card with no associated
    COMPOUND cards, as well as a possible MAT-PROP card (only if a
    pressure is provided, other options of MAT-PROP are unsupported).

    :param name: The name of the material
    :type name: str
    :param atomicNumber: the atomic number, Z, of the element.
    :type atomicNumber: int
    :param density: the density in g/cm3 of the material.
    :type density: float
    :param massNumber: Optional mass number, will be inferred in FLUKA \
    based on atomicNumber.  Allows one to specify a specific isotope.
    :type massNumber: int, None
    :param atomicMass: The mass of the atom in g/mole.  Will be
    inferred in FLUKA based on atomicNumber.
    :type atomicMass: float
    :param pressure: Optional pressure if the material is a gas.
    :type pressure: float
    :param flukaregistry: Optional FlukaRegistry instance the material is to be
    added to.
    :type flukaregistry: FlukaRegistry

    """
    def __init__(self, name, atomicNumber, density,
                 massNumber=None,
                 atomicMass=None,
                 pressure=None,
                 flukaregistry=None):
        self.name = name
        self.atomicNumber = atomicNumber
        self.density = density
        self.atomicMass = atomicMass
        self.massNumber = massNumber
        self.pressure = pressure
        if flukaregistry is not None:
            flukaregistry.addMaterial(self)

    def toCards(self):
        material = [_Card("MATERIAL",
                         what1=self.atomicNumber,
                         what2=self.atomicMass,
                         what3=self.density,
                         what6=self.massNumber,
                         sdum=self.name)]
        if self.pressure:
            material.append(self.makeMatPropCard())
        return material

    def flukaFreeString(self, delim=", "):
        return "".join(c.toFreeString(delim=delim) for c in self.toCards())

    def __repr__(self):
        massNumber = ""
        if self.massNumber is not None:
            massNumber = ", A={}".format(self.massNumber)
        return '<Material: "{}", Z={}, density={}*g/cm3{}>'.format(
            self.name,
            self.atomicNumber,
            self.density,
            massNumber)

    @classmethod
    def fromCard(cls, card, flukaregistry):
        return cls(card.sdum, card.what1, card.what3,
                   massNumber=card.what6,
                   flukaregistry=flukaregistry)


class Compound(_MatProp):
    """
    A FLUKA compound material. This corresponds to the case in
    FLUKA of a single MATERIAL card with one or more associated
    COMPOUND cards.

    :param name: The name of the compound.
    :type name: str
    :param density: The density of the compound in g/cm3
    :type density: float
    :param fractions: List of (Element, fraction) and (Compound, \
    fraction) tuples corresponding to the fractional proportion of \
    that material.
    :type fractions: list
    :param fractionType: The type of the fractions listed in the \
    fractions parameter, either atomic, mass, or volume.
    :type fractionType: str
    :param flukaregistry: Optional FlukaRegistry instance the Compound \
    is to be added to.
    :type flukaregistry: FlukaRegistry
    """
    def __init__(self, name, density, fractions, fractionType,
                 pressure=None,
                 flukaregistry=None):
        self.name = name
        self.density = density
        self.fractions = fractions
        if fractionType not in {"atomic", "mass", "volume"}:
            raise ValueError(f"Unknown fractionType: {fractionType}")
        self.fractionType = fractionType
        self.pressure = pressure

        if flukaregistry is not None:
            flukaregistry.addMaterial(self)

    def toCards(self):
        compoundName =self.name
        material = _Card(keyword="MATERIAL",
                        what3=self.density,
                        sdum=compoundName)


        fractionPrefix = ""
        namePrefix = ""
        fractiontype = self.fractionType

        if fractiontype == "mass":
            fractionPrefix = "-"
        elif fractiontype == "volume":
            fractionPrefix = "-"
            namePrefix = "-"

        compounds = []
        for first, second, third in  _grouper(3, self.fractions):
            frac, name  = _formatFlukaMaterialPair(first, namePrefix,
                                                   fractionPrefix)
            card = _Card("COMPOUND", what1=frac, what2=name, sdum=compoundName)
            if second is not None:
                frac, name  = _formatFlukaMaterialPair(second,
                                                       namePrefix,
                                                       fractionPrefix)
                card.what3 = frac
                card.what4 = name

            if third is not None:
                frac, name = _formatFlukaMaterialPair(third, namePrefix,
                                                      fractionPrefix)

                card.what5 = frac
                card.what6 = name
            compounds.append(card)

        matprop = []
        if self.pressure:
            matprop = [self.makeMatPropCard()]

        return [material] + compounds + matprop

    def flukaFreeString(self, delim=", "):
        return "\n".join(c.toFreeString(delim=delim) for c in self.toCards())

    @classmethod
    def fromCards(cls, cards, flukareg):
        material = next(c for c in cards if c.keyword == "MATERIAL")
        compounds = (c for c in cards if c.keyword == "COMPOUND")

        compoundName = material.sdum
        density = material.what3

        fractions = []
        fractionTypes = []
        for c in compounds:
            if c.sdum != compoundName:
                raise ValueError("COMPOUND name does not match MATERIAL name.")
            _appendFractionPairs(c, fractions, fractionTypes)

        if len(set(fractionTypes)) > 2:
            raise TypeError("Mixed mass, volume, and fraction types"
                            f" are not supported for material={compoundName}")

        # Map the material names to material/compound instances via the FlukaRegistry.
        fractions = [(flukareg.getMaterial(name), f) for name, f in fractions]

        return cls(compoundName, density, fractions, fractionTypes[0],
                   flukaregistry=flukareg)

    def __repr__(self):
        return "<Compound: {}, density={}*g/cm3, nparts={}>".format(
            self.name,
            self.density,
            len(self.fractions))

    def totalWeighting(self, densityWeighted=False):
        if not densityWeighted:
            return sum(x[1] for x in self.fractions)
        return sum(x[0].density * x[1] for x in self.fractions)


def _appendFractionPairs(card, fractions, fractionTypes):
    if card.what1 is not None and card.what2 is not None:
        name, fraction, fractiontype = _parseFraction(card.what1, card.what2)
        fractions.append((name, fraction))
        fractionTypes.append(fractiontype)

    if card.what3 is not None and card.what4 is not None:
        name, fraction, fractiontype = _parseFraction(card.what3, card.what4)
        fractions.append((name, fraction))
        fractionTypes.append(fractiontype)

    if card.what5 is not None and card.what6 is not None:
        name, fraction, fractiontype = _parseFraction(card.what5, card.what6)
        fractions.append((name, fraction))
        fractionTypes.append(fractiontype)

def _parseFraction(what1, what2):
    """Returns the (name, fraction, fractionType). This is for handling
    the different permuations found in the FLUKA manual COMPOUND
    entry

    """
    prefix1 = str(what1)[0]
    prefix2 = str(what2)[0]
    # What1 is a fraction, what2 is a formatted (potentially
    # "negative") name.
    if prefix1 != "-" and prefix2 != "-":
        # atom fraction
        return what2, what1, "atomic"
    elif prefix1 == "-" and prefix2 != "-":
        return what2, abs(what1), "mass"
    elif prefix1 == "-" and prefix2 == "-":
        return str(what2)[1:], abs(what1), "volume"

    raise ValueError("Unknown compound fraction format")


def _formatFlukaMaterialPair(pair, namePrefix, fractionPrefix):
    """Names and fractions maybe stored as "negative" numbers in the
    FLUKA input, permutations between which mean different types of fractions."""
    # pair is just an entry from the list of (material, fraction)
    # tuples.
    return (f"{fractionPrefix}{pair[1]}", f"{namePrefix}{pair[0].name}")

def _grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    https://docs.python.org/3/library/itertools.html#recipes"""
    args = [iter(iterable)] * n
    return _zip_longest(fillvalue=fillvalue, *args)
