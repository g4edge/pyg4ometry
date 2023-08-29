import vtk as _vtk
import copy as _copy
import numpy as _np


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

    for i in range(count):
        scalars.InsertTuple1(i, 1)

    meshPolyData.SetPoints(points)
    meshPolyData.SetPolys(polys)
    meshPolyData.GetPointData().SetScalars(scalars)

    del points
    del polys
    del scalars

    return meshPolyData


def vtkPolyDataToNumpy(data):
    conFlt = _vtk.vtkConnectivityFilter()
    if type(data) is str:
        r = _vtk.vtkPolyDataReader()
        r.SetFileName(data)
        r.Update()
        conFlt.SetInputConnection(r.GetOutputPort())
    else:
        conFlt.SetInputData(data)

    conFlt.SetExtractionModeToAllRegions()
    conFlt.ColorRegionsOn()
    conFlt.Update()

    # print(conFlt.GetNumberOfExtractedRegions())

    retnSortedPnts = []
    for i in range(conFlt.GetNumberOfExtractedRegions()):
        conFlt.SetExtractionModeToSpecifiedRegions()
        conFlt.InitializeSpecifiedRegionList()
        conFlt.AddSpecifiedRegion(i)
        conFlt.Update()
        pd = conFlt.GetOutput()
        # print(pd.GetNumberOfPoints(),pd.GetNumberOfCells())

        firstCell = pd.GetCell(0)
        firstPointId = firstCell.GetPointId(0)

        def pntsInOrder(pointId, nlim=10000, ids=[]):
            ids.append(pointId)
            vidl = _vtk.vtkIdList()
            pd.GetPointCells(pointId, vidl)
            for ci in range(vidl.GetNumberOfIds()):
                c = pd.GetCell(vidl.GetId(ci))
                if c.GetPointId(0) == pointId and len(ids) < nlim:
                    # print(nlim,len(ids))
                    pntsInOrder(c.GetPointId(1), nlim, ids)

        sortedIds = []
        pntsInOrder(firstPointId, pd.GetNumberOfCells() + 1, sortedIds)
        # print(sortedIds)

        sortedPnts = []
        for sid in sortedIds:
            sortedPnts.append(list(pd.GetPoint(sid)))

        retnSortedPnts.append(_np.array(sortedPnts))

    return retnSortedPnts


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


def pyg42VtkTransformation(mtra, tra):
    vtkTransform = _vtk.vtkMatrix4x4()
    vtkTransform.SetElement(0, 0, mtra[0, 0])
    vtkTransform.SetElement(0, 1, mtra[0, 1])
    vtkTransform.SetElement(0, 2, mtra[0, 2])
    vtkTransform.SetElement(1, 0, mtra[1, 0])
    vtkTransform.SetElement(1, 1, mtra[1, 1])
    vtkTransform.SetElement(1, 2, mtra[1, 2])
    vtkTransform.SetElement(2, 0, mtra[2, 0])
    vtkTransform.SetElement(2, 1, mtra[2, 1])
    vtkTransform.SetElement(2, 2, mtra[2, 2])
    vtkTransform.SetElement(0, 3, tra[0])
    vtkTransform.SetElement(1, 3, tra[1])
    vtkTransform.SetElement(2, 3, tra[2])
    vtkTransform.SetElement(3, 3, 1)

    return vtkTransform


def vtkTransformation2PyG4(vt):
    mat = vt.GetMatrix()
    mtra = _np.array(
        [
            [mat.GetElement(0, 0), mat.GetElement(0, 1), mat.GetElement(0, 2)],
            [mat.GetElement(1, 0), mat.GetElement(1, 1), mat.GetElement(1, 2)],
            [mat.GetElement(2, 0), mat.GetElement(2, 1), mat.GetElement(2, 2)],
        ]
    )
    tra = _np.array([mat.GetElement(0, 3), mat.GetElement(1, 3), mat.GetElement(2, 3)])

    return [mtra, tra]


def pycsgMeshToStl(mesh, fileName):
    vtkPD = pycsgMeshToVtkPolyData(mesh)

    w = _vtk.vtkSTLWriter()
    w.SetFileName(fileName)
    w.SetInputData(vtkPD)
    w.Write()
