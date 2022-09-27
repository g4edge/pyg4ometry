from   pyg4ometry.pycsg.geom import Vector as _Vector
from   pyg4ometry.pycsg.core import CSG    as _CSG
#from   pyg4ometry.gdml.Defines import Auxiliary as _Auxiliary

import pyg4ometry as _pyg4ometry
from   pyg4ometry import config as _config
from   pyg4ometry.visualisation  import Mesh            as _Mesh
from   pyg4ometry.visualisation  import Convert         as _Convert
from   pyg4ometry.visualisation  import OverlapType     as _OverlapType
from . import solid as _solid
from . import _Material as _mat
import pyg4ometry.transformation as _trans
import vtk as _vtk

from collections import defaultdict as _defaultdict
import numpy   as _np
import logging as _log
import copy as _copy


def _solid2tessellated(solid):
    pycsg_mesh = solid.mesh()

    # Use VTK to reduce all polygons to triangles
    # as CSG operations can produce arbitrary polygons
    # which cannot be used in Tessellated Solid
    meshVTKPD = _Convert.pycsgMeshToVtkPolyData(pycsg_mesh)
    vtkFLT = _vtk.vtkTriangleFilter()
    vtkFLT.AddInputData(meshVTKPD)
    vtkFLT.Update()
    triangular = vtkFLT.GetOutput()

    meshTriangular = []
    for i in range(triangular.GetNumberOfCells()):
        pts = triangular.GetCell(i).GetPoints()
        vertices = [pts.GetPoint(i) for i in range(pts.GetNumberOfPoints())]
        # The last 3-tuple is a dummy normal to make it look like STL data
        meshTriangular.append((vertices, (None, None, None)))

    name = solid.name + "_asTesselated"
    reg = solid.registry
    mesh_type = _solid.TessellatedSolid.MeshType.Stl
    tesselated_solid = _solid.TessellatedSolid(name, meshTriangular, reg, meshtype=mesh_type)

    return tesselated_solid


