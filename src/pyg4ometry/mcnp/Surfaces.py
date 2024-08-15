
class Plane :
    def __init__(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def __repr__(self):
        return f"plane {self.A} {self.B} {self.C} {self.D}"