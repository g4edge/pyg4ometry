class Scoring:
    def __init__(
        self,
        n1=10,
        low1=-10,
        high1=10,
        n2=10,
        low2=-10,
        high2=10,
        n3=10,
        low3=-10,
        high3=10,
        coordType="cartesian",
        type="",
    ):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.low1 = low1
        self.high1 = high1
        self.low2 = low2
        self.high2 = high2
        self.low3 = low3
        self.high3 = high3
        self.coordType = coordType
        self.type = type

    def flukaString(self):
        pass

    def bdsimString(self):
        pass
