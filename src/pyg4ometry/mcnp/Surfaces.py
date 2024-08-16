
class P:
    '''
    Plane (general)
    '''
    def __init__(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __repr__(self):
        return f"P: {self.A} {self.B} {self.C} {self.D}"

class PX:
    '''
    Plane (normal to x-axis)
    '''

    def __init__(self, D):
        self.D = D

    def __repr__(self):
        return f"PX: {self.D}"

class PY:
    '''
    Plane (normal to y-axis)
    '''

    def __init__(self, D):
        self.D = D

    def __repr__(self):
        return f"PY: {self.D}"

class PZ:
    '''
    Plane (normal to z-axis)
    '''

    def __init__(self, D):
        self.D = D

    def __repr__(self):
        return f"PZ: {self.D}"