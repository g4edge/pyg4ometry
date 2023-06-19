class Boundary:
    def __init__(
        self,
        name="boundary1",
        pos=[0, 0, 0],
        rot=[0, 0, 0],
        type="plane",
        size=1,
        length=1,
    ):
        self.name = name
        self.pos = pos
        self.rot = rot
        self.type = type
        self.size = size
        self.length = length

    def flukaString(self):
        pass

    def bdsimString(self):
        pass
