class Sampler(object):
    def __init__(self, name, position, rotation, apertype, apers):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.apertype = apertype
        self.apers = apers
        if len(apers) != 4:
            raise ValueError("apers1-4 must be provided.")

