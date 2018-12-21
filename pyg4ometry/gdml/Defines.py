from ..geant4 import Expression as _Expression
from matplotlib.cbook import is_numlike


def expressionString(obj1,obj2) : 
    # nubmer/
    if is_numlike(obj2) :
        return str(obj2)
    try :
        obj1.registry.defineDict[obj2.name]
        return obj2.name
    except KeyError : 
        return obj2.expr.expression

class ScalarBase(object) :
    def __init__(self) : 
        pass

    def __add__(self, other) :
                
        v1 = expressionString(self,self)
        v2 = expressionString(self,other)

        v = Constant("var_{}_add_{}".format(v1,v2), '({}) + ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v


    def __sub__(self, other) :
        v1 = expressionString(self,self)
        v2 = expressionString(self,other)

        v = Constant("var_{}_sub_{}".format(v1,v2), '({}) - ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __mul__(self, other):
        v1 = expressionString(self,self)
        v2 = expressionString(self,other)

        v = Constant("var_{}_mul_{}".format(v1,v2), '({}) * ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __div__(self, other):
        v1 = expressionString(self,self)
        v2 = expressionString(self,other)

        v = Constant("var_{}_div_{}".format(v1,v2), '({}) / ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __neg__(self):
        v1 = expressionString(self,self)

        v = Constant("var_neg_{}".format(v1), '(-{})'.format(v1),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__

    def setName(self, name) : 
        self.name          = name
        self.expr.name     = 'expr_{}'.format(name)
        self.expr.registry = self.registry
        self.registry.addDefine(self)

def sin(arg) : 
    v1 = expressionString(arg,arg)
    v = Constant("sin_{}".format(v1), 'sin({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def cos(arg) : 
    v1 = expressionString(arg,arg)
    v = Constant("cos_{}".format(v1), 'cos({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def tan(arg) : 
    v1 = expressionString(arg,arg)
    v = Constant("tan_{}".format(v1), 'tan({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def exp(arg) : 
    v1 = expressionString(arg,arg)
    v = Constant("exp_{}".format(v1), 'exp({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def log(arg) : 
    v1 = expressionString(arg,arg)
    v = Constant("log_{}".format(v1), 'log({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def log10(arg) : 
    v1 = expressionString(arg,arg)
    v = Constant("log10_{}".format(v1), 'log10({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

class Constant(ScalarBase) :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr = _Expression("expr_{}".format(name), str(value), registry=registry)

        if registry != None: 
            self.registry = registry
            registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()
    
    def __repr__(self) :
        return "Constant : {} = {}".format(self.name, str(self.expr))

class Quantity(ScalarBase) :
    def __init__(self, name, value, unit, type, registry = None) :
        self.name  = name
        self.expr  = _Expression("expr_{}".format(name), str(value), registry=registry)
        self.unit  = unit
        self.type  = type

        if registry != None: 
            self.registry = registry
            registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Quantity: {} = {} [{}] {}".format(self.name, str(self.expr), self.unit, self.type)

class Variable(ScalarBase) :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr  = _Expression("expr_{}".format(name), str(value), registry=registry)

        if registry != None: 
            self.registry = registry
            registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Variable: {} = {}".format(self.name, str(self.expr))

class Position :
    def __init__(self,name,x,y,z, registry = None) :
        self.name = name
        self.x = _Expression("expr_{}_pos_x".format(name), str(x), registry=registry)
        self.y = _Expression("expr_{}_pos_y".format(name), str(y), registry=registry)
        self.z = _Expression("expr_{}_pos_z".format(name), str(z), registry=registry)
        
        if registry != None: 
            self.registry = registry
            registry.addDefine(self)

    def eval(self) :
        return [self.x.eval(), self.y.eval(), self.z.eval()]

    def __repr__(self) :
        return "Position : {} = [{} {} {}]".format(self.name, str(self.x), str(self.y), str(self.z))

    def __getitem__(self, key):
        if key == 0 : 
            return self.x
        elif  key == 1 : 
            return self.y 
        elif  key == 2 :
            return self.z
        else :
            raise IndexError
        
class Rotation : 
    def __init__(self,name,rx,ry,rz, registry = None) :
        self.name = name
        self.rx = _Expression("expr_{}_rot_x".format(name), str(rx), registry=registry)
        self.ry = _Expression("expr_{}_rot_y".format(name), str(ry), registry=registry)
        self.rz = _Expression("expr_{}_rot_z".format(name), str(rz), registry=registry)

        if registry != None : 
            self.registry = registry
            registry.addDefine(self)

    def eval(self) :
        return [self.rx.eval(), self.ry.eval(), self.rz.eval()]

    def __repr__(self) :
        return "Rotation : {} = [{} {} {}]".format(self.name, str(self.rx), str(self.ry), str(self.rz))

    def __getitem__(self, key):
        if key == 0 : 
            return self.rx
        elif  key == 1 : 
            return self.ry 
        elif  key == 2 :
            return self.rz
        else :
            raise IndexError

class Scale : 
    def __init__(self,name,sx,sy,sz, registry = None) :
        self.name = name
        self.sx = _Expression("expr_{}_scl_x".format(name), str(sx), registry=registry)
        self.sy = _Expression("expr_{}_scl_x".format(name), str(sy), registry=registry)
        self.sz = _Expression("expr_{}_scl_x".format(name), str(sz), registry=registry)

        if registry != None: 
            self.registry = registry
            registry.addDefine(self)        

    def eval(self) :
        return [self.sx.eval(), self.sy.eval(), self.sz.eval()]

    def __repr__(self) :
        return "Scale : {} = [{} {} {}]".format(self.name, str(self.sx), str(self.sy), str(self.sz))

    def __getitem__(self, key):
        if key == 0 : 
            return self.sx
        elif  key == 1 : 
            return self.sy 
        elif  key == 2 :
            return self.sz
        else :
            raise IndexError

class Matrix :
    def __init__(self,name, coldim, values, registry = None) :
        self.name = name
        self.coldim = coldim

        self.values = [] 
        for v in values :
            self.values.append(_Expression("expr_{}_idx{}_val".format(name,values.index(v)), v,registry=registry))                         

        if registry != None:
            self.registry = registry
            registry.addDefine(self)

    def eval(self) :
        return [ e.eval() for e in self.values ]

    def __repr__(self) :
        return "Matrix : {} = {} {}".format(self.name, str(self.coldim), str(self.values))

    def __getitem__(self, key):
        if key < len(self.values) :
            return self.values[key]
        else :
            raise IndexError

