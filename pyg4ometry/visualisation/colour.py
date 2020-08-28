import configparser
from collections.abc import MutableMapping
from random import randint
import pkg_resources

class RGBAHexFormatError(Exception): pass

def randomColour():
    """Return random RGB tuple"""
    return (randint(0, 255), randint(0, 255), randint(0, 255))

def hexRGBAToRGBAQuad(value):
    """Read a RGBA hex quadtruplet of numbers (e.g. 91BBFFAA) and convert to
    fractions"""
    hexes = [value[:2], value[2:4], value[4:6], value[6:]]
    try:
        return [int(h, 16) / 255 for h in hexes]
    except ValueError:
        raise RGBAHexFormatError(value)

class ColourMap(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._map = dict(*args, **kwargs)

    @classmethod
    def fromPredefined(cls):
        """Construct a ColorMap initialised with default colours for various
        materials."""
        config = configparser.ConfigParser(
            allow_no_value=True,
            interpolation=configparser.ExtendedInterpolation())
        config.optionxform = str

        ini = pkg_resources.resource_filename(__name__, "colours.ini")
        with open(ini, "r") as f:
            config.read_file(f)

        result = cls()
        alphas = config["alpha"]
        sections = [config[s] for s in ["geant4", "bdsim", "fluka"]]
        for section in sections:
            for name in section:
                hexrgb = section.get(name, None)

                if hexrgb is None:
                    continue
                alpha = float(alphas.get(name, 1))
                result[name] = (*hexRGBToRGBTriplet(hexrgb), alpha)

        return result
        
    def __getitem__(self, key):
        return self._map[key]

    def __setitem__(self, key, value):
        self._map[key] = value

    def __delitem__(self, key):
        del self._map[key]

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

    def __repr__(self):
        return repr(self._map)
        

