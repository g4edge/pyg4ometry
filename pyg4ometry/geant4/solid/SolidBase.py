#import time as _time
import numpy as _np

class SolidBase(object):
    """
    Base class for all solids
    """
    def __init__(self, name, type, registry=None):
        self.name = name
        self.type = type
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

    def _twoPiValueCheck(self, attribute, aunit="rad"):
        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        if self.evaluateParameter(getattr(self, attribute)) * (_Units.unit(aunit)) > 2 * _np.pi:
            raise ValueError("pDPhi is strictly greater than 2 x pi in solid \"" + self.name + "\"")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        '''
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
        '''
        self._name = name

    #def mesh(self):
    #    start = _time.time()
    #   m = self.pycsgmesh()
    #    elapsed_time_fl = (_time.time() - start)
    #    print(elapsed_time_fl)
    #    print(len(m.polygons))
    #    return m
