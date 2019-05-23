import ReplicaVolume
import pyg4ometry.exceptions 

class ParametrisedVolume(ReplicaVolume.ReplicaVolume) : 
    '''ParametrisedVolume 
    :param name: of parametrised volume
    :param logical:  volume to be placed
    :param mother: volume logical volume 
    :param ncopies: number of parametrised volumes
    '''
    def __init__(self, name, logical, mother, ncopies, registry=None) : 
        super(ParametrisedVolume, self).__init__([0,0,0],[0,0,0],logicalVolime,name,motherVolume, registry, addRegistry)       
        self.logicalVolume       = logical
        self.mother              = mother
        self.ncopies             = ncopies
        
        self.paramData           = [] 

        if registry  : 
            pass

    def checkOverlap(self) :
        pass

    

