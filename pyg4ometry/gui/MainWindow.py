import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QFileDialog, QTreeWidget, QTreeWidget, QTreeWidgetItem, QDockWidget
from QVTKRenderWindowInteractor import  QVTKRenderWindowInteractor

from GeometryModel import GeometryModel

class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()

        self.initModel()
        self.initUI()

    def initModel(self):
        self.geometryModel = GeometryModel()

    def initUI(self):

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('File')

        openAction = QAction('Open', self)
        openAction.setShortcut('Ctrl+F')
        openAction.setStatusTip('Open GDML file')
        openAction.triggered.connect(self.openFileNameDialog)
        fileMenu.addAction(openAction)

        saveAction = QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save GDML file')
        saveAction.triggered.connect(self.saveFileDialog)
        fileMenu.addAction(saveAction)

        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        actionMenu = menubar.addMenu('Actions')
        overlapAction = QAction('Check overlaps', self)
        overlapAction.setShortcut('Ctrl+O')
        overlapAction.setStatusTip('Check overlaps')
        actionMenu.addAction(overlapAction)

        self.treeView = QTreeWidget()
        self.treeDockWidget = QDockWidget("Models")
        self.treeDockWidget.setWidget(self.treeView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.treeDockWidget)

        from vtk.vtkFiltersSources import vtkConeSource
        from vtk.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer

        vtkWidget  = QVTKRenderWindowInteractor()
        self.setCentralWidget(vtkWidget)

        vtkWidget.Initialize()
        vtkWidget.Start()
        # if you don't want the 'q' key to exit comment this.
        # vtkWidget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

        ren = vtkRenderer()
        ren.SetBackground(1.0, 1.0, 1.0)
        vtkWidget.GetRenderWindow().AddRenderer(ren)

        cone = vtkConeSource()
        cone.SetResolution(8)

        coneMapper = vtkPolyDataMapper()
        coneMapper.SetInputConnection(cone.GetOutputPort())

        coneActor = vtkActor()
        coneActor.SetMapper(coneMapper)

        ren.AddActor(coneActor)

        # show the widget
        vtkWidget.show()

        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 1000, 750)
        self.setWindowTitle('pyg4ometry')
        self.show()

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py);;GDML files (*.gdml);;STL files (*stl);;STEP files (*step);;FLUKA files (*inp)", options=options)
        if fileName:
            name = self.geometryModel.loadNewRegistry(fileName)
            item = QTreeWidgetItem()
            item.setText(0,name)
            self.treeView.insertTopLevelItem(0,item)
            self.treeView.show()
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)


def main() :
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()