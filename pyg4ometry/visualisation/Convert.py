import vtk as _vtk
import copy as _copy

# python iterable to vtkIdList
def mkVtkIdList(it):
    vil = _vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

# convert pycsh mesh to vtkPolyData
def pycsgMeshToVtkPolyData(mesh):
    # refine mesh
    # mesh.refine()

    verts, cells, count = mesh.toVerticesAndPolygons()
    meshPolyData = _vtk.vtkPolyData()
    points = _vtk.vtkPoints()
    polys = _vtk.vtkCellArray()
    scalars = _vtk.vtkFloatArray()

    for v in verts:
        points.InsertNextPoint(v)

    for p in cells:
        polys.InsertNextCell(mkVtkIdList(p))

    for i in range(0, count):
        scalars.InsertTuple1(i, 1)

    meshPolyData.SetPoints(points)
    meshPolyData.SetPolys(polys)
    meshPolyData.GetPointData().SetScalars(scalars)

    del points
    del polys
    del scalars

    return meshPolyData

def pycsgMeshToObj(mesh, fileName):

    vtkPD = pycsgMeshToVtkPolyData(mesh)
    vtkFLT = _vtk.vtkTriangleFilter()
    vtkMAP = _vtk.vtkPolyDataMapper()
    vtkMAP.ScalarVisibilityOff()
    vtkMAP.SetInputData(vtkPD)
    # vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())
    vtkActor = _vtk.vtkActor()
    vtkActor.SetMapper(vtkMAP)

    ren = _vtk.vtkRenderer()
    ren.AddActor(vtkActor)

    rw = _vtk.vtkRenderWindow()
    rw.AddRenderer(ren)

    exporter = _vtk.vtkOBJExporter()
    exporter.SetRenderWindow(rw)
    exporter.SetFilePrefix("./" + fileName)  # create mtl and obj file.
    exporter.Write()