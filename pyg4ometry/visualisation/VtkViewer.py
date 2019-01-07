import vtk as _vtk
import copy as _copy 

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
        self.mappers = {}

        # actors (per placement) 
        self.actors = {}

    def addLocalMesh(self, meshName, mesh) : 
        pass

    def addMeshInstance(self, meshName, placementName, placement) : 
        # Filter? Like triangle filter? 
        # Mapper? 
        
        pass

    def view(self):
        # enable user interface interactor
        self.iren.Initialize()

        # Render and set start interactor
        self.ren.ResetCamera()
        self.renWin.Render()
        self.iren.Start()    

# python iterable to vtkIdList
def mkVtkIdList(it):
    vil = _vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

# convert pycsh mesh to vtkPolyData
def pycsgMeshToVtkPolyData(self, mesh, vtkPolyData) : 

    mesh.refine()
    meshPolyData = _vtk.vtkPolyData() 
    points       = _vtk.vtkPoints()
    polys        = _vtk.vtkCellArray()
    scalars      = _vtk.vtkFloatArray()

    for v in verts :
        points.InsertNextPoint(v)

        # determine axis ranges (should probably replace)
        if(abs(v[0]) > self.xrange) :
            self.xrange = abs(v[0])
        if(abs(v[1]) > self.yrange) :
            self.yrange = abs(v[1])
        if(abs(v[2]) > self.zrange) :
            self.zrange = abs(v[2])

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
