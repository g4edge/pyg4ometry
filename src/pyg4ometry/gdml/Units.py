import numpy as _np

units = {
    # Length units
    "nm": 1.0e-6,
    "um": 1.0e-3,
    "mm": 1.0,
    "cm": 1.0e1,
    "m": 1.0e3,
    "km": 1.0e6,
    # Angle units
    "deg": _np.pi / 180.0,
    "degree": _np.pi / 180.0,
    "rad": 1.0,
    "radian": 1.0,
    "mrad": 1.0e-3,
    "urad": 1.0e-6,
    # Energy units
    "eV": 1.0e-3,
    "keV": 1,
    "MeV": 1.0e3,
    "GeV": 1.0e6,
    # Other
    "none": 1.0,
    # Time units
    "ns": 1.0e-9,
    "us": 1.0e-6,
    "ms": 1.0e-3,
    "s": 1.0,
    "in": 25.4,
    "kg": 1000.0,
}


def unit(unitString):
    return units.get(unitString, None)
