import pyg4ometry.exceptions 

class ReplicaVolume(object) : 
    def __init__(self, name, logical, mother, axis, ncopies, width, offset, registry=None) : 
        '''ReplicaVolume : G4PVReplica
           name     - name of physical volume 
           logical  - logical volume to be placed
           mother   - mother logical volume, 
           axis     - kXAxis,kYAxis,kZAxis,kRho,kPhi
           ncopies  - number of replicas
           width    - spacing between replicas along axis
           offset   - offset of grid
           '''

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
