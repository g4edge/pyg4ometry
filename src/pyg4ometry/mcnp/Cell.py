class Cell:
    def __init__(self, surfaces=[], reg=None, cellNumber=None):
        self.surfaceList = surfaces
        self.cellNumber = cellNumber
        # self.geometry = geometry
        if reg:
            reg.addCell(self)
            self.reg = reg

    def addSurface(self, surface):
        if type(surface) is str and surface in self.reg.surfaceDict:
            surface = self.reg.surfaceDict[surface]
        self.surfaceList.append(surface)

    def addSurfaces(self, surfaces):
        self.surfaceList.extend(surfaces)

    def addMacrobody(self, macrobody):
        self.addSurface(macrobody)

    def addMacrobodies(self, macrobody):
        self.addSurfaces(macrobody)


class Intersection:
    """
    mcnp : blank space between two surface numbers
    pyg4 : asterisk
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toOutputString(self):
        return self.left.toOutputString() + " " + self.right.toOutputString()


class Union:
    """
    mcnp : colon
    pyg4 : plus
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toOutputString(self):
        return self.left.toOutputString() + ":" + self.right.toOutputString()


class Complement:
    """
    mcnp : hash
    pyg4 : hyphen
    """

    def __init__(self, item):
        self.item = item

    def toOutputString(self):
        return "#" + self.item.toOutputString()


class Identity:
    """
    mcnp : no operator
    pyg4 : no operator
    """

    def __init__(self, item):
        self.item = item

    def toOutputString(self):
        return str(self.item.surfaceNumber)
