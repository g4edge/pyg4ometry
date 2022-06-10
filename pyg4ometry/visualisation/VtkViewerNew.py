import vtk as _vtk
import pyg4ometry.visualisation.ViewerBase as _ViewerBase
import   pyg4ometry.visualisation.Convert as _Convert

class VtkViewerNew(_ViewerBase) :
    def __init__(self):
        super(VtkViewerNew, self).__init__()

        self.clear()
        self.initVtk()

        self.cutterOrigins = {}
        self.cutterNormals = {}

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
        self.cutters = {}
        self.cuttersPolyData = {}

    def addCutter(self, name, origin, normal):
        self.cutterOrigins[name] = origin
        self.cutterNormals[name] = normal

    def setCutter(self, name, origin, normal):
        for c in self.cutters[name] :
            p = c.GetCutFunction()
            p.SetOrigin(*origin)
            p.SetNormal(*normal)

    def exportCutter(self, name, fileName):
        pass

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
            vos = self.instanceVisOptions[k] # (v)isualisation (o)ption(s)
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
                visopt = vos[i]
                rgb = visopt.colour
                alpha = visopt.alpha
                actor.GetProperty().SetColor(rgb)
                actor.GetProperty().SetOpacity(alpha)

                self.actors[k+str(i)] = actor
                self.ren.AddActor(actor)

    def buildPipelinesAppend(self) :
        # loop over meshes and create polydata
        for k in self.localmeshes :
            pd = _Convert.pycsgMeshToVtkPolyData(self.localmeshes[k])
            self.polydata[k] = pd

        appFltDict  = {}
        visOptDict  = {}

        # loop over polydata and create actors for instances
        for k in self.instancePlacements :
            vos = self.instanceVisOptions[k] # (v)isualisation (o)ption(s)

            ips = self.instancePlacements[k] # (i)nstance (p)placement(s)
            pd  = self.polydata[k]

            for ip, i in zip(ips,range(0,len(ips))) :
                if str(vos[i]) in appFltDict:
                    appFlt = appFltDict[str(vos[i])]
                else:
                    appFlt = _vtk.vtkAppendPolyData()
                    appFltDict[str(vos[i])] = appFlt
                    visOptDict[str(vos[i])] = vos[i]

                triFlt = _vtk.vtkTriangleFilter()   # (tri)angle (F)i(lt)er
                triFlt.AddInputData(pd)

                traFlt = _vtk.vtkTransformPolyDataFilter() # (tra)nsform (F)i(lt)er
                vtramat = _Convert.pyg42VtkTransformation(ip['transformation'],ip['translation'])
                vtra    = _vtk.vtkGeneralTransform()
                vtra.Concatenate(vtramat)
                traFlt.SetInputConnection(triFlt.GetOutputPort())
                traFlt.SetTransform(vtra)

                appFlt.AddInputConnection(traFlt.GetOutputPort())

        for k in appFltDict :
            normFlt = _vtk.vtkPolyDataNormals() #
            normFlt.SetFeatureAngle(90)
            normFlt.SetInputConnection(appFltDict[k].GetOutputPort())

            # Add cutters
            for ck in self.cutterOrigins :
                p = self.cutterOrigins[ck]
                n = self.cutterNormals[ck]

                plane = _vtk.vtkPlane()
                plane.SetOrigin(*p)
                plane.SetNormal(*n)

                cutFilt = _vtk.vtkCutter()
                cutFilt.SetCutFunction(plane)
                cutFilt.SetInputConnection(normFlt.GetOutputPort())

                try :
                    self.cutters[ck].append(cutFilt)
                except KeyError :
                    self.cutters[ck] = []
                    self.cutters[ck].append(cutFilt)

                map = _vtk.vtkPolyDataMapper()  # vtkPolyData(Map)per
                map.ScalarVisibilityOff()
                map.SetInputConnection(normFlt.GetOutputPort())

                cutMap = _vtk.vtkPolyDataMapper()
                cutMap.ScalarVisibilityOff()
                cutMap.SetInputConnection(cutFilt.GetOutputPort())

                cutActor = _vtk.vtkActor()  # vtk(Actor)
                cutActor.SetMapper(cutMap)
                cutActor.GetProperty().SetLineWidth(4)
                cutActor.GetProperty().SetColor(*[1,0,0])
                cutActor.GetProperty().SetRepresentationToSurface()
                self.actors[k+"_"+ck] = cutActor
                self.ren.AddActor(cutActor)

            # Add clippers


            actor = _vtk.vtkActor()  # vtk(Actor)
            actor.SetMapper(map)
            self.actors[k] = actor

            visOpt = visOptDict[k]
            if visOpt.representation == "wireframe" :
                actor.GetProperty().SetRepresentationToWireframe()

            actor.GetProperty().SetOpacity(visOpt.alpha)
            actor.GetProperty().SetColor(*visOpt.colour)

            self.ren.AddActor(actor)


    def buildPipelinesTransformed(self):
        pass

    def render(self):
        # Render
        self.renWin.Render()

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

