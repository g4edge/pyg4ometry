import sys
import vtk
from PySide import QtCore, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

def example() :

    # every QT app needs an app
    app = QtGui.QApplication(['QVTKRenderWindowInteractor'])

    # Create the widget
    widget = QVTKRenderWindowInteractor()
    widget.Initialize()
    widget.Start()

    # if you dont want the 'q' key to exit comment this.
    widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

    ren = vtk.vtkRenderer()
    widget.GetRenderWindow().AddRenderer(ren)

    cone = vtk.vtkConeSource()
    cone.SetResolution(8)

    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())

    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)

    ren.AddActor(coneActor)

    widget.SetPicker(vtk.vtkPointPicker())

    # show the widget
    widget.show()

    # start event processing
    sys.exit(app.exec_())
