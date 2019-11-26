import pyg4ometry.exceptions
from   pyg4ometry.pycsg.geom import Vector as _Vector
from   pyg4ometry.pycsg.core import CSG    as _CSG
#from   pyg4ometry.gdml.Defines import Auxiliary as _Auxiliary

from   pyg4ometry.visualisation  import Mesh            as _Mesh
from   pyg4ometry.visualisation  import OverlapType     as _OverlapType
import solid                     as                 _solid
import Material                  as                 _mat
import pyg4ometry.transformation as                 _trans
import pyg4ometry.visualisation  as                 _vi
import vtk                       as                 _vtk

import numpy   as   _np
import logging as   _log


def _solid2tessellated(solid):
    pycsg_mesh = solid.pycsgmesh()

    # Use VTK to reduce all polygons to triangles
    # as CSG operations can produce arbitrary polygons
    # which cannot be used in Tessellated Solid
    meshVTKPD = _vi.pycsgMeshToVtkPolyData(pycsg_mesh)
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
    '''
    LogicalVolume : G4LogicalVolume
    :param solid:  
    :param material:
    :param name: 
    :param registry:      
    :param addRegistry: 
    '''

    def __init__(self, solid, material, name, registry=None, addRegistry=True, **kwargs):
        super(LogicalVolume, self).__init__()

        # type 
        self.type            = "logical"
        
        # geant4 required objects 
        self.solid           = solid
 
        if isinstance(material, _mat.Material):
            self.material = material
        elif isinstance(material, str):
            # If the material is registered already, use it
            if registry and material in registry.materialDict:
                self.material = registry.materialDict[material]
            else:  # This will work out if it is a valid NIST and set the type appropriately
                self.material = _mat.MaterialPredefined(name=material)
        else:
            raise ValueError("Unsupported type for material: {}".format(type(material)))

        self.name            = name
        self.daughterVolumes = []

        # geometry mesh
        self.mesh            = _Mesh(self.solid)

        self.auxiliary = []
        self.addAuxiliaryInfo(kwargs.get("auxiliary", None))

        # registry logic
        if registry and addRegistry:
            registry.addLogicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Logical volume : '+self.name+' '+str(self.solid)+' '+str(self.material)

    def add(self, physicalVolume):
        self.daughterVolumes.append(physicalVolume)

    def checkOverlaps(self, recursive = False, debugIO = False) :

        # print 'LogicalVolume.checkOverlaps>'

        # local meshes
        transformedMeshes = []
        transformedBoundingMeshes = []
        transformedMeshesNames = []

        # transform meshes (and bounding meshes) into logical volume frame
        for pv in self.daughterVolumes:

            # cannot currently deal with replica, division and parametrised
            if  pv.type != "placement":
                continue

            _log.info('LogicalVolume.checkOverlaps> %s' % (pv.name))
            mesh = pv.logicalVolume.mesh.localmesh.clone()
            boundingmesh = pv.logicalVolume.mesh.localboundingmesh.clone()

            # rotate 
            aa = _trans.tbxyz2axisangle(pv.rotation.eval())
            mesh.rotate(aa[0],_trans.rad2deg(aa[1]))
            boundingmesh.rotate(aa[0],_trans.rad2deg(aa[1]))

            # scale
            if pv.scale :
                s = pv.scale.eval()
                mesh.scale(s)
                boundingmesh.scale(s)

                if s[0]*s[1]*s[2] == 1 :
                    pass
                elif s[0]*s[1]*s[2] == -1 :
                    mesh = mesh.inverse()
                    boundingmesh.inverse()

            # translate
            t = pv.position.eval()
            mesh.translate(t)
            boundingmesh.translate(t)
            
            transformedMeshes.append(mesh)
            transformedBoundingMeshes.append(boundingmesh)
            transformedMeshesNames.append(pv.name)

        # overlap daughter pv checks
        # print "LogicalVolume.checkOverlaps> daughter overlaps"
        for i in range(0,len(transformedMeshes)) : 
            for j in range(i+1,len(transformedMeshes)) :

                if debugIO :
                    print "LogicalVolume.checkOverlaps> full daughter intersection test",transformedMeshesNames[i],transformedMeshesNames[j]

                # first check if bounding mesh intersects
                cullIntersection = transformedBoundingMeshes[i].intersect(transformedBoundingMeshes[j])
                if cullIntersection.vertexCount() == 0 :
                    continue

                interMesh = transformedMeshes[i].intersect(transformedMeshes[j])
                _log.info('LogicalVolume.checkOverlaps> full inter daughter %d %d %d %d' % (i,j, interMesh.vertexCount(), interMesh.polygonCount()))
                if interMesh.vertexCount() != 0  :
                    print "LogicalVolume.checkOverlaps> overlap between daughters", transformedMeshesNames[i],transformedMeshesNames[j],interMesh.vertexCount()
                    self.mesh.addOverlapMesh([interMesh,_OverlapType.overlap])

        # coplanar daughter pv checks
        # print 'coplanar with pvs'
        # print "LogicalVolume.checkOverlaps> daughter coplanar overlaps"
        for i in range(0,len(transformedMeshes)) :
            for j in range(i+1,len(transformedMeshes)) :

                if debugIO :
                    print "LogicalVolume.checkOverlaps> full coplanar test",transformedMeshesNames[i],transformedMeshesNames[j]

                # first check if bounding mesh intersects
                cullIntersection = transformedBoundingMeshes[i].intersect(transformedBoundingMeshes[j])
                cullCoplanar     = transformedBoundingMeshes[i].coplanarIntersection(transformedBoundingMeshes[j])
                if cullIntersection.vertexCount() == 0 and cullCoplanar.vertexCount() == 0:
                     continue

                coplanarMesh = transformedMeshes[i].coplanarIntersection(transformedMeshes[j])
                if coplanarMesh.vertexCount() != 0:
                    print "LogicalVolume.checkOverlaps> coplanar overlap between daughters",transformedMeshesNames[i],transformedMeshesNames[j],coplanarMesh.vertexCount()
                    self.mesh.addOverlapMesh([coplanarMesh, _OverlapType.coplanar])

        # overlap with solid
        for i in range(0,len(transformedMeshes)) :
            if debugIO :
                print "LogicalVolume.checkOverlaps> full daughter-mother intersection test",transformedMeshesNames[i]

            cullIntersection = transformedBoundingMeshes[i].intersect(self.mesh.localboundingmesh
                                                                      .inverse())
            if cullIntersection.vertexCount() == 0 :
                continue

            interMesh = transformedMeshes[i].intersect(self.mesh.localmesh.inverse())
            _log.info('LogicalVolume.checkOverlaps> daughter container %d %d %d' % (i, interMesh.vertexCount(), interMesh.polygonCount()))

            if interMesh.vertexCount() != 0 :
                print "LogicalVolume.checkOverlaps> overlap with mother",transformedMeshesNames[i],interMesh.vertexCount()
                self.mesh.addOverlapMesh([interMesh,_OverlapType.protrusion])

        # coplanar with solid
        # print 'coplanar with solid'
        for i in range(0,len(transformedMeshes)) :
            if debugIO :
                print "LogicalVolume.checkOverlaps> full daughter-mother coplanar test",transformedMeshesNames[i]

            cullCoplanar = self.mesh.localboundingmesh.coplanarIntersection(transformedBoundingMeshes[i])
            if cullCoplanar.vertexCount() == 0 :
                continue

            coplanarMesh = self.mesh.localmesh.coplanarIntersection(transformedMeshes[i]) # Need mother.coplanar(daughter) as typically mother is larger
            if coplanarMesh.vertexCount() != 0 :
                print "LogicalVolume.checkOverlaps> coplanar overlap between daughter and mother", transformedMeshesNames[i],coplanarMesh.vertexCount()
                self.mesh.addOverlapMesh([coplanarMesh, _OverlapType.coplanar])

        # recusively check entire tree
        if recursive :
            for d in self.daughterVolumes :
                d.logicalVolume.checkOverlaps(recursive=True)

    def setSolid(self, solid) : 
        self.solid = solid 
        self.mesh  = _Mesh(self.solid)        


    def makeSolidTessellated(self):
        tesselated_lv_solid = _solid2tessellated(self.solid)
        self.setSolid(tesselated_lv_solid)

    def addAuxiliaryInfo(self, auxiliary):
        #if auxiliary is not None and not isinstance(auxiliary, _Auxiliary):
        #    raise ValueError("Auxiliary infromation must be a gdml.Defines.Auxiliary instance.")
        if isinstance(auxiliary, list) or isinstance(auxiliary, tuple):
            for aux in auxiliary:
                self.addAuxiliaryInfo(aux)
        else:
            if auxiliary:
                self.auxiliary.append(auxiliary)

    def extent(self,includeBoundingSolid = False) :
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

    def findLogicalByName(self,name) : 
        lv = [] 

        if self.name.find(name) != -1 : 
            lv.append(self)

        
        for d in self.daughterVolumes : 
            l = d.logicalVolume.findLogicalByName(name)
            if len(l) != 0 :
                lv.append(l)
        
        return lv

    def assemblyVolume(self):
        import pyg4ometry.geant4.AssemblyVolume as _AssemblyVolume

        av = _AssemblyVolume(self.name, self.registry, False)

        for dv in self.daughterVolumes :
            av.add(dv)

        return av