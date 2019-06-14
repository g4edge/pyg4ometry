import PhysicalVolume as _PhysicalVolume
from   pyg4ometry.visualisation  import Mesh     as _Mesh

import numpy as _np
import copy as _copy

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

    class Axis :
        kXAxis = 1
        kYAxis = 2
        kZAxis = 3
        kRho   = 4
        kPhi   = 5

    def __init__(self, name, logicalVolume, motherVolume, axis, nreplicas, 
                 width, offset = 0, registry = None, addRegistry=True, wunit = "", ounit= "") : 

        self.type                = "replica"        
        self.name                = name
        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.motherVolume.add(self)
        self.axis                = axis

        self.nreplicas           = nreplicas
        self.width               = width
        self.offset              = offset
        self.wunit               = wunit
        self.ounit               = ounit

        if addRegistry : 
            registry.addPhysicalVolume(self)
        
        # Create replica meshes
        [self.meshes,self.transforms] = self.createReplicaMeshes()

    def createReplicaMeshes(self) : 
        
        nreplicas = int(self.nreplicas.eval())
        offset    = self.offset.eval()
        width     = self.width.eval()
        
        transforms = []
        meshes     = [] 

        for v,i in zip(_np.arange(-width*(nreplicas-1)*0.5,  width*(nreplicas+1)*0.5, width),range(0,nreplicas,1)) :
            if self.axis == self.Axis.kXAxis :                 
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,0],[v,0,0]])

            elif self.axis == self.Axis.kYAxis : 
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,0],[0,v,0]])

            elif self.axis == self.Axis.kYAxis : 
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,0],[0,0,v]])

        for v,i in zip(_np.arange(offset, offset+nreplicas*width,width),range(0,nreplicas,1)) :
            if self.axis == self.Axis.kRho :

                # Copy solid so we don't change the original
                solid       = _copy.deepcopy(self.logicalVolume.solid)
                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)
                # Must be a tubs 
                solid.pRMin.expr.expression = str(v)
                solid.pRMax.expr.expression = str(v+width)            
                mesh   = _Mesh(solid)                                

                meshes.append(mesh)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi : 
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,v],[0,0,0]])                
            
        return [meshes,transforms]

    def __repr__(self) :
        return 'Replica volume : '+self.name+' '+str(self.axis)+' '+str(self.nreplicas)+' '+str(self.offset)+' '+str(self.width)
