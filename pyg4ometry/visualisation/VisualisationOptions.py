import random as _random
from .colour import randomColour

class VisualisationOptions:
    def __init__(self) : 
        self.representation = "surface"
        self.color          = [0.5,0.5,0.5]
        self.alpha          = 0.5
        self.visible        = True
        self.lineWidth      = 1 

    def __repr__(self):
        s = self
        rgba= [*self.color, self.alpha]
        return (f"<VisOpt: rep={self.representation}, rgba={rgba}, "
                f"vis={self.visible}, linewidth={self.lineWidth}>")

    @classmethod
    def withRandomColour(cls):
        vopt = cls()
        vopt.color = [x/255 for x in randomColour()]
        vopt.alpha = 0.0
        return vopt

def makeVisualisationOptionsDictFromMaterials(materials) :

    matVisDict = {}

    for material in materials :
        # strip pointer from name

        if material.find("0x") != -1 :
            materialStrip = material[0:material.find("0x")]
        else :
            materialStrip = material

        matVisDict[material] = VisualisationOptions()

        if materialStrip.lower().find("galactic") != -1 :
            matVisDict[material].visible = False

        elif materialStrip.lower().find("air") != -1 :
            matVisDict[material].visible = False

        elif materialStrip.lower().find("vacuum") != -1 :
            matVisDict[material].visible = False

        else :
            matVisDict[material].color = [_random.random(),_random.random(),_random.random()]
    return matVisDict

def makeVisualisationOptionsDictFromPredefined(ColourMap):

    matVisDict = {}

    for material in ColourMap.keys() :
        # strip pointer from name

        matVisDict[material] = VisualisationOptions()

        if material.lower().find("galactic") != -1 :
            matVisDict[material].visible = False

        elif material.lower().find("air") != -1 :
            matVisDict[material].visible = False

        elif material.lower().find("vacuum") != -1 :
            matVisDict[material].visible = False

        else :
            MaterialColor = ColourMap[material]
            matVisDict[material].color = [MaterialColor[0],MaterialColor[1],MaterialColor[2]]
            matVisDict[material].alpha = MaterialColor[3]

    return matVisDict


