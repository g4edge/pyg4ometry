"""
.. code-block:: text

    GLOBAL        20000.       -1.        1.        0.        0.        0.
    DEFAULTS         0.0       0.0       0.0       0.0       0.0      0.0 EM-CASCA
    BEAM            17.5       0.0   10000.0       0.0       0.0      1.0 ELECTRON
    GEOBEGIN          3.                                                  COMBNAME
                  0    0

    USRBIN    , 10., ELECTRON, -21., 250., 0.1, 2000., ElecTop
    USRBIN    , -250., -0.1, -2000., 400., 1., 400.,  &
    USRBIN    , 10., POSITRON, -22., 250., 0.1, 2000., PosTop
    USRBIN    , -250., -0.1, -2000., 400., 1., 400.,  &
    USRBIN    , 10., PHOTON, -23., 250., 0.1, 2000., PhotTop
    USRBIN    , -250., -0.1, -2000., 400., 1., 400.,  &
    RANDOMIZ  , 1.
    START     , 1000.
    STOP
    END
"""

from . import material as _material
from .directive import RecursiveRotoTranslation, Transform


class Writer:
    """
    Class to write FLUKA input files from a fluka registry object.

    >>> f = Writer()
    >>> f.addDetector(flukaRegObject)
    >>> f.write("model.inp")
    """

    _flukaFFString = (
        "*...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+..."
    )

    def __init__(self):
        pass

    def addDetector(self, flukaRegistry):
        """
        Set the fluka registry and therefore the model for this writer instance.
        """
        self.flukaRegistry = flukaRegistry

    def write(self, fileName):
        """
        Write the output to a given filename. e.g. "model.inp".
        """
        f = open(fileName, "w")

        f.write("FREE\n")

        # actually used rot-defi directives
        rotdefi = {}

        # loop over (init cards)
        for c in self.flukaRegistry.cardDict.keys():
            if (
                c == "TITLE"
                or c == "DEFAULTS"
                or c == "GLOBAL"
                or c == "BEAM"
                or c == "BEAMPOS"
                or c == "BEAMAXES"
                or c == "PHOTONUC"
                or c == "MUPHOTON"
                or c == "PAIRBREM"
                or c == ""
                or len(c) > 8
            ):
                if type(self.flukaRegistry.cardDict[c]) is list:
                    for cc in self.flukaRegistry.cardDict[c]:
                        cardstr = cc.toFreeString()
                        f.write(f"{cardstr}\n")
                else:
                    cardstr = self.flukaRegistry.cardDict[c].toFreeString()

        f.write("GEOBEGIN , , , , , , , COMBNAME\n")
        f.write("    0    0\n")

        # loop over bodies
        for bk in self.flukaRegistry.bodyDict.keys():
            transform = self.flukaRegistry.bodyDict[bk].transform

            if type(transform) is RecursiveRotoTranslation:
                if len(transform) != 0:
                    if transform.flukaFreeString() != "":
                        f.write("$start_transform " + transform.name + "\n")
                        try:
                            rotdefi[transform.name] = transform
                        except KeyError:
                            pass

                f.write(self.flukaRegistry.bodyDict[bk].flukaFreeString() + "\n")

                if len(transform) != 0:
                    if transform.flukaFreeString() != "":
                        f.write("$end_transform\n")
            elif type(transform) is Transform:
                if transform.rotoTranslation:
                    if len(transform.rotoTranslation) != 0:
                        if transform.rotoTranslation.flukaFreeString() != "":
                            f.write("$start_transform " + transform.rotoTranslation.name + "\n")
                            try:
                                rotdefi[transform.rotoTranslation.name] = transform.rotoTranslation
                            except KeyError:
                                pass

                f.write(self.flukaRegistry.bodyDict[bk].flukaFreeString() + "\n")

                if transform.rotoTranslation:
                    if len(transform.rotoTranslation) != 0:
                        if transform.rotoTranslation.flukaFreeString() != "":
                            f.write("$end_transform\n")
        f.write("END\n")

        # loop over regions
        for rk in self.flukaRegistry.regionDict.keys():
            f.write(self.flukaRegistry.regionDict[rk].flukaFreeString())
        f.write("END\n")
        f.write("GEOEND\n")

        # loop over materials
        f.write("FREE\n")

        predefinedNames = _material.predefinedMaterialNames()

        f.write(self._flukaFFString + "\n")

        for mk in self.flukaRegistry.materials.keys():
            # check if material/compound is already defined
            if mk in predefinedNames:
                pass
            else:
                f.write(self.flukaRegistry.materials[mk].flukaFreeString() + "\n")

        # loop over material assignments
        for rk in self.flukaRegistry.regionDict.keys():
            try:
                # print(self.flukaRegistry.assignmas[rk])
                assignmaString = "ASSIGNMA " + self.flukaRegistry.assignmas[rk][0] + " " + rk
                f.write(assignmaString + "\n")

                # now electric field

                # now magnetic field
            except KeyError:
                print("Region does not have an assigned material", rk)

        # loop over magnetic fields

        # loop over rotdefis
        for rotdefi in rotdefi.values():
            rotstr = rotdefi.flukaFreeString()
            f.write(f"{rotstr}\n")

        # loop over (non init cards)
        for c in self.flukaRegistry.cardDict.keys():
            if (
                c != "TITLE"
                and c != "GLOBAL"
                and c != "DEFAULTS"
                and c != "BEAM"
                and c != "BEAMPOS"
                and c != "BEAMAXES"
                and c != ""
            ):
                for card in self.flukaRegistry.cardDict[c]:
                    cardstr = card.toFreeString()
                    f.write(f"{cardstr}\n")

        # Close file (TODO use with)
        # f.write("END\n")
        f.close()
