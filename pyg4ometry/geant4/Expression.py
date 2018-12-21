import math as _math
from pyg4ometry.geant4 import Registry

def sin(expression) : 
    return Expression('sin('+expression.name + ')',_math.sin(expression.value))

def cos(expression) : 
    return Expression('cos('+expression.name + ')',_math.cos(expression.value))

def tan(expression) : 
    return Expression('tan('+expression.name + ')',_math.tan(expression.value))

def exp(expression) : 
    return Expression('exp('+expression.name + ')',_math.exp(expression.value))

def log(expression) :
    return Expression('log('+expression.name + ')',_math.log(expression.value))

def log10(expression) :
    return Expression('log10('+expression.name + ')',_math.log10(expression.value))

class Expression(object) :
    def __init__(self, name, expression, registry=Registry()) :
        # TODO: make the registry required
        self.name  = name
        self.expression = expression
        self.parse_tree = None
        self.registry = registry

    def eval(self) :
        expressionParser = self.registry.getExpressionParser()
        self.parse_tree = expressionParser.parse(self.expression)
        value = expressionParser.evaluate(self.parse_tree,
                                          self.registry.defineDict)

        return value

    def __repr__(self) :
        return "{} : {}".format(self.name, self.expression)

    def __float__(self) :
        return self.eval()

    def str(self):
        return 'Expression : '+self.name+' : '+str(float(self))

    # TODO: implement int and pow operation
    def __add__(self, other):
        return Expression('{}_add_{}'.format(self.name, other.name),'{} + {}'.format(self.expression, other.expression),registry=self.registry)

    def __sub__(self, other):
        return Expression('{}_sub_{}'.format(self.name, other.name),'({}) - ({})'.format(self.expression, other.expression),registry=self.registry)

    def __mul__(self, other):
        return Expression('{}_mul_{}'.format(self.name, other.name),'({}) * ({})'.format(self.expression, other.expression),registry=self.registry)

    def __rmul__(self, other):
        return Expression('{}_mul_{}'.format(self.name, other.name),'({}) * ({})'.format(self.expression, other.expression),registry=self.registry)
    
    def __div__(self, other):
        return Expression('{}_div_{}'.format(self.name, other.name),'({}) / ({})'.format(self.expression, other.expression),registry=self.registry)

    def __neg__(self):
        return Expression('neg_{}'.format(self.name),'- ({})'.format(self.expression), registry=self.registry)

class ExpressionVector(list) : 
    def __init__(self, name, value, registry=None) :
        super(list,self).__init__(self)
        self.name = name 

        # append elements to self
        for elem in value:
            self.append(elem)

    def eval(self) : 
        for elem in self :
            elem.eval()
                            
    def __add__(self,other):
        return ExpressionVector('{}+{}'.format(self, other),[self[0]+other[0],
                                                             self[1]+other[1],
                                                             self[2]+other[2]])
    
    def __sub__(self, other):
        return ExpressionVector('{}-{}'.format(self, other),[self[0]-other[0],
                                                             self[1]-other[1],
                                                             self[2]-other[2]])    

class ExpressionMatrix(list) : 
    def __init__(self,name, ncoldim, value, registry=None) :
        #super(ExpressionMatrix,self).__init__()
        self.name = name

        for elem in value :
            self.append(elem)
    
    def eval(self) : 
        for elem in self :
            elem.eval()

    def index(self,i) :
        return self[i]
    
def expressionTest() : 
    a = Expression("a",1)
    b = Expression("b",2)
    c = Expression("c",3)
    
    print a.str()
    print b.str()
    print c.str()
    
    z = a+b
    print z.str()
    
    z = a-b
    print z.str()
    
    z = a*b
    print z.str()

    z  = 10*b
    print z.str()

    z = a/b
    print z.str()

    z = a/10.0
    print z.str()

    z  = -a
    print z.str()

    z =-(a-b)    
    print z.str()

    z  = a*(b+c)
    print z.str()
    
    z  = a/(b+c)
    print z.str()

    z = sin(a)
    print z.str()
    
    z = cos(a)
    print z.str()

    z = tan(a)
    print z.str()

    z = log(b)
    print z.str()

    z = log10(b)
    print z.str()

    z = exp(a)
    print z.str()

    z = sin(a+b/c)
    print z.str()
    
def expressionVectorTest() :

    x = Expression("x",1)
    y = Expression("y",2)
    z = Expression("z",3)
    v = ExpressionVector("v",[x,y,z])
    
    print v.str()
