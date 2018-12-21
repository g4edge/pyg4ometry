from ..geant4 import Expression as _Expression

class Constant :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr = _Expression("expr_{}".format(name), value, registry=registry)

        registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()
    
    def __repr__(self) :
        return "Constant : {} = {}".format(self.name, str(self.expr))

class Quantity :
    def __init__(self, name, value, unit, type, registry = None) :
        self.name  = name
        self.expr  = _Expression("expr_{}".format(name), value, registry=registry)
        self.unit  = unit
        self.type  = type

        registry.addDefine(self)

    def eval(self) :
        return self.expr.eval()

    def __float__(self) :
        return self.expr.eval()

    def __repr__(self) :
        return "Quantity: {} = {} [{}] {}".format(self.name, str(self.expr), self.unit, self.type)

class Variable :
    def __init__(self, name, value, registry = None) :
        self.name  = name
        self.expr  = _Expression("expr_{}".format(name), value, registry=registry)

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
        self.x = _Expression("expr_{}_pos_x".format(name), x, registry=registry)
        self.y = _Expression("expr_{}_pos_y".format(name), y, registry=registry)
        self.z = _Expression("expr_{}_pos_z".format(name), z, registry=registry)
        
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
        self.rx = _Expression("expr_{}_rot_x".format(name), rx, registry=registry)
        self.ry = _Expression("expr_{}_rot_y".format(name), ry, registry=registry)
        self.rz = _Expression("expr_{}_rot_z".format(name), rz, registry=registry)

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
        self.sx = _Expression("expr_{}_scl_x".format(name), sx, registry=registry)
        self.sy = _Expression("expr_{}_scl_x".format(name), sy, registry=registry)
        self.sz = _Expression("expr_{}_scl_x".format(name), sz, registry=registry)

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

