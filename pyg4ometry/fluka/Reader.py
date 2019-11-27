import sys
import re as _re
import pyg4ometry.geant4
import Body as _body
from FlukaRegistry import *
from BodyTransform import *
from copy import deepcopy as _dc
from pyg4ometry.fluka.RegionExpression import RegionEvaluator as _RegionEval


_BODY_NAMES = {"RPP",
               "BOX",
               "SPH",
               "RCC",
               "REC",
               "TRC",
               "ELL",
               "WED", "RAW",
               "ARB ",
               "XYP", "XZP", "YZP",
               "PLA",
               "XCC", "YCC", "ZCC",
               "XEC", "YEC", "ZEC",
               "QUA"}

def _freeform_split(string):
    """Method to split a string in FLUKA FREE format into its components"""
    # Split the string along non-black separators [,;:/\]
    partial_split = _re.split(';|,|\\/|:|\\\|\n', r"{}".format(string))

    # Populate zeros between consequtive non-blank separators as per the FLUKA manual
    is_blank  = lambda s : not set(s) or set(s) == {" "}
    noblanks_split = [chunk if not is_blank(chunk) else '0.0' for chunk in partial_split]

    # Split along whitespaces now for complete result
    components = []
    for chunk in noblanks_split:
        components += chunk.split()

    return components

class Reader(object):
    def __init__(self, filename) :
        self.fileName = filename
        self.flukaregistry = FlukaRegistry()
        self.registry = pyg4ometry.geant4.Registry()
        self.load()

    def load(self) :

        # read file
        flukaFile = open(self.fileName)
        self.fileLines = flukaFile.readlines()
        flukaFile.close()

        # strip comments
        fileLinesStripped = []
        for l in self.fileLines :
            fileLineStripped = l.lstrip()

            # if there is nothing on  the line
            if len(fileLineStripped) == 0 :
                continue
            # skip comment
            if fileLineStripped[0] != '*' : 
                fileLinesStripped.append(l.rstrip())
        self.fileLines = fileLinesStripped

        # parse file
        self.findLines()
        self.parseBodies()
        self.parseRegions()
        self.parseMaterials()
        self.parseMaterialAssignment()
        self.parseLattice()
        self.parseCards()

    def findLines(self) :
        # find geo(begin/end) lines and bodies/region ends
        firstEND = True
        for i, line in enumerate(self.fileLines) :
            if "GEOBEGIN" in line:
                self.geobegin = i
            elif "GEOEND" in line:
                self.geoend = i
            elif "END" in line:
                if firstEND:
                    self.bodiesend = i
                    firstEND = False
                else:
                    self.regionsend = i

        print self.geobegin, self.fileLines[self.geobegin]
        print self.bodiesend, self.fileLines[self.bodiesend]
        print self.regionsend, self.fileLines[self.regionsend]
        print self.geoend,self.fileLines[self.geoend]

    def parseBodyTransform(self, line):
        sline = _freeform_split(line)
        trans_type = sline[0].split("_")[1]
        transcount = len(self.flukaregistry.bodyTransformDict)
        name = "bodytransform_{}".format(transcount+1)
        value = sline[1:]
        trans = BodyTransform(name, trans_type, value, self.flukaregistry)

        return trans

    def parseBodies(self) :
        bodies_block = self.fileLines[self.geobegin+2:self.bodiesend+1]

        # keep a dict of acitve transforms
        transforms = {"expansion": 1,
                      "translat": [0,0,0],
                      "transform": None} # rot-defi

        description = "" # for accumulating multi-line information
        for i, line in enumerate(bodies_block):
            sline = _freeform_split(line)
            print line

            previous_transforms  = _dc(transforms)
            previous_description = _dc(description)
            terminate_body = True

            if sline[0] == "END":
                descripion = ""
            elif sline[0].startswith("$"): # Transfrom manipulation
                description = ""         # No body info here
                if "start" in sline[0].lower():
                    trans_type = sline[0].split("_")[1]
                    trans = self.parseBodyTransform(line)
                    transforms[trans_type] = trans
                elif "end" in sline[0].lower():
                    trans_type = sline[0].split("_")[1]
                    transforms[trans_type] = None
            elif sline[0] in _BODY_NAMES:
                description = line
            else:
                description += line # Continuing body definition
                terminate_body = False

            if previous_description and terminate_body:
                _make_body(previous_description, transforms, self.flukaregistry)

    def parseRegions(self) :
        region_block = self.fileLines[self.bodiesend+1:self.regionsend+1]

        description = "" # for accumulating multi-line information
        for i, line in enumerate(region_block):
            sline = _freeform_split(line)

            previous_description = _dc(description)
            terminate_region = True

            # The opening declaration has an int as the second argument
            if sline[0] == "END" or sline[1].isdigit():
                description = line
            else:
                description += line
                terminate_region = False

            if previous_description and terminate_region:
                parser = _RegionEval()
                boolean_only = "".join(_freeform_split(previous_description)[2:])
                parsed =  parser.parse(boolean_only)
                print "Parsed: ", "".join([p.getText() for p in parsed.children])
                #result = parser.evaluate(parsed, self.flukaRegistry.bodyDict)

    def parseMaterials(self) :
        pass

    def parseMaterialAssignment(self) : 
        pass

    def parseCards(self) :
        pass

    def parseLattice(self) :
        pass


