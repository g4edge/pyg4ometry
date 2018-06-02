import vtk as _vtk

# python iterable to vtkIdList
def mkVtkIdList(it):
    vil = _vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

class Viewer :
    def __init__(self):
        self.count = 0
        # create a rendering window and renderer
        self.ren = _vtk.vtkRenderer()
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)

        # create a renderwindowinteractor
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        self.ren.SetBackground(1.0, 1.0, 1.0)

        # axis range
        self.xrange = 0
        self.yrange = 0
        self.zrange = 0

    def addPycsgMeshList(self, meshes, refine=True): #, stlname):
        # print 'VtkViewer.addPycsgMeshList>', meshes
        for m in meshes :
            if type(m) == list :
                self.addPycsgMeshList(m, refine=refine) #, stlname)
            else :
                self.addPycsgMesh(m, refine=refine) #, stlname)

    def addPycsgMesh(self,m, refine=True): #, stlname):
        #print 'VtkViewer.addMesh>'
        if refine:
            m.refine()
        #print 'VtkViewer.addMesh> refined'
        verts, cells, count = m.toVerticesAndPolygons()
        #print 'VtkViewer.addMesh> to vertices'
        meshPD  = _vtk.vtkPolyData()
        points  = _vtk.vtkPoints()
        polys   = _vtk.vtkCellArray()
        scalars = _vtk.vtkFloatArray()

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

        meshPD.SetPoints(points)
        meshPD.SetPolys(polys)
        meshPD.GetPointData().SetScalars(scalars)

        del points
        del polys
        del scalars

        triFilter = _vtk.vtkTriangleFilter()

        meshMapper = _vtk.vtkPolyDataMapper()
        if _vtk.VTK_MAJOR_VERSION <= 5:
            triFilter.SetInput(meshPD)
            triFilter.Update()
            meshPD = triFilter.GetOutput()
            meshMapper.SetInput(meshPD)

        else:
            triFilter.SetInputData(meshPD)
            triFilter.Update()
            meshPD = triFilter.GetOutput()
            meshMapper.SetInputData(meshPD)

        meshMapper.ScalarVisibilityOff()
        meshActor = _vtk.vtkActor()

        #
        # Set some visualisation options
        #
        try :
            meshActor.GetProperty().SetOpacity(m.alpha);
        except AttributeError :
            pass

        try : 
            meshActor.GetProperty().SetColor(m.colour)
        except AttributeError : 
            print 'No mesh color selected, use default'
            pass

        try :
            if m.wireframe :
                meshActor.GetProperty().SetRepresentationToWireframe()
        except AttributeError :
            pass


        meshActor.SetMapper(meshMapper)
        self.ren.AddActor(meshActor)

    def setAxes(self) : 
        axes = _vtk.vtkAxesActor()
        axes.SetTotalLength([self.xrange,self.yrange,self.xrange]);
        self.ren.AddActor(axes)

    def view(self):
        # enable user interface interactor
        self.setAxes()
        self.iren.Initialize()
        self.renWin.Render()
        self.iren.Start()
