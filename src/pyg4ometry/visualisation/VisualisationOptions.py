import configparser as _configparser
import random as _random

# instance of vis options loaded lazily as needed for faster import times
_predefinedMaterialVisOptions = None


def randomColour():
    """Return random RGB tuple"""
    return (_random.randint(0, 255), _random.randint(0, 255), _random.randint(0, 255))


def hexRGBToRGBTriplet(value):
    hexes = [value[:2], value[2:4], value[4:]]
    return [int(h, 16) / 255 for h in hexes]


# Vtk
#   ambientColour, coatColour, diffuseColour, specularColour
#   anisotropy, anisotropyRotation, anisotropyTexture
#   coatIOR, coatNormalScale, coatNormalTexture, coatRoughness, coatStrength
#   emissiveFactor, emissiveTesxture
#   metallic
#   normalScale, normalTexture
#   ORMTexture??
#   roughness
#   specularPower
#   texture


class VisualisationOptions:
    """
    Basic holder for visualisation parameters, i.e. colour and opacity.
    Construct an instance then modify members.
    """

    def __init__(
        self,
        representation="surface",
        colour=[0.5, 0.5, 0.5],
        alpha=0.5,
        visible=True,
        lineWidth=1,
        randomColour=False,
        depth=0,
    ):
        self.representation = representation
        self.colour = colour
        self.alpha = alpha
        self.visible = visible
        self.lineWidth = lineWidth
        self.randomColour = randomColour
        self.depth = depth

        # vis options for pbr shaders
        self.usdOptions = UsdPreviewSurfaceOptions()
        self.usdOptions.diffuseColor = colour
        self.usdOptions.opacity = alpha

    def __repr__(self):
        rgba = [*self.getColour(), self.alpha]
        return (
            f"<VisOpt: rep={self.representation}, rgba={rgba}, "
            f"vis={self.visible}, linewidth={self.lineWidth}, depth={self.depth}>"
        )

    def getColour(self):
        """
        Return the colour and generate a random colour if flagged.
        """
        return self._generateRandomColour() if self.randomColour else self.colour

    def _generateRandomColour(self):
        aColour = [x / 255 for x in randomColour()]
        return aColour


def loadPredefined():
    """
    Construct a ColorMap initialised with default colours for various materials.

    Lods from package resource files.
    """
    import importlib_resources

    config = _configparser.ConfigParser(
        allow_no_value=True, interpolation=_configparser.ExtendedInterpolation()
    )
    config.optionxform = str

    ini = importlib_resources.files("pyg4ometry") / "visualisation/colours.ini"

    with open(ini) as f:
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
    for k, v in colourAlpha.items():
        vi = VisualisationOptions()
        vi.colour = v[:3]
        vi.alpha = v[3]
        result[k] = vi
    return result


def getPredefinedMaterialVisOptions():
    global _predefinedMaterialVisOptions
    if _predefinedMaterialVisOptions is None:
        _predefinedMaterialVisOptions = loadPredefined()
    return _predefinedMaterialVisOptions


def makeVisualisationOptionsDictFromPredefined(ColourMap):
    for material in ColourMap.keys():
        if material.lower().find("galactic") != -1:
            ColourMap[material].visible = False
        elif material.lower().find("air") != -1:
            ColourMap[material].visible = False
        elif material.lower().find("vacuum") != -1:
            ColourMap[material].visible = False

    return ColourMap


class UsdPreviewSurfaceOptions:
    """
    Usd preview shader options
    """

    def __init__(self):
        self.diffuseColor = [1, 0.0, 0.0]
        self.emissiveColor = [0, 0, 0.0]
        self.useSpecularWorkflow = 0
        self.specularColor = [0.5, 0.5, 0.5]
        self.metallic = 0.0
        self.roughness = 1.0
        self.clearcoat = 0.0
        self.clearcoatRoughness = 0.0
        self.opacity = 1.0
        self.opacityThreshold = 0.0
        self.ior = 1.5
        self.normal = [0, 0, 1]
        self.displacement = 0.0
        self.occlusion = 1.0
