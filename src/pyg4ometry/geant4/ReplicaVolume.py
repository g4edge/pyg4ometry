from .PhysicalVolume import PhysicalVolume as _PhysicalVolume
import pyg4ometry.geant4.solid as _solid
from   pyg4ometry.visualisation import Mesh as _Mesh
from   pyg4ometry.visualisation import OverlapType as _OverlapType
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
import pyg4ometry.transformation as _trans

import numpy as _np
import copy as _copy
import logging as _log

class ReplicaVolume(_PhysicalVolume):
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

    class Axis:
        kXAxis = 1
        kYAxis = 2
        kZAxis = 3
        kRho   = 4
        kPhi   = 5
        
    def __init__(self, name, logicalVolume, motherVolume, axis, nreplicas, 
                 width, offset=0, registry=None, addRegistry=True, wunit="mm", ounit="mm"):

        # TBC - doesn't call super() so doesn't have PV objects

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

        self.visOptions          = _VisOptions()

        if addRegistry :
            registry.addPhysicalVolume(self)
        self.registry = registry

        # physical visualisation options
        self.visOptions    = _VisOptions()

        # Create replica meshes
        [self.meshes,self.transforms] = self.createReplicaMeshes()
        
    def GetAxisName(self):
        names = {1 : 'kXAxis',
                 2 : 'kYAxis',
                 3 : 'kZAxis',
                 4 : 'kRho',
                 5 : 'kPhi'}
        return names[self.axis]

    def _checkInternalOverlaps(self, debugIO=False, nOverlapsDetected=[0]):
        """
        Check if there are overlaps with the nominal mother volume. ie it possible to provide
        an incorrect mother volume / logical volume and parameterisation.
        """
        # protrusion from mother solid
        tempMeshes = []
        for (rot,tra),m in zip(self.transforms, self.meshes):
            mt = m.localboundingmesh.clone()
            aa = _trans.tbxyz2axisangle(rot)
            mt.rotate(aa[0], _trans.rad2deg(aa[1]))
            mt.translate(tra)
            tempMeshes.append(mt)

        for i in range(0, len(tempMeshes)):
            if debugIO:
                print(f"ReplicaVolume.checkOverlaps> full daughter-mother intersection test {self.meshes[i]}")

            interMesh = tempMeshes[i].subtract(self.motherVolume.mesh.localboundingmesh)
            _log.info('ReplicaVolume.checkOverlaps> daughter container %d %d %d' % (
            i, interMesh.vertexCount(), interMesh.polygonCount()))

            if interMesh.vertexCount() != 0:
                nOverlapsDetected[0] += 1
                print(f"\033[1mOVERLAP DETECTED> overlap with mother \033[0m {tempMeshes[i]} {interMesh.vertexCount()}")
                self.motherVolume.mesh.addOverlapMesh([interMesh, _OverlapType.protrusion])

        # daughter-daughter overlap check
        for i in range(0, len(tempMeshes)):
            for j in range(i + 1, len(tempMeshes)):
                if debugIO:
                    print(f"ReplicaVolume.checkOverlaps> daughter-daughter bounding mesh intersection test: #{i} #{j}")

                # first check if bounding mesh intersects
                cullIntersection = tempMeshes[i].intersect(tempMeshes[j])
                if cullIntersection.vertexCount() == 0:
                    continue

                # bounding meshes collide, so check full mesh properly
                interMesh = tempMeshes[i].intersect(tempMeshes[j])
                _log.info('ReplicaVolume.checkOverlaps> full daughter-daughter intersection test: %d %d %d %d' % (
                i, j, interMesh.vertexCount(), interMesh.polygonCount()))
                if interMesh.vertexCount() != 0:
                    nOverlapsDetected[0] += 1
                    print(f"\033[1mOVERLAP DETECTED> overlap between daughters of {self.name} \033[0m #{i} #{j} {interMesh.vertexCount()}")
                    self.motherVolume.mesh.addOverlapMesh([interMesh, _OverlapType.overlap])

    def createReplicaMeshes(self):
        import pyg4ometry.gdml.Units as _Units
        from pyg4ometry.gdml.Defines import evaluateToFloat

        nreplicas = int(evaluateToFloat(self.registry,self.nreplicas))
        offset    = evaluateToFloat(self.registry,self.offset)*_Units.unit(self.ounit)
        width     = evaluateToFloat(self.registry,self.width)*_Units.unit(self.wunit)

        transforms = []
        meshes     = []

        if self.axis in [self.Axis.kXAxis, self.Axis.kYAxis, self.Axis.kZAxis]:
            for v,i in zip(_np.arange(-width*(nreplicas-1)*0.5,  width*(nreplicas+1)*0.5, width),range(0,nreplicas,1)) :
                rot   = [0,0,0]
                trans = [0,0,0]
                # use enum as index in list
                if self.axis <= 3:
                    trans[self.axis-1] = v

                transforms.append([rot,trans])
                meshes.append(self.logicalVolume.mesh)

                # if daughter contains a replica
                if len(self.logicalVolume.daughterVolumes) == 1 :
                    if isinstance(self.logicalVolume.daughterVolumes[0], ReplicaVolume) :
                        [daughter_meshes,daughter_transforms] = self.logicalVolume.daughterVolumes[0].createReplicaMeshes()
                        for m,t in zip(daughter_meshes,daughter_transforms) :
                            meshes.append(m)
                            transforms.append([rot,_np.array(trans)+_np.array(t[1])])  # TBC - t[0] ie daughter rotation is unused / not compounded
        else:
            # rotation type replica
            for v,i in zip(_np.arange(offset, offset+nreplicas*width,width),range(0,nreplicas,1)) :
                if self.axis == self.Axis.kRho:
                    solid = _solid.Tubs(self.name+"_"+self.logicalVolume.solid.name+"_"+str(i),
                                        v,
                                        v+width,
                                        self.logicalVolume.solid.pDz,
                                        self.logicalVolume.solid.pSPhi,
                                        self.logicalVolume.solid.pDPhi,
                                        self.logicalVolume.registry,
                                        self.logicalVolume.solid.lunit,
                                        self.logicalVolume.solid.aunit,
                                        self.logicalVolume.solid.nslice,
                                        False)
                    mesh   = _Mesh(solid)
                    meshes.append(mesh)
                    transforms.append([[0,0,0],[0,0,0]])

                elif self.axis == self.Axis.kPhi :
                    meshes.append(self.logicalVolume.mesh)
                    transforms.append([[0,0,v],[0,0,0]])
            
        return [meshes,transforms]

    def getPhysicalVolumes(self):
        """
        return a list of temporary (ie not added to the relevant registry) PhysicalVolume instances
        with appropriate transforms including any daughter ReplicaVolumes.

        The exception is for kRho axis where new unique solids and logical volumes are required.
        Therefore, these are added to the registry and inadvertently to the mother LV as PVS.
        """
        result = []
        transforms = []
        import pyg4ometry.gdml.Units as _Units
        from pyg4ometry.gdml.Defines import evaluateToFloat
        from pyg4ometry.geant4 import PhysicalVolume
        from pyg4ometry.geant4 import LogicalVolume

        nreplicas = int(evaluateToFloat(self.registry, self.nreplicas))
        offset = evaluateToFloat(self.registry, self.offset) * _Units.unit(self.ounit)
        width = evaluateToFloat(self.registry, self.width) * _Units.unit(self.wunit)

        if self.axis in [self.Axis.kXAxis, self.Axis.kYAxis, self.Axis.kZAxis]:
            for v, i in zip(_np.arange(-width * (nreplicas - 1) * 0.5, width * (nreplicas + 1) * 0.5, width), range(0, nreplicas, 1)):
                rot = [0, 0, 0]
                trans = [0, 0, 0]
                # use enum as index in list
                if self.axis <= 3:
                    trans[self.axis - 1] = v

                aPV = PhysicalVolume(rot, trans,
                                 self.logicalVolume,
                                 self.name + "_replica_"+str(i),
                                 self.motherVolume,
                                 self.registry,
                                 addRegistry=False)
                result.append(aPV)
                transforms.append([rot, trans])

                # if daughter contains a replica
                if len(self.logicalVolume.daughterVolumes) == 1:
                    if isinstance(self.logicalVolume.daughterVolumes[0], ReplicaVolume):
                        daughterPVs,daughterTransforms = self.logicalVolume.daughterVolumes[0].getPhysicalVolumes()
                        for pv, t in zip(daughterPVs, daughterTransforms):
                            # compound transform to mother's frame
                            compoundRot = _np.array(rot)*_np.array(t[0])
                            compoundTra = _np.array(trans) + _np.array(t[1])
                            pv.rotation = compoundRot
                            pv.position = compoundTra
                            result.append(pv)
                            transforms.append([compoundRot, compoundTra])

        elif self.axis == self.Axis.kRho:
            # rotation type replica
            for v, i in zip(_np.arange(offset, offset + nreplicas * width, width), range(0, nreplicas, 1)):
                # create a unique temporary solid and therefore logical volume
                solid = _solid.Tubs(self.name + "_" + self.logicalVolume.solid.name + "_replica_" + str(i),
                                    v,
                                    v + width,
                                    self.logicalVolume.solid.pDz,
                                    self.logicalVolume.solid.pSPhi,
                                    self.logicalVolume.solid.pDPhi,
                                    self.logicalVolume.registry,
                                    self.logicalVolume.solid.lunit,
                                    self.logicalVolume.solid.aunit,
                                    self.logicalVolume.solid.nslice,
                                    addRegistry=True) # we define a new unique solid, so we do need to store it
                anLV = LogicalVolume(solid,
                                     self.logicalVolume.material,
                                     self.logicalVolume.name + "_replica_"+str(i),
                                     self.registry,
                                     addRegistry=True) # unique LV - need ot add
                rot, trans = [0, 0, 0], [0, 0, 0]
                aPV = PhysicalVolume(rot, trans,
                                     anLV,
                                     self.name + "_replica_" + str(i),
                                     self.motherVolume,
                                     self.registry,
                                     addRegistry=False)
                result.append(aPV)
                transforms.append([rot,trans])

        elif self.axis == self.Axis.kPhi:
            for v, i in zip(_np.arange(offset, offset + nreplicas * width, width), range(0, nreplicas, 1)):
                rot, trans = [0,0,v], [0,0,0]
                aPV = PhysicalVolume(rot, trans,
                                     self.logicalVolume,
                                     self.name + "_replica_" + str(i),
                                     self.motherVolume,
                                     self.registry,
                                     addRegistry=False)
                result.append(aPV)
                transforms.append([rot, trans])

        return result,transforms

    def __repr__(self) :
        return 'Replica volume : '+self.name+' '+str(self.axis)+' '+str(self.nreplicas)+' '+str(self.offset)+' '+str(self.width)

    def extent(self, includeBoundingSolid = True):
        _log.info('ReplicaVolume.extent> %s' %(self.name))

        vMin = [1e99, 1e99, 1e99]
        vMax = [-1e99, -1e99, -1e99]

        for trans, mesh in zip(self.transforms, self.meshes) :
            # transform daughter meshes to parent coordinates
            dvmrot = _trans.tbxyz2matrix(trans[0])
            dvtra = _np.array(trans[1])

            [vMinDaughter, vMaxDaughter] = mesh.getBoundingBox()

            vMinDaughter = (dvmrot.dot(vMinDaughter) + dvtra)
            vMaxDaughter = (dvmrot.dot(vMaxDaughter) + dvtra)


            if vMaxDaughter[0] > vMax[0] :
                vMax[0] = vMaxDaughter[0]
            if vMaxDaughter[1] > vMax[1] :
                vMax[1] = vMaxDaughter[1]
            if vMaxDaughter[2] > vMax[2] :
                vMax[2] = vMaxDaughter[2]

            if vMinDaughter[0] < vMin[0] :
                vMin[0] = vMinDaughter[0]
            if vMinDaughter[1] < vMin[1] :
                vMin[1] = vMinDaughter[1]
            if vMinDaughter[2] < vMin[2] :
                vMin[2] = vMinDaughter[2]

        return [vMin,vMax]
