"""
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

from pyg4ometry.fluka import material as _material

class Writer:
    _flukaFFString = "*...+....1....+....2....+....3....+....4....+....5....+....6....+....7....+..."
    def __init__(self):
        pass

    def addDetector(self, flukaRegistry):
        self.flukaRegistry = flukaRegistry

    def write(self, fileName):
        f = open(fileName,"w")

        # actually used rot-defi directives
        rotdefi = {}

        ###########################################
        # loop over (init cards)
        ###########################################
        for c in self.flukaRegistry.cardDict.keys() :
            if c == "TITLE" or c == "DEFAULTS" or c == "BEAMPOS" :
                cardstr = self.flukaRegistry.cardDict[c].toFreeString()
                f.write(f"{cardstr}\n")

        f.write("GEOBEGIN                                                              COMBNAME\n")
        f.write("    0    0                                                                    \n")

        ###########################################
        # loop over bodies
        ###########################################
        for bk in self.flukaRegistry.bodyDict.keys() :
            #f.write("$Start_translat {} {} {}\n".format(self.flukaRegistry.bodyDict[bk].translation[0],
            #                                            self.flukaRegistry.bodyDict[bk].translation[1],
            #                                            self.flukaRegistry.bodyDict[bk].translation[2]))
            transform = self.flukaRegistry.bodyDict[bk].transform


            if len(transform) != 0 :
                if transform.flukaFreeString() != '' :
                    f.write("$start_transform "+transform.name+"\n")
                    try :
                        rotdefi[transform.name] = transform
                    except KeyError :
                        pass

            f.write(self.flukaRegistry.bodyDict[bk].flukaFreeString()+"\n")

            if len(transform) != 0 :
                if transform.flukaFreeString() != '' :
                    f.write("$end_transform\n")
        f.write("END\n")

        ###########################################
        # loop over regions
        ###########################################
        for rk in self.flukaRegistry.regionDict.keys() :
            f.write(self.flukaRegistry.regionDict[rk].flukaFreeString())
        f.write("END\n")
        f.write("GEOEND\n")

        ###########################################
        # loop over materials
        ###########################################
        f.write("FREE\n")

        predefinedNames = _material.predefinedMaterialNames()

        f.write(self._flukaFFString + "\n")

        for mk in self.flukaRegistry.materials.keys() :
            # check if material/compound is already defined
            if mk in predefinedNames :
                pass
            else :
                f.write(self.flukaRegistry.materials[mk].flukaFreeString()+"\n")

        ###########################################
        # loop over material assignments
        ###########################################
        for rk in self.flukaRegistry.regionDict.keys() :
            try :
                # print(self.flukaRegistry.assignmas[rk])
                assignmaString = "ASSIGNMA "+self.flukaRegistry.assignmas[rk]+" "+rk
                f.write(assignmaString+"\n")
            except KeyError :
                print("Region does not have an assigned material",rk)

        ###########################################
        # loop over rotdefis
        ###########################################
        for rotdefi in rotdefi.values():
            rotstr = rotdefi.flukaFreeString()
            f.write(f"{rotstr}\n")

        ###########################################
        # loop over (non init cards)
        ###########################################
        for c in self.flukaRegistry.cardDict.keys() :
            if c != "TITLE" or c != "DEFAULTS" or c != "BEAMPOS" :
                for card in self.flukaRegistry.cardDict[c] :
                    cardstr = card.toFreeString()
                    f.write(f"{cardstr}\n")

        ###########################################
        # Close file (TODO use with)
        ###########################################
        f.write("END\n")
        f.close()