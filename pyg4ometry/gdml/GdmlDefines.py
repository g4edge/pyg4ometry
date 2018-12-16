from Parameter import Parameter as _Parameter
from Registry import registry as _registry
from ..geant4 import Expression as _Expression

class Constant :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr = _Expression(value, registry=registry)

        registry.addDefine(self)

    def __float__(self) :
        return self.expr.eval()
    
    def __repr__(self) :
        return "Constant : {} = {}".format(self.name, str(self.expr))

class Quantity :
    def __init__(self, name, value, unit, type, registry = None) :
        self.name  = name
        self.expr  = _Expression(value, registry=registry)
        self.unit  = unit
        self.type  = type

        registry.addDefine(self)

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Quantity: {} = {} [{}] {}".format(self.name, str(self.expr), self.unit, self.type)

class Variable :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr  = _Expression(value, registry=registry)

        registry.addDefine(self)

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Variable: {} = {}".format(self.name, str(self.expr))

#class Expression : 
#    def __init__(self, name, value, registry = None) : 
#        self.name = name
#       self.expr = _Expression(value, registry=registry)
#
#        _registry.addDefine(self)
#
#    def __float__(self) :
#        return self.expr.eval()
#
#    def __repr__(self) :
#        return "Expression : {} = {}".format(self.expr, self.value)

class Position :
    def __init__(self,name,x,y,z, registry = None) :
        self.name = name
        self.x = _Expression(x, registry=registry)
        self.y = _Expression(y, registry=registry)
        self.z = _Expression(z, registry=registry)
        
        registry.addDefine(self)

    def __repr__(self) :
        return "Position : {} = [{} {} {}]".format(self.name, str(self.x), str(self.y), str(self.z))
        
class Rotation : 
    def __init__(self,name,rx,ry,rz, registry = None) :
        self.name = name
        self.rx = _Expression(rx, registry=registry)
        self.ry = _Expression(ry, registry=registry)
        self.rz = _Expression(rz, registry=registry)

        registry.addDefine(self)

    def __repr__(self) :
        return "Rotation : {} = [{} {} {}]".format(self.name, str(self.rx), str(self.ry), str(self.rz))

class Scale : 
    def __init__(self,name,sx,sy,sz, registry = None) :
        self.name = name
        self.sx = _Expression(sx, registry=registry)
        self.sy = _Expression(sy, registry=registry)
        self.sz = _Expression(sz, registry=registry)

        registry.addDefine(self)        

    def __repr__(self) :
        return "Scale : {} = [{} {} {}]".format(self.name, str(self.sx), str(self.sy), str(self.sz))

class Matrix :
    def __init__(self,name, coldim, values, registry = None) :
        self.name = name
        self.coldim = coldim
        self.values = values 

        print self.name, self.coldim, self.values

        registry.addDefine(self)

    def __repr__(self) :
        return "Matrix : {} = {} {}".format(self.name, str(self.coldim), str(self.values))