class LogicalVolume(object):
    """
    LogicalVolume : G4LogicalVolume

    :param solid:
    :type solid:
    :param material:
    :type material:
    :param name:
    :type name: str
    :param registry:
    :type registry:
    :param addRegistry:
    :type addRegistry: bool

    """
    def __init__(self, solid, material, name, registry=None, addRegistry=True, **kwargs):
        super(LogicalVolume, self).__init__()

        self.type  = "logical"
        self.solid = solid
 
        if isinstance(material, _mat.Material):
            self.material = material
            self.material.set_registry(registry, dontWarnIfAlreadyAdded=True)
        elif isinstance(material, str):
            # If the material is registered already, use it
            if registry and material in registry.materialDict:
                self.material = registry.materialDict[material]
            else:  # This will work out if it is a valid NIST and set the type appropriately
                self.material = _mat.MaterialPredefined(name=material, registry=registry)
        else:
            raise ValueError("Unsupported type for material: {}".format(type(material)))

        self.name            = name
        self.daughterVolumes = []
        self._daughterVolumesDict = {}
        self.bdsimObjects    = []
        if _config.doMeshing:
            self.reMesh()
        self.auxiliary = []
        self.addAuxiliaryInfo(kwargs.get("auxiliary", None))

        # registry logic
        if registry and addRegistry:
            registry.addLogicalVolume(self)
        self.registry = registry

        # efficient overlap checking
        self.overlapChecked = False

    def __repr__(self):
        return 'Logical volume : '+self.name+' '+str(self.solid)+' '+str(self.material)

    def reMesh(self, recursive=False):
        """
        Regenerate the visualisation for this logical volume.
        """
        try:
            self.mesh = _Mesh(self.solid)
            if recursive:
                for d in self.daughterVolumes:
                    d.logicalVolume.reMesh(recursive)
        except _pyg4ometry.exceptions.NullMeshError:
            self.mesh = None
            print("geant4.LogicalVolume> meshing error {}".format(self.name))
        except ValueError:
            self.mesh = None
            print("geant4.LogicalVolume> meshing error {}".format(self.name))

    def add(self, physicalVolume):
        """
        Add physical volume to this logicalVolume

        :param physicalVolume: physical volume to add
        :type physicalVolume: PhysicalVolume, ReplicaVolume, ParameterisedVolume, DivisionVolume
        """
        self.daughterVolumes.append(physicalVolume)
        self._daughterVolumesDict[physicalVolume.name] = physicalVolume

    def addBDSIMObject(self, bdsimobject):
        self.bdsimObjects.append(bdsimobject)

    def _getPhysicalDaughterMesh(self, pv, warn=True):
        """
        Return a (cloned from the lv) mesh of a given pv with rotation,scale,
        translation evaluated.
        """
        # cannot currently deal with replica, division and parametrised
        if  pv.type != "placement":
            if warn:
                print("Cannot generate specific daughter mesh for replica, division, parameterised")
            return None
        # cannot currently deal with assembly
        if  pv.logicalVolume.type == "assembly":
            mesh = pv.logicalVolume.getAABBMesh()
        else :
            mesh = pv.logicalVolume.mesh.localmesh.clone()

        # rotate
        aa = _trans.tbxyz2axisangle(pv.rotation.eval())
        mesh.rotate(aa[0],_trans.rad2deg(aa[1]))

        # scale
        if pv.scale :
            s = pv.scale.eval()
            mesh.scale(s)
            
            if s[0]*s[1]*s[2] == 1 :
                pass
            elif s[0]*s[1]*s[2] == -1 :
                mesh = mesh.inverse()
                
        # translate
        t = pv.position.eval()
        mesh.translate(t)
        return mesh
        
    def cullDaughtersOutsideSolid(self, solid, rotation=None, position=None):
        """
        Given a solid with a placement rotation and position inside this logical
        volume, remove (cull) any daughters that would not lie entirely within it.
        The rotation and position are applied to the solid w.r.t. the frame of this
        logical volume.

        :param rotation: Tait-Bryan angles for rotation of the solid w.r.t. this lv
        :type  rotation: list(float, float, float) or None - 3 values in radians
        :param position: translation of the solid w.r.t. this lv
        :type  position: list(float, float, float) or None - 3 values in mm
        """
        # form temporary mesh of solid in the coordinate frame of this solid
        clipMesh = _Mesh(solid)
        clipMesh = clipMesh.localmesh
        if rotation:
            aa = _trans.tbxyz2axisangle(rotation)
            clipMesh.rotate(aa[0],_trans.rad2deg(aa[1]))
        # no scale supported for this
        if position:
            clipMesh.translate(position)

        toKeep = [] # build up list of bools - don't modify as we iterate on the list
        for pv in self.daughterVolumes:
            pvmesh = self._getPhysicalDaughterMesh(pv)
            if pvmesh is None:
                toKeep.append(True)
                continue # maybe unsupported type - skip

            intersectionMesh = pvmesh.intersect(clipMesh)
            countIM = intersectionMesh.polygonCount()
            countPV = pvmesh.polygonCount()
            if countIM != countPV:
                # either protruding (count!=0) or outside (count==0)
                # keep only ones that are protruding
                toKeep.append(intersectionMesh.polygonCount() != 0)
            else:
                toKeep.append(True)

        self.daughterVolumes = [pv for pv,keep in zip(self.daughterVolumes, toKeep) if keep]
        self._daughterVolumesDict = {pv.name:pv for pv in self.daughterVolumes}

    def replaceSolid(self, newSolid, rotation = (0,0,0), position=(0,0,0), runit="rad", punit="mm") :

        """
        Replace the outer solid with optional position and rotation

        :param newSolid: object to clip the geometry to
        :type newSolid: pyg4ometry.geant4.solid
        :param rotation: Tait-Bryan angles for rotation of the solid w.r.t. this lv
        :type  rotation: list(float, float, float) or None - 3 values in radians
        :param position: translation of the solid w.r.t. this lv
        :type  position: list(float, float, float) or None - 3 values in mm
        :param runit: angular unit for rotation (rad,deg)
        :type runit: str
        :param punit: length unit for position (m,mm,km)
        :type punit: str
        """
        # need to determine type or rotation and position, as should be Position or Rotation type
        from pyg4ometry.gdml import Defines as _Defines

        import pyg4ometry.gdml.Units as _Units
        puval = _Units.unit(punit)
        ruval = _Units.unit(runit)

        self.solid = newSolid
        self.reMesh(False)

        matNew = _np.linalg.inv(_trans.tbxyz2matrix(_np.array(rotation)*ruval))
        posNew = _np.array(position)*puval

        for pv in self.daughterVolumes:
            matDaughter = _trans.tbxyz2matrix(pv.rotation.eval())
            posDaughter = pv.position.eval()

            newRotation = _trans.matrix2tbxyz(matNew.dot(matDaughter))
            newPosition = _trans.tbxyz2matrix(_np.array(rotation)*ruval).dot(posDaughter) - _np.array(posNew)

            pv.position = _Defines.Position(pv.name+"_ReplaceSolidPos",newPosition[0],newPosition[1],newPosition[2],"mm",self.registry,False)
            pv.rotation = _Defines.Rotation(pv.name+"_ReplaceSolidRot",newRotation[0],newRotation[1],newRotation[2],"rad",self.registry,False)

    def clipGeometry(self, newSolid, rotation = (0,0,0), position=(0,0,0), runit="rad", punit="mm", replace=False, depth=0,
                     solidUsageCount = _defaultdict(int),
                     lvUsageCount    = _defaultdict(int)):
        """
        Clip the geometry to newSolid, placed with rotation and position.

        :param newSolid: object to clip the geometry to
        :type newSolid: pyg4ometry.geant4.solid
        :param rotation: Tait-Bryan angles for rotation of the solid w.r.t. this lv
        :type  rotation: list(float, float, float) or None - 3 values in radians
        :param position: translation of the solid w.r.t. this lv
        :type  position: list(float, float, float) or None - 3 values in mm
        :param runit: angular unit for rotation (rad,deg)
        :type runit: str
        :param punit: length unit for position (m,mm,km)
        :type punit: str
        :param replace: replace the outer solid or not
        :type replace: bool
        :param depth: recursion depth (DO NOT USE)
        :type depth: int
        :param solidUsageCount: solid name dictionary for replacement recursion (DO NOT USE)
        :type solidUsageCount: defaultdict
        :param lvUsageCount: lv name dictionary for replacement recursion (DO NOT USE)
        :type lvUsageCount: defaultdict
        """

        # increment the recursion depth
        depth += 1

        clipMesh = _Mesh(newSolid[depth-1]).localmesh

        import pyg4ometry.gdml.Units as _Units
        puval = _Units.unit(punit)
        ruval = _Units.unit(runit)
        if depth == 1:
            position = [puval*e for e in position]
            rotation = [ruval*e for e in rotation]

        if replace :
            # Replace LV solid
            solid1 = self.solid
            solid2 = newSolid[depth-1]

            solidUsageCount[solid1.name] += 1
            solidNewName = solid1.name + "_n_" + str(solidUsageCount[solid1.name])

            rotationInv = _trans.matrix2tbxyz(_np.linalg.inv(_trans.tbxyz2matrix(rotation)))
            positionInv = list(-_np.array(position))

            _trans.matrix2tbxyz(_np.linalg.inv(_trans.tbxyz2matrix(rotation)))
            solidIntersection = _pyg4ometry.geant4.solid.Intersection(solidNewName,
                                                                      solid1,
                                                                      solid2,
                                                                      [rotationInv,positionInv],
                                                                      self.registry,True)

            self.solid = solidIntersection
            self.reMesh(False)

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
                dv = _copy.copy(dv)
                dv.name = pvNewName+"_"+dv.name
                lvNew.daughterVolumes.append(dv)
                lvNew._daughterVolumesDict[dv.name] = dv

            lvNew.clipGeometry(newSolid,newRotation,newPosition, runit, punit, True, depth, lvUsageCount, solidUsageCount)

            pvi.logicalVolume = lvNew
            self.daughterVolumes.append(pvi)
            self._daughterVolumesDict[pvi.name] = pvi


        return

    def changeSolidAndTrimGeometry(self, newSolid, rotation=(0,0,0), position=(0,0,0), runit="rad", punit="mm"):
        """
        Change the solid of this logical volume, remove any daughters that will lie outside
        it, and form new Boolean intersection solids for any daughters that cross the boundary
        (intersect) it. The rotation and translation are with respect to the original frame and
        all daughters will now be replaced with respect to the new frame. Therefore, that same
        rotation and translation should be use to re-place this logical volume if desired. The
        default is none though, so the frame would nominally remain the same.

        :param newSolid: new solid to use for this logical volume
        :type  newSolid: any of pyg4ometry.geant4.solid
        :param rotation: Tait-Bryan rotation for the new solid w.r.t. old frame (i.e. current lv)
        :type  rotation: list(float, float, float) or None - 3 values in radians
        :param position: translation for the new solid w.r.t. old frame (i.e. current lv)
        :type  position: list(float, float, float) or None - 3 values in mm
        """
        # first cull anything entirely outside

        # prepare clipping mesh from the newSolid
        clipMesh = _Mesh(newSolid)
        clipMesh = clipMesh.localmesh
        if rotation:
            aa = _trans.tbxyz2axisangle(rotation)
            clipMesh.rotate(aa[0], _trans.rad2deg(aa[1]))
        if position:
            clipMesh.translate(position)

        # form intersection between existing lv solid and new solid

        # this is reproduced from cullDaughters, but only a small amount - we benefit by not having
        # to regenerate the meshes again for subsequent operations (< memory, < time)
        toKeep = []  # build up list of bools - don't modify as we iterate on the list
        intersectionMeshes = {}
        for pv in self.daughterVolumes:
            pvmesh = self._getPhysicalDaughterMesh(pv)
            if pvmesh is None:
                toKeep.append(True)
                continue  # maybe unsupported type - skip

            intersectionMesh = pvmesh.intersect(clipMesh)
            countIM = intersectionMesh.polygonCount()
            countPV = pvmesh.polygonCount()
            if countIM != countPV:
                # either protruding (count!=0) or outside (count==0)
                # keep only ones that are protruding
                toKeep.append(intersectionMesh.polygonCount() != 0)
                #toKeep.append(True) # for debugging only
            else:
                toKeep.append(True)
            # cache the intersection mesh for ones we're keeping
            if toKeep[-1]:
                intersectionMeshes[pv] = intersectionMesh
        # do the culling
        self.daughterVolumes = [pv for pv, keep in zip(self.daughterVolumes, toKeep) if keep]
        self._daughterVolumesDict = {pv.name: pv for pv in self.daughterVolumes}

        if len(self.daughterVolumes) == 0:
            print("Warning> no remaining daughters")
            # if there are no daughters remaining, then there's no need to update
            # the placement transforms
            self.solid = newSolid
            return
        # else some daughters remain - check them - if they intersect (judged by the mesh intersection)
        # then reform their solids to  include that intersection

        from pyg4ometry.gdml.Defines import Position, Rotation, upgradeToVector
        from pyg4ometry.geant4.solid import Intersection
        from pyg4ometry import transformation as _transformation

        p, r = position, rotation
        def _updateRotoTranslation(pv):
            mtraInv = _transformation.tbxyz2matrix(r)
            mtra    = _np.linalg.inv(mtraInv)
            tra     = _np.array(p)

            pvmrot = _np.linalg.inv(_transformation.tbxyz2matrix(pv.rotation.eval()))
            if pv.scale:
                print("Warning> this does not work with scale")
                pvmsca = _np.diag(pv.scale.eval())
            else:
                pvmsca = _np.diag([1, 1, 1])
            pvtra = _np.array(pv.position.eval())

            # pv compound transform
            new_mtra = mtra.dot(pvmrot)
            new_tra = (_np.array(mtraInv.dot(pvtra)) - tra)
            new_mtra_tb = _transformation.matrix2tbxyz(new_mtra)
            pv.rotation = Rotation(newSolid.name + "_" + pv.name + "_rot",
                                   new_mtra_tb[0], new_mtra_tb[1], new_mtra_tb[2],
                                   "rad", pv.registry)
            pv.position = Position(newSolid.name + "_" + pv.name + "_pos",
                                   new_tra[0], new_tra[1], new_tra[2],
                                   "mm", pv.registry)
            return

        def _getInverseTranslation(pv):
            invTra = -1 * _np.array(pv.position.eval())
            mtra = _transformation.tbxyz2matrix(pv.rotation.eval())
            result = list(mtra.dot(invTra))
            return result

        daughterAssemblies = []
        lvUsageCount = _defaultdict(int)
        solidUsageCount = _defaultdict(int)
        for pv in self.daughterVolumes:
            pvmesh = self._getPhysicalDaughterMesh(pv, warn=False)
            if pvmesh is None:
                if pv.logicalVolume.type == "assembly":
                    daughterAssemblies.append(pv)
                continue  # maybe unsupported type - skip

            intersectionMesh = intersectionMeshes[pv]
            if intersectionMesh.polygonCount() == 0:
                continue # shouldn't happen as we've already culled daughters entirely outside, but nonetheless
            elif intersectionMesh.polygonCount() == pvmesh.polygonCount():
                # intersection mesh exactly the same as pvmesh, so pv lies entirely
                # inside the solid - just update placement transform
                _updateRotoTranslation(pv)
            else:
                # by elimination it's protruding
                _updateRotoTranslation(pv)
                # We keep the 1st object in the intersection the original so its frame
                # is preserved. We therefore use the inverse of the (new and updated)
                # placement transform of this daughter
                #invRot, invTra = _getInverseRotoTranslation(pv)
                invTra = _getInverseTranslation(pv)
                oldLV = pv.logicalVolume
                oldLVSolid = oldLV.solid
                solidUsageCount[oldLVSolid] += 1
                newSolidName = oldLVSolid.name + "_n_" + newSolid.name + "_" + str(solidUsageCount[oldLVSolid])
                newDSolid = Intersection(newSolidName,
                                         oldLVSolid,
                                         newSolid,
                                         [pv.rotation.eval(), invTra],
                                         self.registry)
                # prepare a new lv as we are changing the solid in this pv only
                lvUsageCount[oldLV] += 1
                newLVName = oldLV.name + "_n_" + str(lvUsageCount[oldLV])
                newLV = LogicalVolume(newDSolid, oldLV.material, newLVName, pv.registry)
                newLV.daughterVolumes      = oldLV.daughterVolumes
                newLV.overlapChecked       = oldLV.overlapChecked
                newLV._daughterVolumesDict = oldLV._daughterVolumesDict
                newLV.bdsimObjects         = oldLV.bdsimObjects
                newLV.auxiliary = oldLV.auxiliary

                pv.logicalVolume = newLV

        # now go back to the assemblies...

        # finally update the solid
        self.solid = newSolid
        self.reMesh(False)


    def checkOverlaps(self, recursive=False, coplanar=True, debugIO=False, printOut=True, nOverlapsDetected=[0]):
        """
        Check based on the meshes in each logical volume if there are any geometrical overlaps. By
        default, overlaps are checked between daughter volumes and with the mother volume itself (protrusion).
        Coplanar overlaps may also be checked (default on).

        Print out will be given for any overlaps detected and the visualiser will show the
        colour coded overlaps.

        :param recursive: bool - Whether to descend into the daughter volumes and check their contents also.
        :param coplanar: bool - Whether to check for coplanar overlaps
        :param debugIO: bool - Print out for every check made
        :param printOut: bool - (internal) Whether to print out a summary of N overlaps detected
        :param nOverlapsDetected: [int] - (internal) counter for recursion - ignore
        """
        from pyg4ometry.geant4 import IsAReplica as _IsAReplica
        if printOut:
            print("LogicalVolume.checkOverlaps> ",self.name)

        # return if overlaps already checked
        if self.overlapChecked:
            if debugIO:
                print("Overlaps already checked - skipping")
            return

        if _IsAReplica(self):
            self.daughterVolumes[0]._checkInternalOverlaps(debugIO, nOverlapsDetected)
            self.overlapChecked = True
            return

        # local meshes
        transformedMeshes = []
        transformedBoundingMeshes = []
        transformedMeshesNames = []

        # transform meshes (and bounding meshes) into logical volume frame
        for pv in self.daughterVolumes:
            # cannot currently deal with replica, division and parametrised
            # but at least their mother will be checked for collisions with other ones at the same level
            # in the case of say replicas
            if  pv.type != "placement":
                continue
            _log.info('LogicalVolume.checkOverlaps> %s' % (pv.name))

            # an assembly will generate more than one mesh, but a regular LV just one - in either case
            # use a list of meshes for applying transforms into this LV frame
            tempMeshes         = []
            tempBoundingMeshes = []
            tempMeshesNames    = []
            if  pv.logicalVolume.type == "assembly":
                tempMeshes,tempBoundingMeshes,tempMeshesNames = pv.logicalVolume._getDaughterMeshes()
                tempMeshesNames = [pv.name+"_"+name for name in tempMeshesNames]
            else:
                # must be of type LogicalVolume
                tempMeshes         = [pv.logicalVolume.mesh.localmesh.clone()]
                tempBoundingMeshes = [pv.logicalVolume.mesh.localboundingmesh.clone()]
                tempMeshesNames    = [pv.name]

            aa = _trans.tbxyz2axisangle(pv.rotation.eval())
            s = None
            if pv.scale:
                s = pv.scale.eval()
            t = pv.position.eval()
            for mesh, boundingmesh, name in zip(tempMeshes, tempBoundingMeshes, tempMeshesNames):
                # rotate
                mesh.rotate(aa[0],_trans.rad2deg(aa[1]))
                boundingmesh.rotate(aa[0],_trans.rad2deg(aa[1]))

                # scale
                if s :
                    mesh.scale(s)
                    boundingmesh.scale(s)

                    if s[0]*s[1]*s[2] == 1 :
                        pass
                    elif s[0]*s[1]*s[2] == -1 :
                        mesh = mesh.inverse()
                        boundingmesh.inverse()

                # translate
                mesh.translate(t)
                boundingmesh.translate(t)
            
                transformedMeshes.append(mesh)
                transformedBoundingMeshes.append(boundingmesh)
                transformedMeshesNames.append(name)

        # overlap daughter pv checks
        for i in range(0,len(transformedMeshes)):
            for j in range(i+1,len(transformedMeshes)):
                if debugIO :
                    print(f"LogicalVolume.checkOverlaps> daughter-daughter bounding mesh intersection test: {transformedMeshesNames[i]} {transformedMeshesNames[j]}")

                # first check if bounding mesh intersects
                cullIntersection = transformedBoundingMeshes[i].intersect(transformedBoundingMeshes[j])
                if cullIntersection.vertexCount() == 0 :
                    continue

                # bounding meshes collide, so check full mesh properly
                interMesh = transformedMeshes[i].intersect(transformedMeshes[j])
                _log.info('LogicalVolume.checkOverlaps> full daughter-daughter intersection test: %d %d %d %d' % (i,j, interMesh.vertexCount(), interMesh.polygonCount()))
                if interMesh.vertexCount() != 0:
                    nOverlapsDetected[0] += 1
                    print(f"\033[1mOVERLAP DETECTED> overlap between daughters of {self.name} \033[0m {transformedMeshesNames[i]} {transformedMeshesNames[j]} {interMesh.vertexCount()}")
                    self.mesh.addOverlapMesh([interMesh,_OverlapType.overlap])

        # coplanar daughter pv checks
        # print 'coplanar with pvs'
        # print "LogicalVolume.checkOverlaps> daughter coplanar overlaps"
        if coplanar:
            for i in range(0,len(transformedMeshes)):
                for j in range(i+1,len(transformedMeshes)):
                    if debugIO :
                        print(f"LogicalVolume.checkOverlaps> full coplanar test between daughters {transformedMeshesNames[i]} {transformedMeshesNames[j]}")

                    # first check if bounding mesh intersects
                    #cullIntersection = transformedBoundingMeshes[i].intersect(transformedBoundingMeshes[j])
                    #cullCoplanar     = transformedBoundingMeshes[i].coplanarIntersection(transformedBoundingMeshes[j])
                    #if cullIntersection.vertexCount() == 0 and cullCoplanar.vertexCount() == 0:
                    #     continue

                    coplanarMesh = transformedMeshes[i].coplanarIntersection(transformedMeshes[j])
                    if coplanarMesh.vertexCount() != 0:
                        nOverlapsDetected[0] += 1
                        print(f"\033[1mOVERLAP DETECTED> coplanar overlap between daughters \033[0m {transformedMeshesNames[i]} {transformedMeshesNames[j]} {coplanarMesh.vertexCount()}")
                        self.mesh.addOverlapMesh([coplanarMesh, _OverlapType.coplanar])

        # protrusion from mother solid
        for i in range(0,len(transformedMeshes)):
            if debugIO :
                print(f"LogicalVolume.checkOverlaps> full daughter-mother intersection test {transformedMeshesNames[i]}")

            cullIntersection = transformedBoundingMeshes[i].subtract(self.mesh.localboundingmesh)
            if cullIntersection.vertexCount() == 0 :
                continue

            interMesh = transformedMeshes[i].subtract(self.mesh.localmesh)
            _log.info('LogicalVolume.checkOverlaps> daughter container %d %d %d' % (i, interMesh.vertexCount(), interMesh.polygonCount()))

            if interMesh.vertexCount() != 0:
                nOverlapsDetected[0] += 1
                print(f"\033[1mOVERLAP DETECTED> overlap with mother \033[0m {transformedMeshesNames[i]} {interMesh.vertexCount()}")
                self.mesh.addOverlapMesh([interMesh,_OverlapType.protrusion])

        # coplanar with solid
        # print 'coplanar with solid'
        if coplanar:
            for i in range(0,len(transformedMeshes)):
                if debugIO :
                    print(f"LogicalVolume.checkOverlaps> full daughter-mother coplanar test {transformedMeshesNames[i]}"),

                #cullCoplanar = self.mesh.localboundingmesh.coplanarIntersection(transformedBoundingMeshes[i])
                #if cullCoplanar.vertexCount() == 0 :
                #    continue

                coplanarMesh = self.mesh.localmesh.coplanarIntersection(transformedMeshes[i]) # Need mother.coplanar(daughter) as typically mother is larger
                if coplanarMesh.vertexCount() != 0:
                    nOverlapsDetected[0] += 1
                    print(f"\033[1mOVERLAP DETECTED> coplanar overlap between daughter and mother\033[0m {transformedMeshesNames[i]} {coplanarMesh.vertexCount()}")
                    self.mesh.addOverlapMesh([coplanarMesh, _OverlapType.coplanar])

        # recursively check entire tree
        if recursive:
            for d in self.daughterVolumes:
                if type(d.logicalVolume) is _pyg4ometry.geant4.AssemblyVolume:
                    continue # no specific overlap check - handled by the PV of an assembly
                # don't make any summary print out for a recursive call
                d.logicalVolume.checkOverlaps(recursive = recursive,
                                              coplanar  = coplanar,
                                              debugIO   = debugIO,
                                              printOut  = False,
                                              nOverlapsDetected=nOverlapsDetected)

        # ok this logical has been checked
        self.overlapChecked = True

        if printOut:
            print(nOverlapsDetected[0]," overlaps detected")

    def setSolid(self, solid) :
        """
        Set (replace) the outer solid. Does not change the placement of the daughters in the volume. If there is a
        transformation then use replaceSolid
        """
        self.solid = solid 
        self.mesh  = _Mesh(self.solid)        

    def makeSolidTessellated(self):
        """
        Make solid tesselated. Sometimes useful when a boolean cannot be visualised in Geant4
        """
        tesselated_lv_solid = _solid2tessellated(self.solid)
        self.setSolid(tesselated_lv_solid)

    def addAuxiliaryInfo(self, auxiliary):
        """
        Add auxilary information to logical volume
        :param auxiliary: auxiliary information for the logical volume
        :type auxiliary: tuple or list
        """
        #if auxiliary is not None and not isinstance(auxiliary, _Auxiliary):
        #    raise ValueError("Auxiliary information must be a gdml.Defines.Auxiliary instance.")
        if isinstance(auxiliary, list) or isinstance(auxiliary, tuple):
            for aux in auxiliary:
                self.addAuxiliaryInfo(aux)
        else:
            if auxiliary:
                self.auxiliary.append(auxiliary)

    def extent(self,includeBoundingSolid = False) :
        """
        Compute the axis aligned extent of the logical volume.

        :param includeBoundingSolid: Include the bounding solid or not
        :type includeBoundingSolid: bool
        """
        _log.info('LogicalVolume.extent> %s ' % (self.name))

        if includeBoundingSolid :
            [vMin, vMax] = self.mesh.getBoundingBox()
            return [vMin, vMax]
        else :
            vMin = [1e99,1e99,1e99]
            vMax = [-1e99,-1e99,-1e99]

        # transform logical solid BB
                
        for dv in self.daughterVolumes :
            [vMinDaughter, vMaxDaughter] = dv.extent(True)

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

        return [vMin, vMax]

    def depth(self, depth = 0):
        '''
        Depth for LV-PV tree
        '''

        depth = depth + 1

        depthList = [depth]
        for dv in self.daughterVolumes :
            depthList.append(dv.logicalVolume.depth(depth))

        return max(depthList)

    def clipSolid(self, lengthSafety=1e-6):
        """
        Assuming the solid of this LV is a Box, reduce its dimensions and re-placement all daughters
        to reduce the box to the minimum (axis-aligned) bounding box. This updates the dimensions of the
        box and the translation of each daughter physical volume.

        :param lengthSafety: safety length
        :type lengthSafety: float
        """
        # loop over daughter volumes to find centres

        eMin = [1e99, 1e99, 1e99]
        eMax = [-1e99, -1e99, -1e99]

        for dv in self.daughterVolumes :
            e = dv.extent()

            if e[0][0] < eMin[0]:
                eMin[0] = e[0][0]
            if e[0][1] < eMin[1]:
                eMin[1] = e[0][1]
            if e[0][2] < eMin[2]:
                eMin[2] = e[0][2]
            if e[1][0] > eMax[0]:
                eMax[0] = e[1][0]
            if e[1][1] > eMax[1]:
                eMax[1] = e[1][1]
            if e[1][2] > eMax[2]:
                eMax[2] = e[1][2]

        eMin = _np.array(eMin)
        eMax = _np.array(eMax)
        diff   = eMax-eMin+lengthSafety
        centre = (eMin + eMax)/2.0

        # move daughter volumes to centre
        for dv in self.daughterVolumes :
            dv.position = dv.position - centre

        # resize outer solid

        # cuboidal solid
        if self.solid.type == "Box":
            self.solid.pX = _pyg4ometry.gdml.Constant(self.solid.name+"_rescaled_x",diff[0],self.registry,True)
            self.solid.pY = _pyg4ometry.gdml.Constant(self.solid.name+"_rescaled_y",diff[1],self.registry,True)
            self.solid.pZ = _pyg4ometry.gdml.Constant(self.solid.name+"_rescaled_z",diff[2],self.registry,True)
        else:
            print("Warning: only Box container volume supported: all daughter placements have been recentred but container solid has not")

        self.mesh.remesh()
        return centre

    def makeLogicalPhysicalNameSets(self):
        """
        Return a set of logical names and physical names used in this logical volume and any daughters.
        This is built up recursively by checking all daughters etc etc.
        """

        logicalNames = set([])
        physicalNames = set([])

        logicalNames.add(self.name)

        for dv in self.daughterVolumes :
            physicalNames.add(dv.name)
            lvn, pvn = dv.logicalVolume.makeLogicalPhysicalNameSets()
            print(lvn)
            logicalNames  = logicalNames.union(lvn)
            physicalNames = physicalNames.union(pvn)
        return logicalNames, physicalNames

    def findLogicalByName(self, name):
        """
        Return a list of LogicalVolume instances used inside this logical volume
        as daughters (at any level inside) with the given name.

        :param name: lv name
        :type name: str

        """
        lv = []
        if self.name.find(name) != -1:
            lv.append(self)
        for d in self.daughterVolumes:
            l = d.logicalVolume.findLogicalByName(name)
            if len(l) != 0 :
                lv.append(l)
        
        return lv

    def makeMaterialNameSet(self):
        """
        Return a set of material names used in this logical volume and any daughters.
        This is built up recursively by checking all daughters etc etc.
        """
        materialNames = set([])

        materialNames.add(self.material.name)

        for dv in self.daughterVolumes:
            dvMaterialNames = dv.logicalVolume.makeMaterialNameSet()
            materialNames = materialNames.union(dvMaterialNames)

        return materialNames

    def assemblyVolume(self):
        """
        Return an assembly volume of this this logical volume, in effect
        removing the solid and material of this logical volume, but retaining
        all of the relative daughter placements.
        """
        import pyg4ometry.geant4.AssemblyVolume as _AssemblyVolume

        # prepend the name because the name might have a pointer in it
        # therefore geant4 will just strip off everything after 0x
        av = _AssemblyVolume("assembly_"+self.name, self.registry)

        for dv in self.daughterVolumes:
            av.add(dv)

        return av

    def makeWorldVolume(self, worldMaterial='G4_Galactic'):
        """
        This will create a container box according to the extents of this logical volume:
        an axis-aligned bounding-box. It will be filled with the given material (predefined
        by name) and assigned as the world volume (outermost) of the registry according
        to this logical volume.
        """
        import pyg4ometry.geant4 as _g4

        extent = self.extent(True)

        # create world box
        ws = _g4.solid.Box("worldSolid",
                           2 * (extent[1][0] - extent[0][0]),
                           2 * (extent[1][1] - extent[0][1]),
                           2 * (extent[1][2] - extent[0][2]),
                           self.registry, "mm")

        wm = _g4.MaterialPredefined(worldMaterial)

        wl = _g4.LogicalVolume(ws, wm, "wl", self.registry)
        cp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], self, self.name+"_pv1", wl, self.registry)

        self.registry.setWorld(wl.name)

    def dumpStructure(self, depth=0):
        print(depth*"-"+self.name+" (lv)")

        for d in self.daughterVolumes :
            print(2*depth*"-"+d.name+" (pv)")
            d.logicalVolume.dumpStructure(depth+2)


