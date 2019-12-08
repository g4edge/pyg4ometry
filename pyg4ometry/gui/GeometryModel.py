import pyg4ometry.geant4
import pyg4ometry.gdml
import pyg4ometry.stl
import pyg4ometry.freecad
import pyg4ometry.fluka

import os.path

def extensionFromPath(fileName) :
    return os.path.splitext(fileName)[1].split(".")[1]

def nameFromPath(fileName) :
    return os.path.splitext(fileName)[0].split("/")[-1]

class GeometryModel :
    def __init__(self):
        self.registryDict    = {}
        self.worldVolumeDict = {}

    def createNewRegistry(self, name, type):
        reg = pyg4ometry.geant4.Registry()
        self.registryDict[name] = reg

    def loadNewRegistry(self, fileName):

        name = nameFromPath(fileName)
        type = extensionFromPath(fileName)

        if type == "gdml" :
            r = pyg4ometry.gdml.Reader(fileName)
            self.registryDict[name] = r.getRegistry()
        elif type == "step" :
            r = pyg4ometry.freecad.Reader(fileName)
            r.relabelModel()
            r.convertFlat()
            self.registyDict[name] = r.getRegistry()
        elif type == "stl" :
            r = pyg4ometry.stl.Reader(fileName)
            reg = pyg4ometry.geant4.Registry()
            l = r.logicalVolume(name,"G4_Galactic",reg)
            self.registryDict[name] = reg
        elif type == "inp" :
            r = pyg4ometry.fluka.Reader(fileName)
