import configparser as _configparser
import random as _random
import pkg_resources as _pkg_resources

def randomColour():
    """Return random RGB tuple"""
    return (_random.randint(0, 255), _random.randint(0, 255), _random.randint(0, 255))

def hexRGBToRGBTriplet(value):
    hexes = [value[:2], value[2:4], value[4:]]
    return [int(h, 16) / 255 for h in hexes]

class VisualisationOptions:
    """
    Basic holder for visualisation parameters, i.e. colour and opacity.
    Construct an instance then modify members.
    """
    def __init__(self):
        self.representation = "surface"
        self.colour         = [0.5,0.5,0.5]
        self.alpha          = 0.5
        self.visible        = True
        self.lineWidth      = 1
        self.randomColour   = False

    def __repr__(self):
        rgba= [*self.getColour(), self.alpha]
        return (f"<VisOpt: rep={self.representation}, rgba={rgba}, "
                f"vis={self.visible}, linewidth={self.lineWidth}>")

    def getColour(self):
        """
        Return the colour and generate a random colour if flagged.
        """
        return self._generateRandomColour() if self.randomColour else self.colour

    def _generateRandomColour(self):
        aColour = [x/255 for x in randomColour()]
        return aColour


def loadPredefined():
    """
    Construct a ColorMap initialised with default colours for various materials.
    """
    config = _configparser.ConfigParser(allow_no_value=True, interpolation=_configparser.ExtendedInterpolation())
    config.optionxform = str

    ini = _pkg_resources.resource_filename(__name__, "colours.ini")
    with open(ini, "r") as f:
        config.read_file(f)

    colourAlpha = {}
    alphas = config["alpha"]
    sections = [config[s] for s in ["geant4", "bdsim", "fluka"]]
    for section in sections:
        for name in section:
            hexrgb = section.get(name, None)

            if hexrgb is None:
                continue
            alpha = float(alphas.get(name, 1))
            colourAlpha[name] = (*hexRGBToRGBTriplet(hexrgb), alpha)

    result = {}
    for k,v in colourAlpha.items():
        vi = VisualisationOptions()
        vi.colour = v[:3]
        vi.alpha  = v[3]
        result[k] = vi
    return result

predefinedMaterialVisOptions = loadPredefined()




# this can be deprecated
def makeVisualisationOptionsDictFromMaterials(materials):

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
            matVisDict[material].colour = [_random.random(),_random.random(),_random.random()]
    return matVisDict




