import numpy as np


class TR:
    """
    Coordinate Transformation

    :param o1, o2, o3: Displacement vector of the transformation. DEFAULT: (0, 0, 0).
    :param rotation Matrix: The rotation Matrix default is /
      [xx' yx' zx']   [1 0 0]
      [xy' yy' zy'] = [0 1 0]
      [xz' yz' zz']   [0 0 1]
    :param displacementOrigin: Displacement vector origin /
      If = positive 1 the displacement vector is the location of the origin of the auxiliary coordinate system, /
            defined in the main system. (DEFAULT)
      If = negative 1 the displacement vector is the location of the origin of the main coordinate system, /
             defined in the auxiliary system.
    :param transformationNumber: Number assigned to the transformation.
    """

    def __init__(
        self,
        o1=0,
        o2=0,
        o3=0,
        rotxx=1,
        rotyx=0,
        rotzx=0,
        rotxy=0,
        rotyy=1,
        rotzy=0,
        rotxz=0,
        rotyz=0,
        rotzz=1,
        displacementOrigin=1,
        reg=None,
        transformationNumber=None,
    ):
        self.o1 = o1
        self.o2 = o2
        self.o3 = o3
        self.rotationMatrix = np.zeros((3, 3))
        self.rotationMatrix[0][0] = rotxx
        self.rotationMatrix[0][1] = rotyx
        self.rotationMatrix[0][2] = rotzx
        self.rotationMatrix[1][0] = rotxy
        self.rotationMatrix[1][1] = rotyy
        self.rotationMatrix[1][2] = rotzy
        self.rotationMatrix[2][0] = rotxz
        self.rotationMatrix[2][1] = rotyz
        self.rotationMatrix[2][2] = rotzz
        self.displacementOrigin = displacementOrigin
        self.transformationNumber = transformationNumber
        if reg:
            reg.addTransformation(self)
            self.reg = reg

    def __repr__(self):
        return (
            f"TR: {self.o1} {self.o2} {self.o3} "
            f"{self.rotxx} {self.rotyx} {self.rotzx}"
            f"{self.rotxy} {self.rotyy} {self.rotzy}"
            f"{self.rotxz} {self.rotyz} {self.rotzz}"
            f"{self.displacementOrigin}"
        )


class TRCL(TR):
    def __init__(
        self,
        o1=0,
        o2=0,
        o3=0,
        rotxx=1,
        rotyx=0,
        rotzx=0,
        rotxy=0,
        rotyy=1,
        rotzy=0,
        rotxz=0,
        rotyz=0,
        rotzz=1,
        displacementOrigin=1,
        reg=None,
        transformationNumber=None,
    ):
        super().__init__(
            o1,
            o2,
            o3,
            rotxx,
            rotyx,
            rotzx,
            rotxy,
            rotyy,
            rotzy,
            rotxz,
            rotyz,
            rotzz,
            displacementOrigin,
            transformationNumber,
        )
