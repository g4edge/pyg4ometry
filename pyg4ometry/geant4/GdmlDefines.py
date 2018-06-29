from Parameter import Parameter

class Constant(Parameter) :
    def __init__(self, name, value) :
        Parameter.__init__(self, name, value, False)

class Quantity :
    def __init__(self, name, value, unit, type) :
        Parameter.__init__(self, name, value, False)
        self.unit = unit
        self.type = type
                        
class Variable :
    def __init__(self) :
        Parameter.__init__(self, name, value, False)

class Position :
    def __init__(self) :
        pass

class Rotation : 
    def __init__(self) :
        pass

class Scale : 
    def __init__(self) :
        pass

class Matrix :
    def __init__(self) :
        pass

