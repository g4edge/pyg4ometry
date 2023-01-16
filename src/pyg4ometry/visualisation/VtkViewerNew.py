import base64 as _base64
import random as _random

import vtk as _vtk
import numpy as _np

import pyg4ometry.transformation as _transformation
import pyg4ometry.visualisation.ViewerBase as _ViewerBase
import pyg4ometry.visualisation.Convert as _Convert
from pyg4ometry.visualisation.VisualisationOptions import VisualisationOptions as _VisOptions
from .VisualisationOptions import getPredefinedMaterialVisOptions as _getPredefinedMaterialVisOptions
from pyg4ometry.pycgal.Polygon_mesh_processing import isotropic_remeshing as _isotropic_remeshing

class VtkViewerNew(_ViewerBase) :
    def __init__(self):
        super(VtkViewerNew, self).__init__()

        self.initVtk()
        self.clear()

        self.cutterOrigins = {}
        self.cutterNormals = {}

        self.bClipper = False
        self.bClipperCutter = False
        self.clipperOrigin = None
        self.clipperNormal = None

        self.clipperPlaneWidget = None

    def initVtk(self):
        # create a renderer
        self.ren = _vtk.vtkRenderer()
        self.ren.SetBackground(1.0, 1.0, 1.0)

        # create a rendering window
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
        self.renWin.SetSize(1024, 1024)

        # create a rendering window interactor
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        # add the custom style
        self.interactorStyle = MouseInteractorNamePhysicalVolume(self.ren, self)
        self.interactorStyle.SetDefaultRenderer(self.ren)
        self.iren.SetInteractorStyle(self.interactorStyle)

    def clear(self):

        super(VtkViewerNew, self).clear()

        self.polydata = {}
        self.actors   = {}
        self.cutters  = {}   # cut filters
        self.clippers = []   # clip filters
        self.axes     = []   # axes actors

        self.pdNameDict       = {} # polydata to LV name
        self.instanceNameDict = {} # instance transformation to PV name

        self.bBuiltPipelines = False

        # remove all actors
        for a in self.ren.GetActors() :
            self.ren.RemoveActor(a)

    def addAxes(self, length=20.0, origin=(0, 0, 0)):
        """
        Add x,y,z axis to the scene.

        :param length: float - length of each axis in mm
        :param origin: (float,float,float) - (x,y,z) of origin in mm
        """
        axes = _vtk.vtkAxesActor()

        # transform to move axes
        tran = _vtk.vtkTransform()
        tran.Translate(origin[0], origin[1], origin[2])
        axes.SetUserTransform(tran)

        self.axes.append(axes)

        axes.SetTotalLength(length, length, length)
        self.ren.AddActor(axes)

    def setAxes(self, iAxes, length, origin):
        aa = self.axes[iAxes]

    def addAxesWidget(self):
        axesActor = _vtk.vtkAnnotatedCubeActor()
        axesActor.SetXPlusFaceText('+x')
        axesActor.SetXMinusFaceText('-x')
        axesActor.SetYPlusFaceText('+y')
        axesActor.SetYMinusFaceText('-y')
        axesActor.SetZPlusFaceText('+z')
        axesActor.SetZMinusFaceText('-z')
        axesActor.GetTextEdgesProperty().SetColor(1, 1, 1)
        axesActor.GetTextEdgesProperty().SetLineWidth(2)
        axesActor.GetCubeProperty().SetColor(0.4, 0.4, 0.4)
        self.axesWidget = _vtk.vtkOrientationMarkerWidget()
        self.axesWidget.SetOrientationMarker(axesActor)
        self.axesWidget.SetInteractor(self.iren)
        self.axesWidget.EnabledOn()
        self.axesWidget.InteractiveOn()

    def addCutter(self, name, origin, normal):
        if self.bBuiltPipelines :
            print("Need to add cutter before pipelines are built")

        self.cutterOrigins[name] = origin
        self.cutterNormals[name] = normal

    def setCutter(self, name, origin, normal):
        for c in self.cutters[name] :
            p = c.GetCutFunction()
            p.SetOrigin(*origin)
            p.SetNormal(*normal)

    def addCutterWidget(self):
        pass

    def exportCutter(self, name, fileName):

        self.cuttersAppFlt = _vtk.vtkAppendPolyData()

        for c in self.cutters[name] :
            self.cuttersAppFlt.AddInputConnection(c.GetOutputPort())

        w = _vtk.vtkPolyDataWriter()
        w.SetFileName(fileName)
        w.SetInputConnection(self.cuttersAppFlt.GetOutputPort())
        w.Write()

    def addClipper(self, origin, normal, bClipperCutter = False, bClipperCloseCuts = True):
        if self.bBuiltPipelines :
            print("Need to add clipper before pipelines are built")

        self.bClipper          = True
        self.clipperOrigin     = origin
        self.clipperNormal     = normal
        self.bClipperCutter    = bClipperCutter
        self.bClipperCloseCuts = bClipperCloseCuts

        if self.bClipperCutter :
            self.addCutter("clipperCutter", origin, normal)

    def setClipper(self, origin, normal):
        for c in self.clippers :
            p = c.GetClipFunction()
            p.SetOrigin(*origin)
            p.SetNormal(*normal)

        if self.bClipperCutter :
            self.setCutter("clipperCutter",origin,normal)

        if self.clipperPlaneWidget :
            self.clipperPlaneWidget.GetRepresentation().SetNormal(*normal)
            self.clipperPlaneWidget.GetRepresentation().SetOrigin(*origin)


    def addClipperWidget(self):

        if not self.bBuiltPipelines :
            print("Need to build pipelines before adding clipper widget e.g. v.bulidPipelinesAppend()")
            return

        if len(self.clippers) == 0 :
            print("Need to add a clipping plane adding clipper widget e.g. v.addClipper([0, 0, 0], [0, 0, 1], True")
            return

        plaRep = _vtk.vtkImplicitPlaneRepresentation()
        # plaRep.SetPlaceFactor(1.25)
        plaRep.PlaceWidget(list(self.actors.values())[0].GetBounds())
        plaRep.SetNormal(self.clippers[0].GetClipFunction().GetNormal())
        plaRep.SetOrigin(self.clippers[0].GetClipFunction().GetOrigin())

        self.clipperPlaneWidget = _vtk.vtkImplicitPlaneWidget2()
        self.clipperPlaneWidget.SetInteractor(self.iren)
        self.clipperPlaneWidget.SetRepresentation(plaRep)

        self.clipperPlaneWidget.AddObserver("InteractionEvent", self.updateClipperPlaneCallback)

    def updateClipperPlaneCallback(self, obj, event):
        rep = obj.GetRepresentation()

        plane = _vtk.vtkPlane()
        rep.GetPlane(plane)
        self.setClipper(plane.GetOrigin(), plane.GetNormal())

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

        self.bBuiltPipelines = True

    def buildPipelinesAppend(self) :
        # loop over meshes and create polydata
        for k in self.localmeshes :
            pd = _Convert.pycsgMeshToVtkPolyData(self.localmeshes[k])
            # pd.SetObjectName(k)
            self.polydata[k] = pd
            self.pdNameDict[pd] = k

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

                self.instanceNameDict[traFlt] = ip['name']

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

                edgTriFlt = _vtk.vtkTriangleFilter()
                edgTriFlt.SetInputConnection(edgFlt.GetOutputPort())

                cleFlt = _vtk.vtkContourLoopExtraction()
                cleFlt.SetInputConnection(edgTriFlt.GetOutputPort())
                #cleFlt.SetLoopClosureToBoundary()
                #cleFlt.SetLoopClosureToOff()

                strFlt = _vtk.vtkStripper()
                strFlt.SetInputConnection(cleFlt.GetOutputPort())

                visOpt = visOptDict[k]

                edgMap = _vtk.vtkPolyDataMapper()
                edgMap.SetInputConnection(strFlt.GetOutputPort())
                edgMap.SetResolveCoincidentTopologyToPolygonOffset()
                edgMap.SetRelativeCoincidentTopologyPolygonOffsetParameters(0,-3*visOpt.depth)
                edgMap.ScalarVisibilityOff()
                edgActor = _vtk.vtkActor()
                edgActor.SetMapper(edgMap)

                if visOpt.representation == "wireframe":
                    edgActor.GetProperty().SetRepresentationToWireframe()

                edgActor.GetProperty().SetOpacity(visOpt.alpha)
                edgActor.GetProperty().SetColor(*visOpt.colour)

                if self.bClipperCloseCuts :
                    self.actors[k+"_clipper"] = edgActor
                    self.ren.AddActor(edgActor)

                self.clippers.append(cliFlt)

            visOpt = visOptDict[k]

            map = _vtk.vtkPolyDataMapper()  # vtkPolyData(Map)per
            map.ScalarVisibilityOff()
            map.SetResolveCoincidentTopologyToPolygonOffset()
            map.SetRelativeCoincidentTopologyPolygonOffsetParameters(0, 3*visOpt.depth)

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

        self.bBuiltPipelines = True

    def buildPipelinesTransformed(self):
        pass

    def render(self):
        if not self.bBuiltPipelines :
            print("Not built pipelines")
            return

        # Render
        self.renWin.Render()

    def view(self, interactive = True, resetCamera = False):
        if not self.bBuiltPipelines :
            print("Not built pipelines")
            return

        # enable user interface interactor
        self.iren.Initialize()

        # Camera setup
        if resetCamera:
            self.ren.ResetCamera()

        # Render
        self.renWin.Render()

        if self.clipperPlaneWidget :
            self.clipperPlaneWidget.On()

        if interactive:
            self.iren.Start()

    def removeInvisible(self):
        '''Remove wireframe or transparent instances from self'''
        toRemove = []

        for k in self.localmeshes:
            pyg4VisOpt = self.instanceVisOptions[k][0]
            pyg4_rep   = pyg4VisOpt.representation
            pyg4_alp   = pyg4VisOpt.alpha

            if pyg4_rep == "wireframe" or pyg4_alp == 0:
                toRemove.append(k)

        for k in toRemove :
            self.localmeshes.pop(k)
            self.instancePlacements.pop(k)
            self.instanceVisOptions.pop(k)

    def exportGLTFScene(self, gltfFileName = 'test.gltf', singleInstance = False):
        '''Export entire scene as gltf file, filename extension dictates binary (glb) or readable json (gltf)
           singleInstance is a Boolean flag to supress all but one instance'''

        try :
            from pygltflib import GLTF2, Scene, Material, PbrMetallicRoughness, Buffer, BufferView, Accessor, \
                                  Mesh, Attributes, Primitive, Node, \
                                  ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER, \
                                  FLOAT, UNSIGNED_INT, SCALAR, VEC3
        except ImportError :
            print("pygltflib needs to be installed for export : 'pip install pygltflib'")
            return

        materials   = []
        buffers     = []
        bufferViews = []
        accessors   = []
        meshes      = []
        nodes       = []
        scenes      = []

        # loop over meshes
        iBuffer = 0
        key_iBuffer = {}
        for k in self.localmeshes :
            key_iBuffer[k] = iBuffer

            # get mesh
            csg = self.localmeshes[k]

            scale = 1-0.001*self.instanceVisOptions[k][0].depth
            csg.scale([scale,scale,scale])

            inf = csg.info()

            vAndPs = csg.toVerticesAndPolygons()
            verts = vAndPs[0]
            tris = vAndPs[1]

            verts = _np.array(verts).astype(_np.float32)
            tris = _np.array(tris).astype(_np.uint32)

            verts_binary_blob = verts.flatten().tobytes()
            tris_binary_blob = tris.flatten().tobytes()

            pyg4VisOpt = self.instanceVisOptions[k][0]

            pyg4_color = pyg4VisOpt.colour
            pyg4_alpha = pyg4VisOpt.alpha
            pyg4_rep   = pyg4VisOpt.representation

            pbrMetallicRoughness = PbrMetallicRoughness(baseColorFactor = [_random.random(), _random.random(), _random.random(), 1.0],
                                                        metallicFactor = _random.random(),
                                                        roughnessFactor = _random.random())
            #alphaMode = "OPAQUE"


            #if pyg4_rep == "wireframe" :
            #    alphaMode = "BLEND"
            #    alphaCutoff = pyg4_alpha

            materials.append(Material(pbrMetallicRoughness=pbrMetallicRoughness))

            buffers.append(Buffer(uri = 'data:application/octet-stream;base64,'+str(_base64.b64encode(tris_binary_blob+verts_binary_blob).decode("utf-8")),
                                  byteLength=len(tris_binary_blob) + len(verts_binary_blob)))

            bufferViews.append(BufferView(buffer=iBuffer,
                                          byteLength=len(tris_binary_blob),
                                          target=ELEMENT_ARRAY_BUFFER))
            bufferViews.append(BufferView(buffer=iBuffer,
                                          byteOffset=len(tris_binary_blob),
                                          byteLength=len(verts_binary_blob),
                                          target=ARRAY_BUFFER))
            accessors.append(Accessor(bufferView=2*iBuffer,
                                      componentType=UNSIGNED_INT,
                                      count=tris.size,
                                      type=SCALAR,
                                      max=[int(tris.max())],
                                      min=[int(tris.min())]))
            accessors.append(Accessor(bufferView=2*iBuffer+1,
                                      componentType=FLOAT,
                                      count=int(verts.size/3),
                                      type=VEC3,
                                      max=verts.max(axis=0).tolist(),
                                      min=verts.min(axis=0).tolist()))
            meshes.append(Mesh(primitives=[Primitive(attributes=Attributes(POSITION=2*iBuffer+1),
                                                     indices=2*iBuffer,
                                                     material=iBuffer)]))

            iBuffer += 1

        # loop over instances
        iMesh = 0
        for k in self.instancePlacements :
            iInstance = 0
            for p in self.instancePlacements[k] :
                t = p['translation']
                r = p['transformation']
                aa = _transformation.matrix2axisangle(r)
                axis = aa[0]
                angle = aa[1]

                nodes.append(Node(name=k+"_"+str(iInstance),
                                  mesh=iMesh,
                                  translation=[float(t[0]),float(t[1]),float(t[2])],
                                  rotation=[axis[0]*_np.sin(angle/2),
                                            axis[1]*_np.sin(angle/2),
                                            axis[2]*_np.sin(angle/2),
                                            _np.cos(angle/2)]))

                # Only make a single instance
                if singleInstance :
                    break

                iInstance += 1

            iMesh += 1

        scene = Scene(nodes=list(range(0,len(nodes),1)))
        scenes.append(scene)

        gltf = GLTF2(scene=0,
                     scenes=scenes,
                     nodes=nodes,
                     meshes=meshes,
                     accessors=accessors,
                     bufferViews=bufferViews,
                     buffers=buffers,
                     materials=materials)

        if gltfFileName.find('gltf') != -1 :
            gltf.save_json(gltfFileName)
        elif gltfFileName.find('glb') != -1 :
            glb = b"".join(gltf.save_to_bytes())
            f = open(gltfFileName,"wb")
            f.write(glb)
            f.close()
        else :
            print("VtkViewerNew::exportGLTFScene> unknown gltf extension")

    def exportGLTFAssets(self, gltfFileName = 'test.gltf'):
        '''Export all the assets (meshes) without all the instances. The position of the asset is
           the position of the first instance'''

        self.exportGLTFScene(gltfFileName, singleInstance = True)

    def __repr__(self):
        return ''

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

