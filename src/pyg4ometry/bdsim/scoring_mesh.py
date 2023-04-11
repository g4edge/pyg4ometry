class ScoringMesh(object):
    def __init__(self, name, position, rotation, quantity, nbins, size):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.quantity = quantity # quantity to be scored.
        self.nbins = nbins # [nx, ny, nz] nbins in each dimension of mesh.
        self.size = size # [xsize, ysize, zsize] dimensions of mesh.
