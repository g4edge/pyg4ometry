from ReplicaVolume import ReplicaVolume as _ReplicaVolume
import pyg4ometry.exceptions 

class ParametrisedVolume(_ReplicaVolume) : 
    '''ParametrisedVolume 
    :param name: of parametrised volume
    :param logical:  volume to be placed
    :param mother: volume logical volume 
    :param ncopies: number of parametrised volumes
    '''
    def __init__(self, name, logicalVolume, mother, ncopies, registry=None,addRegistry=True) : 

        self.type                = "parametrised" 

        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.ncopies             = ncopies
        
        self.paramData           = [] 

        if addRegistry  : 
            registry.addPhysicalVolume(self)


    def createParametrisedMeshes(self) : 

        for v in _np.arange(self.offset, self.offset+self.nreplicas*self.width,self.width) : 
            print v 

    def checkOverlap(self) :
        pass

    def __repr__(self) :
        return ""
    

