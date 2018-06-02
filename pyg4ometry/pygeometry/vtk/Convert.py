import vtk as _vtk
import copy as _copy


# python iterable to vtkIdList
def mkVtkIdList(it):
    vil = _vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil


class Convert :
    def __init__(self):
        self.polyDataList = []

    def MeshListToPolyData(self,meshes) :
        for m in meshes:
            if type(m) == list:
                self.MeshListToPolyData(m)
            else:
                pd = VerticesAndPolygonsToPolyData(m)
                self.polyDataList.append(pd)

        return self.polyDataList

def VerticesAndPolygonsToPolyData(m) :
    m.refine()
    verts, cells, count = m.toVerticesAndPolygons()

    meshPD  = _vtk.vtkPolyData()
    points  = _vtk.vtkPoints()
    polys   = _vtk.vtkCellArray()
    scalars = _vtk.vtkFloatArray()

    for v in verts:
        points.InsertNextPoint(v[0],v[1],v[2])

    for p in cells:
        polys.InsertNextCell(mkVtkIdList(p))

    for i in range(0, count):
        scalars.InsertTuple1(i, 1)

    meshPD.SetPoints(points)
    meshPD.SetPolys(polys)
    meshPD.GetPointData().SetScalars(scalars)

    triFilter = _vtk.vtkTriangleFilter()

    if _vtk.VTK_MAJOR_VERSION <= 5:
        triFilter.SetInput(meshPD)
        triFilter.Update()
    else:
        triFilter.SetInputData(meshPD)
        triFilter.Update()
    pass

    try :
        m.logical
    except AttributeError :
        return triFilter