def _make_body(definition, transforms, flukareg):
    # definition is string of the entire definition as written in the file.
    elements = _freeform_split(definition)
    body_type = elements[0]
    name = elements[1]
    param = map(float, elements[2:])

    transforms = {"translation": transforms["translat"],
                  "expansion": transforms["expansion"],
                  "rotdefi" : transforms["rotdefi"]}

    if body_type == "RPP":
        b = _body.RPP(name, *param, flukaregistry=flukareg, **transforms)
    elif body_type == "BOX":
        b = _body.BOX(name, param[0:3], param[3:6], param[6:9],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "ELL":
        b = _body.ELL(name, param[0:3], param[3:6], param[7],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "WED":
        b = _body.WED(name, param[0:3], param[3:6], param[6:9], param[9:12],
                      flukaregistry=flukareg, **transforms)
    elif body_type == "RAW":
        b = _body.RAW(name, param[0:3], param[3:6], param[6:9], param[9:12],
                      flukaregistry=flukareg, **transforms)
    elif body_type == "ARB":
        vertices = [param[0:3], param[3:6], param[6:9], param[9:12],
                    param[12:15], param[15:18], param[18:21], param[21:24]]
        facenumbers = param[24:]
        b = _body.ARB(name, vertices, facenumbers,
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "XYP":
        b = _body.XYP(name, param[0:], flukaregistry=flukareg, **transforms)
    elif body_type == "XZP":
        b = _body.XZP(name, param[0:], flukaregistry=flukareg, **transforms)
    elif body_type == "YZP":
        b = _body.YZP(name, param[0:], flukaregistry=flukareg, **transforms)
    elif body_type == "PLA":
        b = _body.PLA(name, param[0:3], param[3:6], flukaregistry=flukareg,
                      **transforms)
    elif body_type == "XCC":
        b = _body.XCC(name, param[0], param[1], param[2:],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "YCC":
        b = _body.YCC(name, param[0], param[1], param[2:],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "ZCC":
        b = _body.ZCC(name, param[0], param[1], param[2:],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "XEC":
        b = _body.XEC(name, param[0], param[1], param[2], param[3:],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "YEC":
        b = _body.YEC(name, param[0], param[1], param[2], param[3:],
                      flukaregistry=flukareg,
                      **transforms)
    elif body_type == "ZEC":
        b = _body.ZEC(name, param[0], param[1], param[2], param[3:],
                      flukaregistry=flukareg,
                      **transforms)
    else:
        raise TypeError("Body type {} not supported".format(body_type))
    return b


def main(filein):
    r = Reader(filein)

if __name__ == '__main__':
    main(sys.argv[1])
