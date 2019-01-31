import numpy as _np
import vtk as _vtk
import copy as _copy 
import pyg4ometry.transformation as _transformation

class VtkViewer : 
    def __init__(self,size=(1024,768)) : 
        
        # create a renderer
        self.ren = _vtk.vtkRenderer()
        
        # create a rendering window
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)

        # create a rendering window interactor 
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        self.ren.SetBackground(1.0, 1.0, 1.0)
        self.renWin.SetSize(*size)

        # local meshes 
        self.localmeshes = {}

        # filters (per mesh)
        self.filters = {}
        
        # mappers (per mesh) 
        self.mappers = []
        self.physicalMapperMap = {}

        # actors (per placement) 
        self.actors = []
        self.physicalActorMap = {}

    def addLocalMesh(self, meshName, mesh) : 
        pass

    def addMeshInstance(self, meshName, placementName, placement) : 
        # Filter? Like triangle filter? 
        # Mapper? 
        
        pass

    def addLogicalVolume(self, logical, mrot = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra = _np.array([0,0,0])) :
        #print 'addLogicalVolume',logical.name
        #print mrot,_np.shape(mrot),type(mrot)
        #print tra,_np.shape(tra),type(tra)

        for pv in logical.daughterVolumes : 
            print 'VtkViewerAddLogicalVolume>',pv.name, pv.logicalVolume.name, pv.logicalVolume.solid.name
            
            pvmrot  = _transformation.tbxyz2matrix(pv.rotation.eval())
            pvtra   = _np.array(pv.position.eval())

            # print 'local pvtransform'
            # print pvmrot,_np.shape(pvmrot),type(pvmrot)
            # print pvtra,_np.shape(pvtra),type(pvtra)
             
            new_mrot = mrot*pvmrot
            new_tra  = (_np.array(mrot.dot(pvtra)) + tra)[0]
  
            # get the local vtkPolyData 
            print 'VtkViewerAddLogicalVolume> vtkPD'
            solidname = pv.logicalVolume.solid.name
            try : 
                vtkPD = self.localmeshes[solidname]
            except KeyError : 
                localmesh = pv.logicalVolume.mesh.localmesh
                vtkPD     = pycsgMeshToVtkPolyData(localmesh)
                self.localmeshes[solidname] = vtkPD

            # triangle filter    
            print 'VtkViewerAddLogicalVolume> vtkFLT'
            filtername = solidname+"_filter"
            try : 
                vtkFLT = self.filters[filtername] 
            except KeyError :  
                vtkFLT = _vtk.vtkTriangleFilter()
                vtkFLT.AddInputData(vtkPD)
                # vtkFLT.Update()
                self.filters[filtername] = vtkFLT

            # mapper 
            print 'VtkVieweraddLogicalVolume> vtkMAP'

            mappername = solidname+"_mapper" 

            vtkMAP = _vtk.vtkPolyDataMapper()
            vtkMAP.ScalarVisibilityOff()
            vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())

            self.mappers.append(vtkMAP)
            
            # mapper look up dictionary 
            try : 
                self.physicalMapperMap[pv.name].append(vtkMAP)
            except KeyError : 
                self.physicalMapperMap[pv.name] = [vtkMAP]
            
#            try : 
#                vtkMAP = self.mappers[mappername] 
#            except KeyError : 
#                vtkMAP = _vtk.vtkPolyDataMapper()             
#                vtkMAP.ScalarVisibilityOff()
#                vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())
#                self.mappers[mappername] = vtkMAP

            # actor
            print 'VtkVieweraddLogicalVolume> vtkActor'

            actorname = pv.name+"_actor"             
            vtkActor = _vtk.vtkActor() 

            # store actor (need to increment count if exists)
            self.actors.append(vtkActor)
            
            # actor look up dictionary
            try : 
                self.physicalActorMap[pv.name].append(vtkActor)
            except KeyError : 
                self.physicalActorMap[pv.name] = [vtkActor]

            vtkActor.SetMapper(vtkMAP)        

            #tra = pv.mesh.tra
            #rot = pv.mesh.rot
            
            rotaa = _transformation.matrix2axisangle(new_mrot)

            vtkActor.SetPosition(new_tra[0],new_tra[1],new_tra[2])
            vtkActor.RotateWXYZ(rotaa[1]/_np.pi*180.0,rotaa[0][0],rotaa[0][1],rotaa[0][2])
            vtkActor.GetProperty().SetColor(1,0,0)


            print 'VtkVieweraddLogicalVolume> Add actor'
            self.ren.AddActor(vtkActor)

            # print 'recursion'
            # print mrot,_np.shape(mrot),type(mrot)
            # print tra,_np.shape(tra),type(tra)
            self.addLogicalVolume(pv.logicalVolume,new_mrot,new_tra)

        
    def view(self):
        # enable user interface interactor
        # self.iren.Initialize()

        # Camera setup
        camera =_vtk.vtkCamera();
        self.ren.SetActiveCamera(camera);
        self.ren.ResetCamera()

        # Render 
        self.renWin.Render()

        self.iren.Start()    

# python iterable to vtkIdList
def mkVtkIdList(it):
    vil = _vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

# convert pycsh mesh to vtkPolyData
def pycsgMeshToVtkPolyData(mesh) : 

    # refine mesh 
    # mesh.refine()

    verts, cells, count = mesh.toVerticesAndPolygons()
    meshPolyData = _vtk.vtkPolyData() 
    points       = _vtk.vtkPoints()
    polys        = _vtk.vtkCellArray()
    scalars      = _vtk.vtkFloatArray()

    for v in verts :
        points.InsertNextPoint(v)

        # determine axis ranges (should probably replace)
        #if(abs(v[0]) > self.xrange) :
        #    self.xrange = abs(v[0])
        #if(abs(v[1]) > self.yrange) :
        #    self.yrange = abs(v[1])
        #if(abs(v[2]) > self.zrange) :
        #    self.zrange = abs(v[2])

        #print 'VtkViewer.addMesh> size determined'
    for p in cells :
        polys.InsertNextCell(mkVtkIdList(p))

    for i in range(0,count) :
        scalars.InsertTuple1(i,1)

    meshPolyData.SetPoints(points)
    meshPolyData.SetPolys(polys)
    meshPolyData.GetPointData().SetScalars(scalars)

    del points
    del polys
    del scalars
        
    return meshPolyData

def writeVtkPolyDataAsSTLFile(fileName, meshes) :
# Convert vtkPolyData to STL mesh
    ''' meshes : list of triFilters '''

    appendFilter = _vtk.vtkAppendPolyData()

    for m in meshes:
        if m :
            appendFilter.AddInputConnection(m.GetOutputPort())

    # append mesh to filter
    appendFilter.Update()

    # remove duplicate points
    cleanFilter = _vtk.vtkCleanPolyData()
    cleanFilter.SetInputConnection(appendFilter.GetOutputPort())
    cleanFilter.Update()

    # write STL file
    print 'stlWriter'
    stlWriter = _vtk.vtkSTLWriter()
    print 'setFileName'
    stlWriter.SetFileName(fileName)
    print 'inputConnection'
    stlWriter.SetInputConnection(appendFilter.GetOutputPort())
    print 'write'
    stlWriter.Write()
    print 'done'
    return stlWriter
