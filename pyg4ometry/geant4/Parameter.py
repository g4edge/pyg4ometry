from Registry import registry as _registry

class Parameter(object):
    def __init__(self, name, value, addRegistry=True):
        self.name  = name

        if isinstance(value,Parameter):
            self.value = value.value
            self.expr  = value.name
        else:
            self.value = float(value)
            self.expr  = name
        if addRegistry:
            _registry.addParameter(self)

    def __repr__(self):
        return self.name

    def str(self):
        return 'param:'+self.name+':'+str(self.value)

    def __float__(self):
        return float(self.value)

    def __getitem__(self, i): 
        return self.value[i]

    def __add__(self, other):
        return Parameter('{} + {}'.format(self, other),float(self)+float(other),False)

    def __sub__(self, other):
        return Parameter('{} - {}'.format(self, other),float(self)-float(other),False)

    def __mul__(self, other):
        return Parameter('{} * {}'.format(self, other), float(self) * float(other),False)

    def __rmul__(self, other):
        return Parameter('{} * {}'.format(self, other), float(other)* float(self),False)
    
    def __div__(self, other):
        return Parameter('{} / {}'.format(self, other), float(self) / float(other),False)

    def __neg__(self):
        return Parameter('- {}'.format(self), -float(self),False)
