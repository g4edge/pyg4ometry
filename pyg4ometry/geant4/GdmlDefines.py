from Parameter import Parameter as _Parameter
from Registry import registry as _registry
from ..geant4 import Expression as _Expression

class Constant :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.value = value

        registry.addDefine(self)
            
    def __repr__(self) :
        return 'Constant : '+self.name+' '+str(self.value)

class Quantity :
    def __init__(self, name, value, unit, type, registry = None) :
        self.name  = name
        self.expr  = _Expression(value,0)
        self.unit  = unit
        self.type  = type

        registry.addDefine(self)
                        
    def __repr__(self) :
        return 'Quantity : '+self.name+' '+str(self.value)+' '+self.unit+' '+self.type

class Variable :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr  = _Expression(value,0)

        registry.addDefine(self)

    def __repr__(self) :
        return 'Variable : '+self.name+' '+str(self.value)

class Expression : 
    def __init__(self, name, value, registry = None) : 
        self.name = name
        self.value = _Expression(value,0)

        _registry.addDefine(self)

    def __repr__(self) :
        return 'Expression : '+self.name+' '+str(self.value)

class Position :
    def __init__(self,name,x,y,z, registry = None) :
        self.name = name
        self.x = _Expression(x,0)
        self.y = _Expression(y,0)
        self.z = _Expression(z,0)
        
        registry.addDefine(self)

    def __repr__(self) :
        return 'Position : '+self.name+' '+str(self.x)+' '+str(self.y)+' '+str(self.z)
        
class Rotation : 
    def __init__(self,name,rx,ry,rz, registry = None) :
        self.name = name
        self.rx = _Expression(rx,0)
        self.ry = _Expression(ry,0)
        self.rz = _Expression(rz,0)

        registry.addDefine(self)

    def __repr__(self) :
        return 'Rotation : '+self.name+' '+str(self.rx)+' '+str(self.ry)+' '+str(self.rz)

class Scale : 
    def __init__(self,name,sx,sy,sz, registry = None) :
        self.name = name
        self.sx = _Expression(sx,0)
        self.sy = _Expression(sy,0)
        self.sz = _Expression(sz,0)

        registry.addDefine(self)        

    def __repr__(self) :
        return 'Scale : '+self.name+' '+str(self.sx)+' '+str(self.sy)+' '+str(self.sz)

class Matrix :
    def __init__(self,name, coldim, values, registry = None) :
        self.name = name
        self.coldim = coldim
        self.values = values 

        print self.name, self.coldim, self.values

        registry.addDefine(self)

    def __repr__(self) :
        return 'Matrix : '+self.name+' '+str(self.coldim)+' '+str(self.values)