class MouseInteractorNamePhysicalVolume(_vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, renderer, vtkviewer):
        self.AddObserver("RightButtonPressEvent", self.rightButtonPressEvent)

        self.ren       = renderer
        self.vtkviewer = vtkviewer

        self.highLightActor = None
        self.highLightTextActor = None

    def removeHighLight(self):
        if self.highLightActor :
            self.ren.RemoveActor(self.highLightActor)
            self.ren.GetRenderWindow().Render()

    def removeHighLightText(self):
        if self.highLighTextActor :
            self.ren.RemoveActor(self.highLightTextActor)
            self.ren.GetRenderWindow().Render()

    def rightButtonPressEvent(self, obj, event):

        if self.highLightActor :
            self.ren.RemoveActor(self.highLightActor)

        clickPos = self.GetInteractor().GetEventPosition()
        print("clickPos> ",clickPos)

        picker = _vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        actor = picker.GetActor()

        pointPicker = _vtk.vtkPointPicker()
        pointPicker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        print("pointId>", pointPicker.GetPointId())

        cellPicker = _vtk.vtkCellPicker()
        cellPicker.SetPickClippingPlanes(False)
        cellPicker.Pick(clickPos[0], clickPos[1], 0, self.ren)
        actor = cellPicker.GetActor()

        # possible we don't hit an actor
        if actor is None :
            return

        map   = actor.GetMapper()
        self.inalgo = map.GetInputAlgorithm()


        if self.inalgo.GetClassName() == "vtkClipPolyData" :
            appPolyData = self.inalgo.GetInputAlgorithm()
        elif self.inalgo.GetClassName() == "vtkAppendPolyData" :
            appPolyData = self.inalgo
        else :
            appPolyData = self.inalgo.GetInputAlgorithm().GetInputAlgorithm().GetInputAlgorithm().GetInputAlgorithm().GetInputAlgorithm()

        print(self.inalgo.GetClassName(), appPolyData.GetClassName())

        point = self.inalgo.GetOutput().GetPoint(cellPicker.GetPointId())
        print("pointPos>",point)

        # loop over appendPolyData and find closest
        dmin = 1e99
        di   = -1
        pdmin  = None
        pdamin = None
        for ipd in range(0,appPolyData.GetNumberOfInputConnections(0),1) :
            pd = appPolyData.GetInput(ipd)              # polydata
            pda = appPolyData.GetInputAlgorithm(0,ipd)  # polydata algorithm
            pdd = _vtk.vtkImplicitPolyDataDistance()
            pdd.SetInput(pd)
            dist = pdd.EvaluateFunction(*point)
            if dist < dmin :
                di = ipd
                dmin = dist
                pdmin  = pd
                pdamin = pda

        lvName  = self.vtkviewer.pdNameDict[pdamin.GetInputAlgorithm().GetInput()]
        pvName  = self.vtkviewer.instanceNameDict[pdamin]
        pvTrans = pdamin.GetTransform()
        [mtra, tra] = _Convert.vtkTransformation2PyG4(pvTrans.GetConcatenatedTransform(0))
        globalExtent = pdmin.GetBounds()
        localExtent  = pdamin.GetInput().GetBounds()

        tba = _transformation.matrix2tbxyz(mtra)

        print("minimum pd>", di,dmin, lvName, pvName,tba,tra, localExtent, globalExtent)

        if self.highLightActor :
            self.ren.RemoveActor(self.highLightActor)

        highLightMapper = _vtk.vtkPolyDataMapper()
        highLightMapper.SetInputData(appPolyData.GetInput(di))

        self.highLightActor = _vtk.vtkActor()
        self.highLightActor.SetMapper(highLightMapper)
        self.highLightActor.GetProperty().SetColor(0,1,0)
        self.highLightActor.GetProperty().SetOpacity(0.5)

        self.ren.AddActor(self.highLightActor)

        if self.highLightTextActor :
            self.ren.RemoveActor(self.highLightTextActor)

        self.highLightTextActor = _vtk.vtkTextActor()
        self.highLightTextActor.GetTextProperty().SetFontSize(40);
        self.highLightTextActor.GetTextProperty().SetColor(0,0,0)
        self.highLightTextActor.SetInput("lv   : "+lvName+"\n"+
                                         "pv   : "+pvName+"\n"+
                                         "tbr  :"+str(tba)+"\n"+
                                         "tra  :"+str(tra)+"\n"+
                                         "local aabb :"+str(localExtent)+"\n"+
                                         "global aabb :"+str(globalExtent))
        self.highLightTextActor.SetDisplayPosition(20, 30)
        self.ren.AddActor(self.highLightTextActor)

        # update rendering
        self.ren.GetRenderWindow().Render()
