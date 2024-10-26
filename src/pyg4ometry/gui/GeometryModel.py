from .. import geant4 as _g4
from .. import gdml as _gdml
from .. import stl as _stl
from .. import freecad as _freecad
from .. import fluka as _fluka
from .. import visualisation as _vis

import os.path


def extensionFromPath(fileName):
    return os.path.splitext(fileName)[1].split(".")[1].lower()


def nameFromPath(fileName):
    return os.path.splitext(fileName)[0].split("/")[-1]


class GeometryModel:
    def __init__(self):
        self.registryDict = {}
        self.worldLogicalDict = {}
        self.vtkDict = {}

    def createNewRegistry(self, name, type):
        reg = _g4.Registry()
        self.registryDict[name] = reg

    def loadNewRegistry(self, fileName):
        name = nameFromPath(fileName)
        type = extensionFromPath(fileName)

        if type == "gdml":
            r = _gdml.Reader(fileName)
            self.registryDict[name] = r.getRegistry()
            self.worldLogicalDict[name] = self.registryDict[name].getWorldVolume()
        elif type == "step" or type == "stp":
            r = _freecad.Reader(fileName)
            r.relabelModel()
            r.convertFlat()
            self.registryDict[name] = r.getRegistry()
            self.worldLogicalDict[name] = self.registryDict[name].getWorldVolume()
        elif type == "stl":
            r = _stl.Reader(fileName)
            reg = _g4.Registry()
            log = r.logicalVolume(name, "G4_Galactic", reg)
            self.registryDict[name] = reg
            self.worldLogicalDict[name] = log
        elif type == "inp":
            r = _luka.Reader(fileName)
        elif type == "py":
            # load and execute python to create registry
            pass

        v = _vis.VtkViewer()
        l = self.worldLogicalDict[name]
        v.addLogicalVolume(l)
        self.vtkDict[name] = v

        return name
