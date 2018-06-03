import FreeCAD as _FreeCAD
import Mesh as _Mesh
import MeshPart as _MeshPart

import pygeometry.geant4 as _g4
import pygeometry.vtk as _vtk
import pygeometry.gdml as _gdml

# Recursive mesh writing : FINISHED
# need to make recursive groups and parts : TODO 
# Groups
# 

def GdmlTest(mesh) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box('worldBox',500,500,500)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic','worldLogical')

    facetList = MeshToFacetList(mesh)

    ts = _g4.solid.TesselatedSolid('test',facetList)
    tl = _g4.LogicalVolume(ts,'G4_Cu','tl')
    tp = _g4.PhysicalVolume([0,0,0],[0,0,0],tl,'tp',worldLogical)

    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld('worldLogical')

    # mesh the geometry
    m = worldLogical.pycsgmesh()

    v = _vtk.Viewer()
    v.addPycsgMeshList(m)
    v.view();

def MeshListToGdml(fileStub, meshList, materialMap = {"default":"G4_Cu"}) :
    _g4.registry.clear()
    
    worldSolid      = _g4.solid.Box(fileStub+"_solid",1000,1000,1000)
    worldLogical    = _g4.LogicalVolume(worldSolid,'G4_Galactic',fileStub+"_lv")

    def MeshListToPhysicalVolume(ml) :
        print 'MeshListToPhysicalVolume>',ml[0][0]
        for m in ml :             

            if isinstance(m[1],list) : 
                MeshListToPhysicalVolume(m[1])
            else :
                facetList = MeshToFacetList(m[1])

                # name of mesh/object
                name = m[0]

                # get material
                try : 
                    material = materialMap[name]
                except KeyError :
                    material = materialMap["default"]

                ts = _g4.solid.TesselatedSolid(name+"_solid",facetList)    
                tl = _g4.LogicalVolume(ts,'G4_Cu',name+"_lv")
                tp = _g4.PhysicalVolume([0,0,0],[0,0,0],tl,name+"_pv",worldLogical)

    MeshListToPhysicalVolume(meshList)

    # clip the world logical volume
    worldLogical.setClip();

    # register the world volume
    _g4.registry.setWorld(fileStub+"_lv")

    # mesh the geometry
    m = worldLogical.pycsgmesh()

    v = _vtk.Viewer()
    v.addPycsgMeshList(m)
    v.view();    

    w = _gdml.Writer()
    w.addDetector(_g4.registry)
    w.write(fileStub+".gdml")
    w.writeGmadTester(fileStub+".gmad")        

def MakeMaterialDict(interactive = False) :
    pass

def MeshToFacetList(mesh) : 
    topology = mesh.Topology
    verts    = topology[0]
    wind     = topology[1]

    facet_list = []

    for tri in wind :
        i1 = tri[0]
        i2 = tri[1]
        i3 = tri[2]

        facet_list.append( (((verts[i1][0],verts[i1][1],verts[i1][2]),
                             (verts[i2][0],verts[i2][1],verts[i2][2]),
                             (verts[i3][0],verts[i3][1],verts[i3][2])),(0,1,2)) )

    return facet_list

def ShapeToMesh(shape, scale=None):
    print 'ShapeToMesh>'
    mesh_deviation=0.03 #the smaller the best quality, 1 coarse; 0.03 good compromise :)
    mesh_data = shape.tessellate(mesh_deviation)
    points = mesh_data[0]
    if scale != None:
        points = map(lambda p: p*scale, points)
        return [points,meshdata[1]]
    else :
        return mesh_data

def BodyToMesh(body, xscale = 1.0, yscale = 1.0, zscale = 1.0, debug=False) :
    print 'BodyToMesh>'

    # shape of body
    shape = body.Shape

    # center of mass 
    centreOfMass = shape.CenterOfMass
    
    mat = _FreeCAD.Matrix()
    mat.scale(xscale,yscale,zscale)

    m = _MeshPart.meshFromShape(shape,LinearDeflection=0.1, AngularDeflection=0.523599)
    m.translate(-centreOfMass[0],-centreOfMass[1],-centreOfMass[2])
    m.transform(mat)

    m.translate(centreOfMass[0],centreOfMass[1],centreOfMass[2])
    
    if debug :
        mm = _FreeCAD.ActiveDocument.addObject("Mesh::Feature","Mesh")
        mm.Mesh = m
        mm.Label = body.Label+"_Mesh"

    return m

'''
    # loop over faces 
    for index in range(len(shape.Faces)):
        singleFace=shape.Faces[index]
        mesh_data = ShapeToMesh(singleFace)
        meshes.append(mesh_data)
'''

def PartToMesh(part) : 
    print 'PartToMesh> ', part.Label
    
    meshes = []

    placement = part.Placement

    # loop over all bodies 
    for obj in part.OutList : 
        print 'PartToMesh> ',obj.Label,' ', obj.TypeId
        if obj.TypeId == 'Part::Feature' or obj.TypeId == 'Part::Box' or obj.TypeId == 'Part::Sphere' or obj.TypeId == 'Part::Cylinder' or obj.TypeId == 'Cone' or obj.TypeId == 'Torus' :

            mesh = BodyToMesh(obj)
            mesh.transform(placement.toMatrix())
            meshes.append([obj.Label,mesh])
            

    return meshes

def GroupToMesh(group) :
    print 'GroupToMesh'

def DocumentToGdml(materialMap = {"default":"G4_Cu"}) :
    doc = _FreeCAD.activeDocument()
    
    # get root objects 
    rootObjects = doc.RootObjects

    # meshes 
    meshes = []
    
    for rootObject in rootObjects :
        print 'DocumentToGdml> ',rootObject.TypeId,' ', rootObject.Label

        # Body object
        if rootObject.TypeId == 'Part::Feature' : 
            meshes.append([rootObject.Label,BodyToMesh(rootObject)])

        if rootObject.TypeId == 'Part::Box' : 
            pass
        if rootObject.TypeId == 'Part::Cone' : 
            pass
        if rootObject.TypeId == 'Part::Sphere' : 
            pass
        if rootObject.TypeId == 'Part::Cylinder' :
            pass
        if rootObject.TypeId == 'Part::Torus' : 
            pass

        # Group object

        # Part object 
        if rootObject.TypeId == 'App::Part' : 
            meshes.append([rootObject.Label,PartToMesh(rootObject)])

    MeshListToGdml(doc.Label,meshes,materialMap)        
    
    return meshes
