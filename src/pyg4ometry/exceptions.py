class NullMeshError(Exception):
    """Null Mesh exception.  Should be raised when the output of
    mesh.toPolygons evaluates to the empty list.  arg can be a
    user-provided message (string), or a SolidBase-derived instance."""

    def __init__(self, arg):
        from . import geant4

        if isinstance(arg, geant4.solid.SolidBase):
            self.solid = arg
            if isinstance(self.solid, geant4.solid.Intersection):
                self.message = f"Null mesh in intersection between solids: {self.solid.obj1.name}, {self.solid.obj2.name}."
            elif isinstance(self.solid, geant4.solid.Subtraction):
                self.message = f"Null mesh in subtraction between solids: {self.solid.obj1.name}, {self.solid.obj2.name}."
            else:
                self.message = f"Null mesh in {type(self.solid)}."
            super(Exception, self).__init__(str(self))
        elif isinstance(arg, str):
            self.message = arg
            super(Exception, self).__init__(str(self))


class IdenticalNameError(Exception):
    """
    Exception for trying to add the same name to the geant4 registry.

    :param name: the name that has been duplicated
    :type name: str
    :param nametype: optional extra information regarding the nature of thecduplicate ("material", "solid", etc.)
    :type nametype: str
    """

    def __init__(self, name, nametype=None):
        self.name = name
        self.nametype = nametype
        if nametype is None:
            self.message = f"Identical name detected in registry: {name}"
        else:
            self.message = f"Identical {nametype} name detected in registry: {name}"
        super(Exception, self).__init__(self.message)


class FLUKAError(Exception):
    pass


class FLUKAInputError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(self.message)
