import os
from itertools import zip_longest as _zip_longest

import pandas as pd

from .card import Card

# http://www.fluka.org/content/manuals/online/5.2.html

PREDEFINED_ELEMENT_NAMES = ["BLCKHOLE",
                            "VACUUM",
                            "HYDROGEN",
                            "HELIUM",
                            "BERYLLIU",
                            "CARBON",
                            "NITROGEN",
                            "OXYGEN",
                            "MAGNESIU",
                            "ALUMINUM",
                            "IRON",
                            "COPPER",
                            "SILVER",
                            "SILICON",
                            "GOLD",
                            "MERCURY",
                            "LEAD",
                            "TANTALUM",
                            "SODIUM",
                            "ARGON",
                            "CALCIUM",
                            "TIN",
                            "TUNGSTEN",
                            "TITANIUM",
                            "NICKEL"]

PREDEFINED_COMPOUND_NAMES = ["WATER",
                             "POLYSTYR",
                             "PLASCINT",
                             "PMMA",
                             "BONECOMP",
                             "BONECORT",
                             "MUSCLESK",
                             "MUSCLEST",
                             "ADTISSUE",
                             "KAPTON",
                             "POLYETHY",
                             "AIR"]

PREDEFINED_MATERIAL_NAMES = PREDEFINED_ELEMENT_NAMES + PREDEFINED_COMPOUND_NAMES

class _MassNumberLookup(object):
    THISDIR = os.path.dirname(os.path.abspath(__file__))
    def __init__(self):
        self.table = pd.read_csv(
            os.path.join(self.THISDIR, "periodic-table.csv"))

    def getMassNumberFromAtomicNumber(self, z):
        t = self.table
        result = t["AtomicMass"][t["AtomicNumber"] == z].values
        if not result:
            raise FLUKAError(
                "Unable to determine mass number for Z = {}".format(z))

        return int(round(result))


_MASS_NUMBER_LOOKUP = _MassNumberLookup()

def buildPredefinedMaterials():
    pass

class BuiltIn(object):
    def __init__(self, name, massNumber=None, flukaregistry=None):
        self.name = name

        self.massNumner = massNumber # Necessary for some conversions.

        if flukaregistry is not None:
            return flukaregistry

    def __repr__(self):
        return "<Builtin: {}>".format(self.name)

    def flukaFreeString(self, delim=""):
        return ""


class Element(object):
    def __init__(self, name, atomicNumber, density,
                 massNumber=None,
                 flukaregistry=None):
        self.name = name
        self.atomicNumber = atomicNumber
        self.density = density

        if massNumber is None:
            self.massNumber = _MASS_NUMBER_LOOKUP.getMassNumberFromAtomicNumber(
                atomicNumber)

        if flukaregistry is not None:
            flukaregistry.addMaterial(self)

    def isGas(self):
        return self.density < 0.01

    def toCard(self):
        return Card("MATERIAL",
                    what1=self.atomicNumber,
                    what3=self.density,
                    what6=self.massNumber,
                    sdum=self.name)

    def flukaFreeString(self, delim=", "):
        return self.toCard().toFreeString(delim=delim)

    def __repr__(self):
        massNumber = ""
        if self.massNumber is not None:
            massNumber = ", A={}".format(self.massNumber)
        return '<Element: "{}", Z={}, density={}*g/cm3{}>'.format(
            self.name,
            self.atomicNumber,
            self.density,
            massNumber)

    @classmethod
    def fromCard(cls, card, flukaregistry):
        return cls(card.sdum, card.what1, card.what3,
                   massNumber=card.what6,
                   flukaregistry=flukaregistry)

    def geat4material(self, greg):
        pass

class Compound(object):
    def __init__(self, name, density, fractions, fractionType,
                 flukaregistry=None):
        self.name = name
        self.density = density
        self.fractions = fractions
        if fractionType not in {"atomic", "mass", "volume"}:
            raise ValueError("Unknown fractionType: {}".format(fractionType))
        self.fractionType = fractionType

        if flukaregistry is not None:
            flukaregistry.addMaterial(self)

    def toCards(self):
        compoundName =self.name
        material = Card(keyword="MATERIAL",
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
            card = Card("COMPOUND", what1=frac, what2=name, sdum=compoundName)
            if second is not None:
                frac, name  = _formatFlukaMaterialPair(second, namePrefix,
                                                       fractionPrefix)
                card.what3 = frac
                card.what4 = name

            if third is not None:
                frac, name = _formatFlukaMaterialPair(third, namePrefix,
                                                      fractionPrefix)

                card.what5 = frac
                card.what6 = name
            compounds.append(card)

        return [material] + compounds

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
                            " are not supported for material={}".format(name))

        # Map the material names to material/compound instances via
        # the FlukaRegistry.
        fractions = [(flukareg.getMaterial(name), f) for name, f in fractions]

        return cls(compoundName, density, fractions, fractionTypes[0],
                   flukaregistry=flukareg)

    @property
    def massNumber(self):
        number = 0
        for material, _ in self.fractions:
            number += material.massNumber
        return number

    def __repr__(self):
        return "<Compound: {}, density={}*g/cm3, nparts={}>".format(
            self.name,
            self.density,
            len(self.fractions))


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
    """Returns the (name, fraction, fractionType)."""
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


def _formatFlukaMaterialPair(first, namePrefix, fractionPrefix):
    return ("{}{}".format(fractionPrefix, first[1]),
            "{}{}".format(namePrefix, first[0].name))

def _grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    https://docs.python.org/3/library/itertools.html#recipes"""
    args = [iter(iterable)] * n
    return _zip_longest(fillvalue=fillvalue, *args)
