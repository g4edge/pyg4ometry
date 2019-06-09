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
        self.name                = name
        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.motherVolume.add(self)
        self.ncopies             = ncopies
        
        self.paramData           = [] 

        if addRegistry  : 
            registry.addPhysicalVolume(self)

        # Create parameterised meshes
        [self.meshes,self.transforms] = self.createParameterisedMeshes()
                    
    def createParametrisedMeshes(self) : 
        return None,None
            
    def __repr__(self) :
        return ""
    

