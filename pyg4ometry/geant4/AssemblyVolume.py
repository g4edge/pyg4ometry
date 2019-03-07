import pyg4ometry.exceptions 

class AssemblyVolume(object) : 

    def __init__(self, name, registry=None) :
        '''AssemblyVolume : similar to a logical volume but does not have a sense of shape, material or field'''

        super(AssemblyVolume, self).__init__()
        
        self.name = name 
        self.daughterVolumes = []

        if registry :
            registry.addAssemblyVolume(self)                    
            
    def __repr__(self):
        return 'Logical volume : '+self.name

    def add(self, physicalVolume) :
        self.daughterVolume.append(physicalVolume)
        
    def checkOverlaps(self) : 
        pass

