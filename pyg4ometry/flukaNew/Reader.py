import re as _re
import pyg4ometry.geant4
import Body as _body
from FlukaRegistry import *
from BodyTransform import *
from copy import deepcopy as _dc
from pyg4ometry.flukaNew.Region import RegionEvaluator as _RegionEval

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
        # find geo(begin/end) lines 
        for l,i in zip(self.fileLines,range(0,len(self.fileLines))) : 
            if l.find("GEOBEGIN") != -1 : 
                self.geobegin = i 
            if l.find("GEOEND") != -1 : 
                self.geoend = i
     
        # find the line numbers for geometry
        first = True
        for l,i in zip(self.fileLines[self.geobegin:self.geoend+1],
                       range(self.geobegin,self.geoend+1)) :
            if l.find("END") != -1 and first : 
                self.bodiesend = i
                first = False
            elif l.find("END") != -1 and l.find("GEOEND") == -1: 
                self.regionsend = i
        
        print self.geobegin, self.fileLines[self.geobegin] 
        print self.bodiesend, self.fileLines[self.bodiesend]
        print self.regionsend, self.fileLines[self.regionsend] 
        print self.geoend,self.fileLines[self.geoend]
        
    def parseBodies(self) :
        pass

    def parseRpp(self, lstart) :
        pass

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
        pass

    def parseMaterials(self) :
        pass

    def parseMaterialAssignment(self) : 
        pass

    def parseCards(self) :
        pass

    def parseLattice(self) :
        pass

    
