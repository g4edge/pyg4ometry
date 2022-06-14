import vtk as _vtk
import pyg4ometry.visualisation.ViewerBase as _ViewerBase
import pyg4ometry.visualisation.Convert as _Convert
from pyg4ometry.visualisation.VisualisationOptions import VisualisationOptions as _VisOptions
from .VisualisationOptions import getPredefinedMaterialVisOptions as _getPredefinedMaterialVisOptions

class VtkViewerNew(_ViewerBase) :
    def __init__(self):
        super(VtkViewerNew, self).__init__()

        self.clear()
        self.initVtk()

        self.cutterOrigins = {}
        self.cutterNormals = {}

        self.bClipper = False
        self.clipperOrigin = None
        self.clipperNormal = None

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
        self.clippers = []

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

    def addClipper(self, origin, normal):
        self.bClipper = True
        self.clipperOrigin = origin
        self.clipperNormal = normal

    def setClipper(self, origin, normal):
        for c in self.clippers :
            p = c.GetClipFunction()
            p.SetOrigin(*origin)
            p.SetNormal(*normal)

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
            normFlt.SetFeatureAngle(179)
            normFlt.SetInputConnection(appFltDict[k].GetOutputPort())

            normFlt = appFltDict[k] # bypass the normal filter

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
            if self.clipperNormal is not None :
                p = self.clipperOrigin
                n = self.clipperNormal

                plane = _vtk.vtkPlane()
                plane.SetOrigin(*p)
                plane.SetNormal(*n)

                cliFlt = _vtk.vtkClipPolyData()
                cliFlt.SetInputConnection(normFlt.GetOutputPort())
                cliFlt.SetClipFunction(plane)
                cliFlt.GenerateClipScalarsOn()
                cliFlt.GenerateClippedOutputOn()

                edgFlt = _vtk.vtkFeatureEdges()
                edgFlt.SetInputConnection(cliFlt.GetOutputPort())
                edgFlt.BoundaryEdgesOn()
                edgFlt.FeatureEdgesOff()
                edgFlt.NonManifoldEdgesOff()
                edgFlt.ManifoldEdgesOff()

                strFlt = _vtk.vtkStripper()
                strFlt.SetInputConnection(edgFlt.GetOutputPort())

                cleFlt = _vtk.vtkContourLoopExtraction()
                cleFlt.SetInputConnection(strFlt.GetOutputPort())

                visOpt = visOptDict[k]

                edgMap = _vtk.vtkPolyDataMapper()
                edgMap.SetInputConnection(cleFlt.GetOutputPort())
                # edgMap.SetResolveCoincidentTopologyToShiftZBuffer()
                edgMap.SetResolveCoincidentTopologyToPolygonOffset()
                edgMap.SetRelativeCoincidentTopologyPolygonOffsetParameters(0,-10*visOpt.depth)
                edgMap.ScalarVisibilityOff()
                edgActor = _vtk.vtkActor()
                edgActor.SetMapper(edgMap)

                if visOpt.representation == "wireframe":
                    edgActor.GetProperty().SetRepresentationToWireframe()

                edgActor.GetProperty().SetOpacity(visOpt.alpha)
                edgActor.GetProperty().SetColor(*visOpt.colour)

                self.actors[k+"_clipper"] = edgActor
                self.ren.AddActor(edgActor)

                self.clippers.append(cliFlt)

            visOpt = visOptDict[k]

            map = _vtk.vtkPolyDataMapper()  # vtkPolyData(Map)per
            map.ScalarVisibilityOff()
            map.SetResolveCoincidentTopologyToPolygonOffset()
            map.SetRelativeCoincidentTopologyPolygonOffsetParameters(0, 10 * visOpt.depth)

            if not self.bClipper :
                map.SetInputConnection(normFlt.GetOutputPort())
            else :
                map.SetInputConnection(cliFlt.GetClippedOutputPort())
                self.ren.GetActiveCamera().SetFocalPoint(0,0,0)

            actor = _vtk.vtkActor()  # vtk(Actor)
            actor.SetMapper(map)
            self.actors[k] = actor

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


class VtkViewerColouredNew(VtkViewerNew):
    """
    Visualiser that extends VtkViewer. Uses "flat" interpolation and introduces control over colours.

    :Keyword Arguments:
        * **materialVisOptions**: {"materialName": :class:`VisualisationOptions` or list or tuple, ...}
        * **interpolation** (str): see :class:`VtkViewer`
        * **defaultColour** (str): "random" or [r,g,b]

    :Examples:

    >>> vMaterialMap = VtkViewerColoured(materialVisOptions={"G4_WATER":[0,0,1]})
    >>> vRandom = VtkViewerColoured(defaultColour="random")
    >>> vColoured = VtkViewerColoured(defaultColour=[0.1,0.1,0.1])
    >>> vColourAlpha = VtkViewerColoured(defaultColour=[0.1,0.1,0.1,0.5])

    of use visualisation options instances

    >>> vo = pyg4ometry.visualisation.VisualisationOptions()
    >>> vo.colour = [0.1,1.0,0.5]
    >>> vo.alpha = 0.3
    >>> options = {'G4_WATER':vo}
    >>> vis = VtkViewerColoured(materialVisOptions=options)

    If the value in the materialVisOptions is a list or a tuple, it will be upgraded
    to a :class:`VisualisationOptions` instance.
    """

    def __init__(self, *args, defaultColour=None, materialVisOptions=None, **kwargs):
        kwargs["interpolation"] = kwargs.get("interpolation", "flat")
        super().__init__()

        self._defaultVis = _VisOptions()
        self._defaultVis.randomColour = defaultColour == "random"
        if type(defaultColour) is list:
            self._defaultVis.colour = defaultColour

        # loop over dictionary of material vis options - if value is list(rgba)
        # convert to vis options instance, make invisible if alpha is 0
        if materialVisOptions:
            for k, v in materialVisOptions.items():
                if type(v) is list or type(v) is tuple:
                    vi = _VisOptions()
                    vi.colour = v[:3]
                    if any([i > 1 for i in vi.colour]):
                        vi.colour = [i / 255.0 for i in vi.colour]
                    if len(v) > 3:
                        vi.alpha = v[3]
                        vi.visible = vi.alpha != 0
                    self.materialVisOptions[k] = vi
                else:
                    self.materialVisOptions[k] = v

    def _getDefaultVis(self, pv):
        return self._defaultVis

class VtkViewerColouredMaterialNew(VtkViewerColouredNew):
    """
    Extension of VtkViewerColoured that uses a default material dictionary for
    several common materials. Material colours are in defined Colour.py for many
    Geant4, FLUKA and BDSIM materials.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, materialVisOptions=_getPredefinedMaterialVisOptions(), **kwargs)
