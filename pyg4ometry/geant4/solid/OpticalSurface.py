from .SolidBase import SolidBase as _SolidBase
from .._Material import WithPropertiesBase

class OpticalSurface(_SolidBase, WithPropertiesBase):
    allowed_models    = []
    allowed_types     = []
    allowed_finishes  = []

    def __init__(self, name, finish, model, surf_type, value, registry, addRegistry=True):
        """
        Construct an optical surface.

        :param name:    of this optical surface
        :type name:     str
        :param finish:  One of the allowed surface finishes
        :type finish:   str
        :param model:   One of the allowed surface models
        :type model:    str
        :param surf_type: One of the allowed surface types
        :type surf_type: str
        :param value:   Parameter, depending on the model
        :type value:    str,float,int
        """
        super(OpticalSurface, self).__init__(name, 'OpticalSurface', registry)
        self.finish = finish
        self.model  = model
        self.osType = surf_type
        self.value  = value
        self.properties = {}

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return 'OpticalSurface : '+str(self.name)

    def add_property(self, name, value):
        """
        Add a property to this surface from a matrix.

        :param name: key of the surface property
        :type name: str
        :param value: matrix defining the value(s) of the property
        :type value: Matrix
        """
        self.properties[name] = value

    def addProperty(self, name, value):
        """
        Alias for add_property
        """
        self.add_property(name, value)
