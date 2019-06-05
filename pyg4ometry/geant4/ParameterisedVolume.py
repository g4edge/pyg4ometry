from ReplicaVolume import ReplicaVolume as _ReplicaVolume
import pyg4ometry.exceptions 

class ParametrisedVolume(_ReplicaVolume) : 
    '''ParametrisedVolume 
    :param name: of parametrised volume
    :param logical:  volume to be placed
    :param mother: volume logical volume 
    :param ncopies: number of parametrised volumes
    '''
    def __init__(self, name, logical, mother, ncopies, registry=None,addRegistry=True) : 
        # super(ParametrisedVolume, self).__init__([0,0,0],[0,0,0],logicalVolume,name,motherVolume, registry, addRegistry)       
        self.logicalVolume       = logical
        self.mother              = mother
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
    

