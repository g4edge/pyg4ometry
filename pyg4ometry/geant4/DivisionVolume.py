import PhysicalVolume as _PhysicalVolume
import numpy as _np

class DivisionVolume(_PhysicalVolume.PhysicalVolume) : 
    '''
    DivisionVolume: G4PVDivision

    :param name: of physical volume 
    :param logical: volume to be placed
    :param mother: logical volume, 
    :param axis: kXAxis,kYAxis,kZAxis,kRho,kPhi
    :param ncopies: number of replicas
    :param width: spacing between replicas along axis
    :param offset: of grid
    '''

    class Axis:
        kXAxis = 1
        kYAxis = 2
        kZAxis = 3
        kRho   = 4
        kPhi   = 5

    def __init__(self, name, logicalVolume, motherVolume, axis, nreplicas, 
                 width, offset = 0, registry = None, addRegistry=True) : 

        self.type = "division"
        self.name = name
        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.motherVolume.add(self)
        self.axis                = axis
        self.nreplicas           = nreplicas
        self.width               = width
        self.offset              = offset
        
        if addRegistry : 
            registry.addPhysicalVolume(self)
        
        # Create replica meshes
        [self.meshes, self.transforms] = self.createDivisionMeshes()

    def createDivisionMeshes(self) :

        transforms = []
        meshes     = []

        for v in _np.arange(self.offset, self.offset+self.nreplicas*self.width,self.width) : 
            print v

        return [meshes, transforms]

    def __repr__(self) :
        return ""
