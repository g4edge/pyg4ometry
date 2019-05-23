import PhysicalVolume as _PhysicalVolume

class ReplicaVolume(_PhysicalVolume.PhysicalVolume) : 
    '''
    ReplicaVolume: G4PVReplica

    :param name: of physical volume 
    :param logical: volume to be placed
    :param mother: logical volume, 
    :param axis: kXAxis,kYAxis,kZAxis,kRho,kPhi
    :param ncopies: number of replicas
    :param width: spacing between replicas along axis
    :param offset: of grid
    '''

    def __init__(self, name, logicalVolume, motherVolume, axis, nreplicas, 
                 width, offset = 0, registry = None, addRegistry=True) : 
        super(ReplicaVolume, self).__init__([0,0,0],[0,0,0],logicalVolime,name,motherVolume, registry, addRegistry)

        self.logicalVolume       = logical
        self.mother              = mother
        self.axis                = axis
        self.ncopies             = ncopies
        self.width               = width
        self.offset              = offset
        
        if registry  : 
            pass

    def add(self) :
        pass

    def checkOverlap(self) :
        pass
