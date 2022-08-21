import numpy as _np

class TwoVector(object):
    def __init__(self, xIn, yIn):
        self.x = xIn
        self.y = yIn

    def Rotated(self, angle):
        # do rotation
        xr = self.x*_np.cos(angle) - self.y*_np.sin(angle)
        yr = self.x*_np.sin(angle) + self.y*_np.cos(angle)
        return TwoVector(xr,yr)

    def __repr__(self):
        s = '(' + str(self.x) + ', ' + str(self.y) + ')'
        return s

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Invalid index "+str(index))

    def __add__(self, other):
        if type(other) == TwoVector:
            return TwoVector(self.x + other.x, self.y + other.y)
        elif type(other) == float or type(other) == int:
            return TwoVector(self.x + other, self.y + other)
        else:
            raise ValueError("unsupported type " + str(type(other)))

    def __sub__(self, other):
        if type(other) == TwoVector:
            return TwoVector(self.x - other.x, self.y - other.y)
        elif type(other) == float or type(other) == int:
            return TwoVector(self.x - other, self.y - other)
        else:
            raise ValueError("unsupported type " + str(type(other)))

    def __mul__(self, other):
        if type(other) == float or type(other) == int:
            return TwoVector(self.x * other, self.y * other)
        else:
            raise ValueError("unsupported type " + str(type(other)))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) == float or type(other) == int:
            return TwoVector(self.x / other, self.y / other)
        else:
            raise ValueError("unsupported type " + str(type(other)))

    def __abs__(self):
        return _np.sqrt((self.x)**2 + (self.y)**2)

    def dot(self, other):
        if type(other) == TwoVector:
            return self.x * other.x + self.y * other.y
        else:
            raise ValueError("unsupported type" + str(type(other)))

    def cross(self, other):
        if type(other) == TwoVector:
            z = self.x * other.y - self.y * other.x
            return _np.array([0,0,z])
