import sys
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QFileDialog, QTreeWidget, QTreeWidget, QTreeWidgetItem, QDockWidget
from .QVTKRenderWindowInteractor import  QVTKRenderWindowInteractor

import pyg4ometry.visualisation.VtkViewer

from .GeometryModel import GeometryModel

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

        randomColourAction = QAction('Random colour', self)
        randomColourAction.setStatusTip('Random colour')
        actionMenu.addAction(randomColourAction)

        materialColourAction = QAction('Material colour', self)
        materialColourAction.setStatusTip('Material colour')
        actionMenu.addAction(materialColourAction)

        self.treeView = QTreeWidget()
        self.treeDockWidget = QDockWidget("Models")
        self.treeDockWidget.setWidget(self.treeView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.treeDockWidget)
        self.treeView.clicked.connect(self.slotModelChanged)

        self.vtkWidget  = QVTKRenderWindowInteractor()
        self.setCentralWidget(self.vtkWidget)

        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 1000, 750)
        self.setWindowTitle('pyg4ometry')
        self.show()

    def slotModelChanged(self, signal):
        iModel = signal.row()
        print(signal,iModel)

        rens = self.vtkWidget.GetRenderWindow().GetRenderers()


        for r,i in zip(self.vtkWidget.GetRenderWindow().GetRenderers(),range(rens.GetNumberOfItems())) :

            if i == iModel :
                r.SetDraw(1)
                r.SetLayer(0)
            else :
                r.SetDraw(0)
        self.vtkWidget.GetRenderWindow().Render()

    def setDisplayRenderer(self, iRenderer):
        ren = self.vtkWidget.GetRenderWindow().GetRenderers()[0]

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

            ren = self.geometryModel.vtkDict[name].ren

            self.vtkWidget.GetRenderWindow().AddRenderer(ren)

            if len(self.geometryModel.registryDict) == 1 :
                self.vtkWidget.Initialize()
                self.vtkWidget.Start()

            rens = self.vtkWidget.GetRenderWindow().GetRenderers()
            self.vtkWidget.GetRenderWindow().SetNumberOfLayers(rens.GetNumberOfItems())
            #self.vtkWidget.GetRenderWindow().SetNumberOfLayers(1)
            for r,i in zip(self.vtkWidget.GetRenderWindow().GetRenderers(),range(rens.GetNumberOfItems())) :
                r.SetLayer(i)

            self.vtkWidget.GetRenderWindow().Render()
            self.vtkWidget.show()

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