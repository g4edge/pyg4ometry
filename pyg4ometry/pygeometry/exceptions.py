
class NullMeshError(Exception):
    """
    Exception for possible null mesh formed in Boolean operation.

    NullMeshError(vol1,vol2,"union")
    """
    def __init__(self, vol1, vol2, combination):
        super(NullMeshError, self).__init__(str(combination) + " null mesh with \n A: " + str(vol1) + "\nand B: " + str(vol2))
        self.vol1 = vol1
        self.vol2 = vol2
        self.combination = combination
