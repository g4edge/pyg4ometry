import random as _random

class VisualisationOptions(object) :
    
    def __init__(self) : 
        self.representation = "surface"
        self.color          = [0.5,0.5,0.5]
        self.alpha          = 0.5
        self.visible        = True
        self.lineWidth      = 1 

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




