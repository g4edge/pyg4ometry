import pyg4ometry.exceptions 

class AssemblyVolume(object) : 
    '''AssemblyVolume : similar to a logical volume but does not have a sense of 
    shape, material or field
    :param name: of assembly volume
    :type name:        
    :param registry: 
    :type registry: 
    :param addRegistry: 
    :type addRegistry: bool
    '''

    def __init__(self, name, registry=None, addRegistry=True) :
        super(AssemblyVolume, self).__init__()

        # type 
        self.type            = "assembly"
        
        self.name            = name 
        self.daughterVolumes = []

        if registry :
            registry.addLogicalVolume(self)                    
            
    def __repr__(self):
        return 'Logical volume : '+self.name

    def add(self, physicalVolume) :
        self.daughterVolumes.append(physicalVolume)
        
    def checkOverlaps(self) : 
        pass

    def extent(self) : 
        pass
