import vtk as _vtk
import itertools as _itertools

def writeVtkPolyDataAsSTLFile(fileName, meshes):
    """
    meshes : list of triFilters
    """
    # Convert vtkPolyData to STL mesh
    appendFilter = _vtk.vtkAppendPolyData()

    for m in meshes:
        if m :
            appendFilter.AddInputData(m)

    # append mesh to filter
    appendFilter.Update()

    # remove duplicate points
    cleanFilter = _vtk.vtkCleanPolyData()
    cleanFilter.SetInputConnection(appendFilter.GetOutputPort())
    cleanFilter.Update()

    # write STL file
    stlWriter = _vtk.vtkSTLWriter()
    stlWriter.SetFileName(fileName)
    stlWriter.SetInputConnection(appendFilter.GetOutputPort())
    stlWriter.Write()
    return stlWriter



