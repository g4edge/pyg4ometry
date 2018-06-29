import math as _math

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


class ExpressionRegistry(dict) : 
    def __init__(self) : 
        pass
    
expressionRegistry = ExpressionRegistry() 

class Expression(object) :
    def __init__(self,name, value = 0.0) :
        self.name  = name 
        self.value = value

    def eval(self) : 
        pass

    def __repr__(self) :
        return self.name 

    def __float__(self) : 
        return float(self.value)

    def str(self):
        return 'Expression : '+self.name+' : '+str(self.value)

    def __add__(self, other):
        return Expression('{} + {}'.format(self, other),float(self)+float(other))

    def __sub__(self, other):
        return Expression('{} - {}'.format(self, other),float(self)-float(other))

    def __mul__(self, other):
        return Expression('({}) * ({})'.format(self, other), float(self) * float(other))

    def __rmul__(self, other):
        return Expression('({}) * ({})'.format(self, other), float(other)* float(self))
    
    def __div__(self, other):
        return Expression('({}) / ({})'.format(self, other), float(self) / float(other))

    def __neg__(self):
        return Expression('- ({})'.format(self), -float(self)) 

class ExpressionVector(list) : 
    def __init__(self, name, value) :
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
    def __init__(self,name, ncoldim, value) :
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
    
