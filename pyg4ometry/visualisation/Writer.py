import vtk as _vtk
import itertools as _itertools

def WriteSTL(fileName, meshes) :
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


