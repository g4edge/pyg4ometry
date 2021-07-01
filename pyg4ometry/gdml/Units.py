import numpy as _np

units = {
    # Length units
    "nm" : 1.0e-6,
    "um" : 1.0e-3,
    "mm" : 1.0,
    "cm" : 1.0e1,
    "m"  : 1.0e3,
    "km" : 1.0e6,

    # Angle units
    "deg" : _np.pi/180.0,
    "degree" : _np.pi/180.0,
    "rad" : 1.0,
    "radian" : 1.0,
    "mrad": 1.0e-3,
    "urad": 1.0e-6,

    # Energy units
    "eV" : 1.e-3,
    
    # Other
    "none" : 1.0,
    }

def unit(unitString) :
    return units.get(unitString, None)
