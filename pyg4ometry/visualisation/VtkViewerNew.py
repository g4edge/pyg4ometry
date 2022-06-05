import vtk as _vtk
import pyg4ometry.visualisation.ViewerBase as _ViewerBase
import   pyg4ometry.visualisation.Convert as _Convert

class VtkViewerNew(_ViewerBase) :
    def __init__(self):
        super(VtkViewerNew, self).__init__()

        self.clear()
        self.initVtk()

    def initVtk(self):
        # create a renderer
        self.ren = _vtk.vtkRenderer()
        self.ren.SetBackground(1.0, 1.0, 1.0)

        # create a rendering window
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)

        # create a rendering window interactor
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

    def clear(self):
        self.polydata = {}
        self.actors = {}

    def _polydata2Actor(self, polydata):
        pass

    def buildPipelines(self):
        pass

    def buildPipelinesSeparate(self):

        # loop over meshes and create polydata
        for k in self.localmeshes :
            pd = _Convert.pycsgMeshToVtkPolyData(self.localmeshes[k])
            self.polydata[k] = pd

        # loop over polydata and create actors for instances
        for k in self.instancePlacements :
            ips = self.instancePlacements[k] # (i)nstance (p)placement(s)
            pd  = self.polydata[k]
            for ip, i in zip(ips,range(0,len(ips))) :

                triFlt = _vtk.vtkTriangleFilter()   # (tri)angle (F)i(lt)er
                triFlt.AddInputData(pd)
                map = _vtk.vtkPolyDataMapper()      # vtkPolyData(Map)per
                map.ScalarVisibilityOff()
                map.SetInputConnection(triFlt.GetOutputPort())
                actor = _vtk.vtkActor()             # vtk(Actor)
                actor.SetMapper(map)
                vtrans = _Convert.pyg42VtkTransformation(ip['transformation'],ip['translation'])
                actor.SetUserMatrix(vtrans)

                self.actors[k+str(i)] = actor
                self.ren.AddActor(actor)

    def buildPipelinesAppend(self) :
        pass

    def buildPipelinesTransformed(self):
        pass

    def view(self, interactive = True, resetCamera = False):
        # enable user interface interactor
        self.iren.Initialize()

        # Camera setup
        if resetCamera:
            self.ren.ResetCamera()

        # Render
        self.renWin.Render()

        if interactive:
            self.iren.Start()

