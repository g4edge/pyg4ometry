import pyg4ometry.exceptions 

class ParametrisedVolume(object) : 
    def __init__(self, name, logical, mother, ncopies, registry=None) : 
        '''ParametrisedVolume 
           name     - name of physical volume 
           logical  - logical volume to be placed
           mother   - mother logical volume 
           ncopies  - number of parametrised volumes
        '''

        self.logicalVolume       = logical
        self.mother              = mother
        self.ncopies             = ncopies
        
        self.paramData           = [] 

        if registry  : 
            pass

    def checkOverlap(self) :
        pass

    

