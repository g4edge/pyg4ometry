import re as _re
import pyg4ometry.geant4
import Body as _body
from FlukaRegistry import *
from BodyTransform import *
from copy import deepcopy as _dc
from pyg4ometry.flukaNew.Region import RegionEvaluator as _RegionEval


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
        self.flukaRegistry = FlukaRegistry()
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
        sline = line.split()
        trans_type = sline[0].split("_")[1]
        transcount = len(self.flukaRegistry.bodyTransformDict)
        name = "bodytransform_{}".format(transcount+1)
        value = _freeform_split(line)[1:]
        trans = BodyTransform(name, trans_type, value, self.flukaRegistry)

        return trans

    def parseBodies(self) :
        bodies_block = self.fileLines[self.geobegin+2:self.bodiesend]

        # keep a dict of acitve transforms
        transforms = {"expansion" : 1,
                      "translat" : [0,0,0],
                      "transform" : None} # rot-defi

        description = "" # for accumulating multi-line information
        for i, line in enumerate(bodies_block):
            sline = _freeform_split(line)
            print line

            previous_transforms  = _dc(transforms)
            previous_description = _dc(description)
            terminate_body = True

            if sline[0].startswith("$"): # Transfrom manipulation
                description = ""         # No body info here
                if "start" in sline[0].lower():
                    trans_type = sline[0].split("_")[1]
                    trans = self.parseBodyTransform(line)
                    transforms[trans_type] = trans
                elif "end" in sline[0].lower():
                    trans_type = sline[0].split("_")[1]
                    transforms[trans_type] = None
            elif hasattr(self, sline[0]): # New body defintion
                description = line
            else:
                description += line
                terminate_body = False

            if previous_description and terminate_body:
                name = _freeform_split(previous_description)[0]
                body_parser = getattr(self, "parse{}".format(name.capitalize()))
                body = body_parser(previous_description, previous_transforms)
                body.geant4_solid(self.registry)


    def parseRpp(self, description, transforms) :
        par = _freeform_split(description) # parameters
        body = _body.RPP(par[1],
                         float(par[2]), float(par[3]),
                         float(par[4]), float(par[5]),
                         float(par[6]), float(par[7]),
                         expansion = transforms["expansion"],
                         translation = transforms["translat"],
                         rotdefi = transforms["transform"],
                         flukaregistry = self.flukaRegistry)

        return body

    def parseBox(self, lstart) : 
        pass

    def parseSph(self, lstart) :
        pass 

    def parseRcc(self, lstart) : 
        pass

    def parseRec(self, lstart) :
        pass 

    def parseTrc(self, lstart) : 
        pass

    def parseEll(self, lstart) : 
        pass

    def parseWed(self, lstart) : 
        pass
    
    def parseRaw(self, lstart) : 
        pass
    
    def parseArb(self, lstart) : 
        pass

    def parseXyp(self, lstart) :
        pass
    
    def parseZxp(self, lstart) :
        pass
        
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

    
