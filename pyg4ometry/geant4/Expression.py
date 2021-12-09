import math as _math
from pyg4ometry.geant4.Registry import Registry as _Registry

#try:
#    import sympy as _sympy
#except ImportError :
#    noSymPy = True

class Expression(object) :
    def __init__(self, name, expression, registry=_Registry()) :
        # TODO: make the registry required
        self.name       = name
        self.expression = expression
        self.parse_tree = None
        self.registry   = registry

    def eval(self) :
        expressionParser = self.registry.getExpressionParser()
        self.parse_tree = expressionParser.parse(self.expression)
        value = expressionParser.evaluate(self.parse_tree, self.registry.defineDict)

        return value

    def variables(self) :
        expressionParser = self.registry.getExpressionParser()
        self.parse_tree = expressionParser.parse(self.expression)
        variables = expressionParser.get_variables(self.parse_tree)

        return variables

    def simp(self) : 
        # find all variables of the expression and create
        pass

    def __repr__(self) :
        return "{} : {}".format(self.name, self.expression)

    def __float__(self) :
        return self.eval()

    def str(self):
        return 'Expression : '+self.name+' : '+str(float(self))

