class SolidBase(object):
    """
    Base class for all solis
    """
    def __init__(self, name="noname", registry=None):
        self.name = name
        self.registry = registry

    def evaluateParameter(self, obj):
        from pyg4ometry.gdml.Defines import evaluateToFloat
        return evaluateToFloat(self.registry, obj)

    def _addProperty(self, attribute):
        #create local setter and getter with a particular attribute name
        if hasattr(self.__class__, attribute):
            return

        getter = lambda self: self._getProperty(attribute)
        setter = lambda self, value: self._setProperty(attribute, value)

        #construct property attribute and add it to the class
        setattr(self.__class__, attribute, property(fget=getter,
                                                    fset=setter,
                                                    doc="Auto-generated method"))

    def _setProperty(self, attribute, value):
        #print "Setting: %s = %s" %(attribute, value) # DEBUG
        # When setting a parameter of a solid, add the solid name
        # to a list of edited solids in the registry. This forces a fresh
        # meshing for visualisation, instead of using the cached mesh.
        self.registry.registerSolidEdit(self)
        setattr(self, '_' + attribute, value)

    def _getProperty(self, attribute):
        #print "Getting: %s" %str(attribute) # DEBUG
        return getattr(self, "_" + attribute)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        non_alphanum = set([c for c in name if not c.isalnum()])
        non_alphanum = non_alphanum.difference('_')  # underscores are # OK.
        non_alphanum = non_alphanum.difference('.')  #
        if non_alphanum:
            msg = \
                'Forbidden character(s) in name "{}": {}.'.format(name,
                    list(non_alphanum))
            raise ValueError(msg)
        if not name[0].isalpha():
            msg = \
                'First char of name "{}" must be a letter.'.format(name)
            raise ValueError(msg)
        self._name = name
