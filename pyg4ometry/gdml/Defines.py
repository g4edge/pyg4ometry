from pyg4ometry.geant4 import Expression as _Expression
from pyg4ometry.gdml import Units as _Units

from matplotlib.cbook import is_numlike
import numpy as _np

def expressionStringScalar(obj1,obj2) : 
    # nubmer/varible/expression
    if is_numlike(obj2) :                       # number
        return str(obj2)
    try :
        obj1.registry.defineDict[obj2.name]     # variable already defined in registry
        return obj2.name
    except KeyError : 
        return obj2.expr.expression             # just an object as an expression

def upgradeToVector(var, reg, type = "position", addRegistry = False) : 

    # check if already a vector type 
    if isinstance(var,VectorBase) : 
        return var 

    # create appropriate vector type
    if isinstance(var,list) :
        if type == "position" :
            return Position("temp",var[0],var[1],var[2],"mm",reg, addRegistry)
        elif type == "rotation" : 
            return Rotation("temp",var[0],var[1],var[2],"rad",reg, addRegistry)
        elif type == "scale" : 
            return Scale("temp",var[0],var[1],var[2],"none",reg, addRegistry)
        else : 
            print 'type not defined'

def upgradeToTransformation(var, reg, addRegistry = False) : 


    if isinstance(var[0],VectorBase) :
        rot = var[0]
    elif isinstance(var[0],list) :
        rot = upgradeToVector(var[0],reg,"rotation",addRegistry) 

    if isinstance(var[1],VectorBase) :
        tra = var[1] 
    elif isinstance(var[1],list) : 
        tra = upgradeToVector(var[1],reg,"position",addRegistry) 

    return [rot,tra]

