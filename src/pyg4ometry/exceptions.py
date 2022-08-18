class NullMeshError(Exception):
    """Null Mesh exception.  Should be raised when the output of
    mesh.toPolygons evaluates to the empty list.  arg can be a
    user-provided message (string), or a SolidBase-derived instance."""
    def __init__(self, arg):
        import pyg4ometry.geant4

        if isinstance(arg, pyg4ometry.geant4.solid.SolidBase):
            self.solid = arg
            if isinstance(self.solid,pyg4ometry.geant4.solid.Intersection):
                self.message = ("Null mesh in intersection between solids:"
                                " {}, {}.".format(self.solid.obj1.name,
                                                  self.solid.obj2.name))
            elif isinstance(self.solid,pyg4ometry.geant4.solid.Subtraction):
                self.message = ("Null mesh in subtraction between solids:"
                                " {}, {}.".format(self.solid.obj1.name,
                                                  self.solid.obj2.name))
            else:
                self.message = "Null mesh in {}.".format(type(self.solid))
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
            self.message = (
                "Identical name detected in registry: {}".format(name))
        else:
            self.message = (
                "Identical {} name detected in registry: {}".format(
                    nametype, name))
        super(Exception, self).__init__(self.message)


class FLUKAError(Exception):
    pass


class FLUKAInputError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(self.message)
