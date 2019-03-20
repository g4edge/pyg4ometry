import numpy as _np

nm = 1.0e-6
um = 1.0e-3
mm = 1.0
m  = 1.0e3
km = 1.0e6

deg = _np.pi/180.0
rad = 1.0

def lunit(unitString) : 
    if unitString == "nm" :
        return nm
    elif unitString == "um" : 
        return um 
    elif unitString == "mm" : 
        return mm
    elif unitString == "m" : 
        return m
    elif unitString == "km" :
        return km
    else : 
        return None

def aunit(unitString) : 
    if unitString == "deg" : 
        return deg
    elif unitString == "rad" : 
        return rad
    else :
        return None 

def unit(unitString) : 
    lu = lunit(unitString)
    au = aunit(unitString)
    if lu : 
        return lu
    if au :
        return au

    if unitString == "none" : 
        return 1.0