class ScalarBase(object) :
    def __init__(self) : 
        pass

    def __add__(self, other) :
                
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)

        v = Constant("var_{}_add_{}".format(v1,v2), '({}) + ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v


    def __sub__(self, other) :
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)

        v = Constant("var_{}_sub_{}".format(v1,v2), '({}) - ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __rsub__(self,other) :
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)        
        
        v = Constant("var_{}_sub_{}".format(v2,v1), '({}) - ({})'.format(v2, v1),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v        


    def __mul__(self, other):
        
        # check to see if other is a vector 
        if isinstance(other,VectorBase) : 
            return other*self

        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)

        v = Constant("var_{}_mul_{}".format(v1,v2), '({}) * ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __div__(self, other):
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)

        v = Constant("var_{}_div_{}".format(v1,v2), '({}) / ({})'.format(v1, v2),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __rdiv__(self, other):
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)

        v = Constant("var_{}_div_{}".format(v2,v1), '({}) / ({})'.format(v2, v1),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    def __neg__(self):
        v1 = expressionStringScalar(self,self)

        v = Constant("var_neg_{}".format(v1), '(-{})'.format(v1),registry=None)
        v.registry      = self.registry
        v.expr.registry = self.registry
        return v

    __radd__ = __add__
    __rmul__ = __mul__

    def setName(self, name) : 
        self.name          = name
        self.expr.name     = 'expr_{}'.format(name)
        self.expr.registry = self.registry
        self.registry.addDefine(self)

def sin(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("sin_{}".format(v1), 'sin({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def cos(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("cos_{}".format(v1), 'cos({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def tan(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("tan_{}".format(v1), 'tan({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def asin(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("sin_{}".format(v1), 'asin({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def acos(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("cos_{}".format(v1), 'acos({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def atan(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("tan_{}".format(v1), 'atan({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def exp(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("exp_{}".format(v1), 'exp({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def log(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("log_{}".format(v1), 'log({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def log10(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("log10_{}".format(v1), 'log10({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v

def sqrt(arg) : 
    v1 = expressionStringScalar(arg,arg)
    v = Constant("sqrt_{}".format(v1), 'sqrt({})'.format(v1),registry=None)
    v.registry      = arg.registry
    v.expr.registry = arg.registry    
    return v    

class Constant(ScalarBase) :
    def __init__(self, name, value, registry = None, addRegistry = True) :
        self.name  = name

        if isinstance(value,ScalarBase) : 
            self.expr = _Expression("expr_{}".format(name), value.expr.expression, registry=registry)            
        else :
            self.expr = _Expression("expr_{}".format(name), str(value), registry=registry)

        if registry != None: 
            self.registry = registry
            if addRegistry :
                registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()
    
    def __repr__(self) :
        return "Constant : {} = {}".format(self.name, str(self.expr))

class Quantity(ScalarBase) :
    def __init__(self, name, value, unit, type, registry = None, addRegistry = True) :
        self.name  = name
        self.unit  = unit
        self.type  = type

        if isinstance(value,ScalarBase) : 
            self.expr = _Expression("expr_{}".format(name), value.expr.expression, registry=registry)                    
        else : 
            self.expr  = _Expression("expr_{}".format(name), str(value), registry=registry)


        if registry != None: 
            self.registry = registry
            if addRegistry :
                registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Quantity: {} = {} [{}] {}".format(self.name, str(self.expr), self.unit, self.type)

class Variable(ScalarBase) :
    def __init__(self, name, value, registry = None, addRegistry = True) :
        self.name  = name

        if isinstance(value,ScalarBase) : 
            self.expr = _Expression("expr_{}".format(name), value.expr.expression, registry=registry)            
        else : 
            self.expr  = _Expression("expr_{}".format(name), str(value), registry=registry)

        if registry != None: 
            self.registry = registry
            if addRegistry : 
                registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Variable: {} = {}".format(self.name, str(self.expr))

class Expression(ScalarBase) : 
    def __init__(self, name, value, registry = None, addRegistry = False) :
        self.name  = name

        if isinstance(value,ScalarBase) : 
            self.expr = _Expression("expr_{}".format(name), value.expr.expression, registry=registry)                        
        else : 
            self.expr  = _Expression("expr_{}".format(name), str(value), registry=registry)
            
        if registry != None: 
            self.registry = registry

        if addRegistry and registry != None:
            registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()

    def __int__(self) :
        return int(self.expr.eval())

    def __repr__(self) :
        return "Expression: {} = {}".format(self.name, str(self.expr))    

class VectorBase(object) :
    def __init__() :
        pass
    
    def __add__(self,other) :
        p  = Position("vec_{}_add_{}".format(self.name,other.name),
                      '({})+({})'.format(self.x.expression,other.x.expression),
                      '({})+({})'.format(self.y.expression,other.y.expression),
                      '({})+({})'.format(self.z.expression,other.z.expression),
                      self.unit,
                      None)
        p.registry      = self.registry
        p.x.registry    = self.registry
        p.y.registry    = self.registry
        p.z.registry    = self.registry
        return p

    def __sub__(self,other) : 
        p  = Position("vec_{}_sub_{}".format(self.name,other.name),
                      '({})-({})'.format(self.x.expression,other.x.expression),
                      '({})-({})'.format(self.y.expression,other.y.expression),
                      '({})-({})'.format(self.z.expression,other.z.expression),
                      self.unit,
                      None)
        p.registry      = self.registry
        p.x.registry    = self.registry
        p.y.registry    = self.registry
        p.z.registry    = self.registry
        return p

    def __mul__(self,other) : 
        print type(self),type(other)
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)
        
        p = Position("vec_{}_mul_{}".format(self.name,v2),
                     '({})*({})'.format(self.x.expression,v2),
                     '({})*({})'.format(self.y.expression,v2),
                     '({})*({})'.format(self.z.expression,v2),
                     self.unit,
                     None)
        p.registry      = self.registry
        p.x.registry    = self.registry
        p.y.registry    = self.registry
        p.z.registry    = self.registry
        return p                     

    __rmul__ = __mul__

    def __div__(self,other) : 
        v1 = expressionStringScalar(self,self)
        v2 = expressionStringScalar(self,other)
        
        p = Position("vec_{}_div_{}".format(self.name,v2),
                     '({})/({})'.format(self.x.expression,v2),
                     '({})/({})'.format(self.y.expression,v2),
                     '({})/({})'.format(self.z.expression,v2),
                     self.unit,
                     None)
        p.registry      = self.registry
        p.x.registry    = self.registry
        p.y.registry    = self.registry
        p.z.registry    = self.registry
        return p                     
    
    def setName(self, name) : 
        self.name          = name
        self.x.registry    = self.registry 
        self.y.registry    = self.registry 
        self.z.registry    = self.registry 
        self.x.name        = 'expr_{}_vec_x'.format(name)
        self.y.name        = 'expr_{}_vec_y'.format(name)
        self.z.name        = 'expr_{}_vec_z'.format(name)
        self.registry.addDefine(self)

    def eval(self) :
        u = _Units.unit(self.unit)
        return [self.x.eval()*u, self.y.eval()*u, self.z.eval()*u]

    def __getitem__(self, key):
        if key == 0 : 
            return self.x
        elif  key == 1 : 
            return self.y 
        elif  key == 2 :
            return self.z
        else :
            raise IndexError

def expressionStringVector(var) : 

    if isinstance(var,ScalarBase) :                
        try :                
            var.registry.defineDict[var.name]
            return var.name
        except KeyError : 
            return var.expr.expression
    else :
        return str(var)
    
class Position(VectorBase) :
    def __init__(self,name,x,y,z, unit="mm", registry = None, addRegistry = True) :
        self.name = name
        if unit != None :
            self.unit = unit
        else :
            self.unit = "mm"

        self.x = _Expression("expr_{}_pos_x".format(name), expressionStringVector(x), registry=registry)
        self.y = _Expression("expr_{}_pos_y".format(name), expressionStringVector(y), registry=registry)
        self.z = _Expression("expr_{}_pos_z".format(name), expressionStringVector(z), registry=registry)
               
        if registry != None: 
            self.registry = registry
            if addRegistry : 
                registry.addDefine(self)

    def __repr__(self) :
        return "Position : {} = [{} {} {}]".format(self.name, str(self.x), str(self.y), str(self.z))

class Rotation(VectorBase) : 
    def __init__(self,name,rx,ry,rz, unit="rad", registry = None, addRegistry = True) :
        self.name = name
        if unit != None : 
            self.unit = unit
        else :
            self.unit = "rad"

        self.x = _Expression("expr_{}_rot_x".format(name), expressionStringVector(rx), registry=registry)
        self.y = _Expression("expr_{}_rot_y".format(name), expressionStringVector(ry), registry=registry)
        self.z = _Expression("expr_{}_rot_z".format(name), expressionStringVector(rz), registry=registry)

        if registry != None : 
            self.registry = registry
            if addRegistry :
                registry.addDefine(self)

    def __repr__(self) :
        return "Rotation : {} = [{} {} {}]".format(self.name, str(self.x), str(self.y), str(self.z))

class Scale(VectorBase) : 
    def __init__(self,name,sx,sy,sz, unit="none", registry = None, addRegistry = True) :
        self.name = name
        if unit != None : 
            self.unit = unit 
        else :
            self.unit = "none"

        self.x = _Expression("expr_{}_scl_x".format(name), expressionStringVector(sx), registry=registry)
        self.y = _Expression("expr_{}_scl_y".format(name), expressionStringVector(sy), registry=registry)
        self.z = _Expression("expr_{}_scl_z".format(name), expressionStringVector(sz), registry=registry)

        if registry != None: 
            self.registry = registry
            if addRegistry : 
                registry.addDefine(self)        

    def __repr__(self) :
        return "Scale : {} = [{} {} {}]".format(self.name, str(self.x), str(self.y), str(self.z))

class Matrix :
    def __init__(self,name, coldim, values, registry = None, addRegistry = True) :
        self.name = name
        self.coldim = int(coldim)

        self.values = [] 
        for i, v in enumerate(values) :
            self.values.append(Expression("matrix_expr_{}_idx{}_val".format(name,i), expressionStringVector(v),registry=registry))

        self.values_asarray = _np.array(self.values, dtype=_np.object)
        if self.coldim > 1:
            self.values_asarray = self.values_asarray.reshape(self.coldim, len(values)/self.coldim)

        if registry != None:
            self.registry = registry
            if addRegistry :
                registry.addDefine(self)
            
    def eval(self) :
        return [ e.eval() for e in self.values ]

    def __repr__(self) :
        return "Matrix : {} = {} {}".format(self.name, str(self.coldim), str(self.values))

    def __getitem__(self, key):
        return self.values_asarray[key]
