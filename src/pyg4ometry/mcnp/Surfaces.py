class P:
    """
    Plane (general)
    """

    def __init__(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __repr__(self):
        return f"P: {self.A} {self.B} {self.C} {self.D}"


class PX:
    """
    Plane (normal to x-axis)
    """

    def __init__(self, D):
        self.D = D

    def __repr__(self):
        return f"PX: {self.D}"


class PY:
    """
    Plane (normal to y-axis)
    """

    def __init__(self, D):
        self.D = D

    def __repr__(self):
        return f"PY: {self.D}"


class PZ:
    """
    Plane (normal to z-axis)
    """

    def __init__(self, D):
        self.D = D

    def __repr__(self):
        return f"PZ: {self.D}"

class SO:
    '''
    Sphere (centered at origin)
    '''
    def __init__(self, R):
        self.R = R

    def __repr__(self):
        return f"SO: {self.R}"

class S:
    '''
    Sphere (general)
    '''
    def __init__(self, x, y, z, R):
        self.x = x
        self.y = y
        self.z = z
        self.R = R

    def __repr__(self):
        return f"S: {self.x} {self.y} {self.z} {self.R}"

class SX:
    '''
    Sphere (centered on x-axis)
    '''
    def __init__(self, x, R):
        self.x = x
        self.R = R

    def __repr__(self):
        return f"SX: {self.x} {self.R}"

class SY:
    '''
    Sphere (centered on y-axis)
    '''
    def __init__(self, y, R):
        self.y = y
        self.R = R

    def __repr__(self):
        return f"SY: {self.y} {self.R}"

class SZ:
    '''
    Sphere (centered on z-axis)
    '''
    def __init__(self, z, R):
        self.z = z
        self.R = R

    def __repr__(self):
        return f"SZ: {self.z} {self.R}"

