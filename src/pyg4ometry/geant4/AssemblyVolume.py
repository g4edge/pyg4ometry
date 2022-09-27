import pyg4ometry as _pyg4ometry
import pyg4ometry.transformation as _trans
import pyg4ometry.geant4.solid as _solid
from   pyg4ometry.visualisation  import Mesh as _Mesh

import numpy as _np
import logging as _log
from collections import defaultdict as _defaultdict
import copy as _copy

class AssemblyVolume(object):
    """
    AssemblyVolume : similar to a logical volume but does not have a sense of
    shape, material or field
    :param name: of assembly volume
    :type name: str
    :param registry: 
    :type registry: 
    :param addRegistry: 
    :type addRegistry: bool
    """
    def __init__(self, name, registry=None, addRegistry=True) :
        super(AssemblyVolume, self).__init__()
        self.type            = "assembly"
        self.name            = name 
        self.daughterVolumes = []
        self._daughterVolumesDict = {}
        self.registry = registry
        if addRegistry:
            registry.addLogicalVolume(self)

        self.overlapChecked = False
            
    def __repr__(self):
        return 'Logical volume : '+self.name

    def add(self, physicalVolume):
        self.daughterVolumes.append(physicalVolume)
        self._daughterVolumesDict[physicalVolume.name] = physicalVolume

    def _getDaughterMeshesByName(self, name):
        pv = self._daughterVolumesDict[name]
        return self._getPVMeshes(pv)

    def _getDaughterMeshesByIndex(self, index):
        pv = self.daughterVolumes[index]
        return self._getPVMeshes(pv)

    def _getDaughterMeshes(self):
        """
        Get daughter meshes for overlap checking.
        return [daughterMesh,..],[daughterBoundingMesh,..][daughterName,...]
        """
        transformedMeshes = []
        transformedBoundingMeshes = []
        transformedMeshesNames = []
        for pv in self.daughterVolumes:
            tm,tbm,tmn = self._getPVMeshes(pv)
            transformedMeshes.extend(tm)
            transformedBoundingMeshes.extend(tbm)
            transformedMeshesNames.extend(tmn)

        return transformedMeshes, transformedBoundingMeshes, transformedMeshesNames

    def _getPVMeshes(self, pv):
        """
        Can technically return more than one mesh if the daughter is also an assembly.
        """
        transformedMeshes = []
        transformedBoundingMeshes = []
        transformedMeshesNames = []

        dlv = pv.logicalVolume
        if type(dlv) is AssemblyVolume:
            m, bm, nm = dlv._getDaughterMeshes()
            nm = [self.name + "_" + pv.name + "_" + n for n in nm]
        else:
            # assume type is LogicalVolume
            m  = [dlv.mesh.localmesh.clone()]
            bm = [dlv.mesh.localboundingmesh.clone()]
            nm = [self.name + "_" + pv.name]

        aa = _trans.tbxyz2axisangle(pv.rotation.eval())
        s = None
        if pv.scale:
            s = pv.scale.eval()
        t = pv.position.eval()
        for mesh, boundingmesh, name in zip(m, bm, nm):
            # rotate
            mesh.rotate(aa[0], _trans.rad2deg(aa[1]))
            boundingmesh.rotate(aa[0], _trans.rad2deg(aa[1]))

            # scale
            if s:
                mesh.scale(s)
                boundingmesh.scale(s)

                if s[0] * s[1] * s[2] == 1:
                    pass
                elif s[0] * s[1] * s[2] == -1:
                    mesh = mesh.inverse()
                    boundingmesh.inverse()

            # translate
            mesh.translate(t)
            boundingmesh.translate(t)

            transformedMeshes.append(mesh)
            transformedBoundingMeshes.append(boundingmesh)
            transformedMeshesNames.append(name)

        return transformedMeshes, transformedBoundingMeshes, transformedMeshesNames

    def _getPhysicalDaughterMesh(self, pv, warn=True):
        """
        Return a (cloned from the lv) mesh of a given pv with rotation,scale,
        translation evaluated.
        """
        # cannot currently deal with replica, division and parametrised
        if pv.type != "placement":
            if warn:
                print("Cannot generate specific daughter mesh for replica, division, parameterised")
            return None
        if pv.logicalVolume.type == "assembly":
            mesh = pv.logicalVolume.getAABBMesh()
        else:
            mesh = pv.logicalVolume.mesh.localmesh.clone()

        # rotate
        aa = _trans.tbxyz2axisangle(pv.rotation.eval())
        mesh.rotate(aa[0], _trans.rad2deg(aa[1]))

        # scale
        if pv.scale:
            s = pv.scale.eval()
            mesh.scale(s)

            if s[0] * s[1] * s[2] == 1:
                pass
            elif s[0] * s[1] * s[2] == -1:
                mesh = mesh.inverse()

        # translate
        t = pv.position.eval()
        mesh.translate(t)
        return mesh

    def clipGeometry(self, newSolid, rotation = (0,0,0), position=(0,0,0), runit="rad", punit="mm", replace=False, depth=0,
                     solidUsageCount = _defaultdict(int),
                     lvUsageCount    = _defaultdict(int)):

        """
        Clip the geometry to newSolid, placed with rotation and position.
        """

        # increment the recursion depth
        depth += 1

        import pyg4ometry.gdml.Units as _Units
        puval = _Units.unit(punit)
        ruval = _Units.unit(runit)
        if depth == 1:
            position = [puval*e for e in position]
            rotation = [ruval*e for e in rotation]

        clipMesh = _Mesh(newSolid[depth-1]).localmesh

        outside =[]
        intersections = []
        inside = []

        intersectionsPV = []
        insidePV = []

        for pv in self.daughterVolumes:
            pvmesh      = self._getPhysicalDaughterMesh(pv)

            pvInterMesh = pvmesh.intersect(clipMesh)
            pvDiffMesh  = pvmesh.subtract(pvInterMesh)

            # print(i,pvmesh.vertexCount(),pvInterMesh.vertexCount(), pvInterMesh.hash(), pvmesh.hash())
            # check intersection mesh (completely outside, intersects, completely inside)
            if pvInterMesh.isNull() :
                # print(i,pv.position.eval(),pvmesh.vertexCount(),pvInterMesh.vertexCount(), pvInterMesh.hash(), pvmesh.hash(),"pv solid is outside")
                outside.append(pvmesh)
            elif not pvInterMesh.isNull() : # intersection of new solid and existing solid
                # print(i,pv.position.eval(),pvmesh.vertexCount(),pvInterMesh.vertexCount(), pvInterMesh.hash(), pvmesh.hash(),"pv solid is intersecting")
                intersections.append(pvInterMesh)
                intersectionsPV.append(pv)
                if pvDiffMesh.isNull()  : # completely inside
                    # print(i,pv.position.eval(),pvmesh.vertexCount(),pvInterMesh.vertexCount(), pvInterMesh.hash(), pvmesh.hash(),"pv solid is inside")
                    inside.append(pvmesh)
                    insidePV.append(pv)


        self.daughterVolumes = insidePV
        self._daughterVolumesDict = {pvi.name:pvi for pvi in insidePV}

        for pvi in intersectionsPV :
            mat      = _trans.tbxyz2matrix(rotation)
            matInv    = _np.linalg.inv(mat)
            matPV    = _trans.tbxyz2matrix(pvi.rotation.eval())
            matPVInv = _np.linalg.inv(matPV)

            newRotation = _trans.matrix2tbxyz(mat.dot(matPVInv))
            newPosition = list(matPV.dot(pvi.position.eval()) + position)

            lvUsageCount[pvi.name] += 1
            pvNewName = pvi.name + "_n_" + str(lvUsageCount[pvi.name])

            if pvi.logicalVolume.type == "assembly" :
                lvNew = _pyg4ometry.geant4.AssemblyVolume(pvNewName,pvi.logicalVolume.registry)
            else :
                lvNew = _pyg4ometry.geant4.LogicalVolume(pvi.logicalVolume.solid,
                                                         pvi.logicalVolume.material,
                                                         pvNewName,
                                                         pvi.logicalVolume.registry)
            for dv in pvi.logicalVolume.daughterVolumes :
                lvNew.daughterVolumes.append(_copy.copy(dv))

            lvNew.clipGeometry(newSolid,newRotation,newPosition, runit, punit, True, depth, lvUsageCount, solidUsageCount)

            pvi.logicalVolume = lvNew
            self.daughterVolumes.append(pvi)
            self._daughterVolumesDict[pvi.name] = pvi


        return

    def extent(self, includeBoundingSolid=True) :
        _log.info('AssemblyVolume.extent> %s ' % (self.name))

        vMin = [1e99,1e99,1e99]
        vMax = [-1e99,-1e99,-1e99]

        for dv in self.daughterVolumes:
            [vMinDaughter, vMaxDaughter] = dv.extent()

            if vMaxDaughter[0] > vMax[0]:
                vMax[0] = vMaxDaughter[0]
            if vMaxDaughter[1] > vMax[1]:
                vMax[1] = vMaxDaughter[1]
            if vMaxDaughter[2] > vMax[2]:
                vMax[2] = vMaxDaughter[2]

            if vMinDaughter[0] < vMin[0]:
                vMin[0] = vMinDaughter[0]
            if vMinDaughter[1] < vMin[1]:
                vMin[1] = vMinDaughter[1]
            if vMinDaughter[2] < vMin[2]:
                vMin[2] = vMinDaughter[2]

        return [vMin, vMax]

    def depth(self, depth=0):
        '''
        Depth for LV-PV tree
        '''

        depth = depth + 1

        depthList = [depth]
        for dv in self.daughterVolumes :
            depthList.append(dv.logicalVolume.depth(depth))

        return max(depthList)

    def getAABBMesh(self):
        '''return CSG.core (symmetric around the origin) axis aligned bounding box mesh'''
        extent = self.extent()

        x = max(abs(extent[0][0]),extent[1][0])
        y = max(abs(extent[0][1]),extent[1][1])
        z = max(abs(extent[0][2]),extent[1][2])

        bs = _solid.Box(self.name+"_aabb",x,y,z,self.registry,"mm",False)

        bm = _Mesh(bs)

        return bm.localmesh

    def logicalVolume(self, material = "G4_Galactic", solidName = "worldSolid"):
        """
        Return an logical volume of this this assembly volume, in effect
        adding a cuboid solid and material of this logical volume, retaining
        all of the relative daughter placements.
        """

        import pyg4ometry.geant4.LogicalVolume as _LogicalVolume


        extent = self.extent(True)

        # create world box
        solid = _pyg4ometry.geant4.solid.Box("worldSolid",
                           2.1 * max([abs(extent[1][0]),abs(extent[0][0])]),
                           2.1 * max([abs(extent[1][1]),abs(extent[0][1])]),
                           2.1 * max([abs(extent[1][2]),abs(extent[0][2])]),
                           self.registry, "mm")

        lv = _LogicalVolume(solid, material,"logical_"+self.name, self.registry )

        for dv in self.daughterVolumes:
            lv.add(dv)

        return lv

    def makeWorldVolume(self, material = "G4_Galactic"):

        wl = self.logicalVolume(material, "worldSolid")

        self.registry.setWorld(wl.name)

        return wl
    def dumpStructure(self, depth=0):
        print(depth*"-"+self.name+" (lv)")

        for d in self.daughterVolumes :
            print(2*depth*"-"+d.name+" (pv)")
            d.logicalVolume.dumpStructure(depth+2)