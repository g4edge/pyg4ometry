import numpy as _np
import vtk as _vtk
import pyg4ometry.transformation as _transformation
from   pyg4ometry.visualisation  import OverlapType     as _OverlapType
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
from   pyg4ometry.visualisation import Convert as _Convert
import logging as _log
import random

class VtkViewer:
    def __init__(self,size=(2048,1536), interpolation="none"):
        
        # create a renderer
        self.ren = _vtk.vtkRenderer()
        
        # create a rendering window
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)

        # create a rendering window interactor 
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        self.ren.SetBackground(1.0, 1.0, 1.0)
        self.renWin.SetSize(*size)

        # local meshes 
        self.localmeshes = {}
        self.localmeshesOverlap = {}

        # filters (per mesh)
        self.filters = {}
        self.filtersOverlap = {}
        
        # mappers (per mesh) 
        self.mappers = []
        self.physicalMapperMap = {}
        self.mappersOverlap = []
        self.physicalMapperMapOverlap = {}

        # actors (per placement) 
        self.actors = []
        self.physicalActorMap = {}
        self.actorsOverlap = [] 
        self.physicalActorMapOverlap = {}

        # axes
        self.axes = []

        # axes widget
        self.addAxesWidget()

        # material options dict
        self.materialVisualisationOptions = None

        # interpolation for vertex shading
        interps = ("none", "flat", "gouraud", "phong")
        if interpolation not in interps:
            raise ValueError("Unrecognised interpolation option {}."
                             " Possible options are :{}".format(interpolation, ", ".join(interps)))
        self.interpolation = interpolation

    def addAxes(self, length = 20.0, origin = (0,0,0)):
        axes = _vtk.vtkAxesActor()

        # transform to move axes
        tran = _vtk.vtkTransform()
        tran.Translate(origin[0],origin[1], origin[2])
        axes.SetUserTransform(tran)

        self.axes.append(axes)
        axes.SetTotalLength(length,length,length)
        self.ren.AddActor(axes)

    def addAxesWidget(self):
        axesActor = _vtk.vtkAnnotatedCubeActor();
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

    def setOpacity(self, v, iActor = -1):
        for a, i in zip(self.actors,range(0,len(self.actors))):
            if i == iActor :
                a.GetProperty().SetOpacity(v)
            elif iActor == -1:
                a.GetProperty().SetOpacity(v)

    def setWireframe(self, iActor = -1 ) :
        for a, i in zip(self.actors,range(0,len(self.actors))):
            if i == iActor :
                a.GetProperty().SetRepresentationToWireframe()
            elif iActor == -1 :
                a.GetProperty().SetRepresentationToWireframe()

    def setSurface(self, iActor = -1):
        for a, i in zip(self.actors, range(0, len(self.actors))):
            if i == iActor:
                a.GetProperty().SetRepresentationToSurface()
            elif iActor == -1 :
                a.GetProperty().SetRepresentationToSurface()

    def setOpacityOverlap(self,v, iActor = -1):
        for a, i in zip(self.actorsOverlap, range(0, len(self.actorsOverlap))):
            if i == iActor:
                a.GetProperty().SetOpacity(v)
            elif iActor == -1:
                a.GetProperty().SetOpacity(v)

    def setWireframeOverlap(self, iActor = -1) :
        for a, i in zip(self.actors, range(0, len(self.actors))):
            if i == iActor:
                a.GetProperty().SetRepresentationToWireframe()
            elif iActor == -1:
                a.GetProperty().SetRepresentationToWireframe()

    def setSurfaceOverlap(self, iActor = -1):
        for a, i in zip(self.actors, range(0, len(self.actors))):
            if i == iActor:
                a.GetProperty().SetRepresentationToSurface()
            elif iActor == -1:
                a.GetProperty().SetRepresentationToSurface()

    def setRandomColours(self):
        for a in self.actors:

            a.GetProperty().SetColor(random.random(),
                                     random.random(),
                                     random.random())

    def setMaterialVisualisationOptions(self, dict):
        self.materialVisualisationOptions = dict

    def setCameraFocusPosition(self,focalPoint = [0,0,0], position = [100,100,100]):
        self.ren.GetActiveCamera().SetFocalPoint(focalPoint)
        self.ren.GetActiveCamera().SetPosition(position)

    def start(self):
        self.renWin.Render()
        self.iren.Start()

    def exportOBJScene(self,fileName="scene") :
        rw = _vtk.vtkRenderWindow()
        rw.AddRenderer(self.renWin.GetRenderers().GetFirstRenderer())

        exporter = _vtk.vtkOBJExporter()
        exporter.SetRenderWindow(rw)
        exporter.SetFilePrefix("./"+fileName)  # create mtl and obj file.
        exporter.Write()



    def exportVRMLScene(self,fileName="scene") :
        rw = _vtk.vtkRenderWindow()
        rw.AddRenderer(self.renWin.GetRenderers().GetFirstRenderer())

        exporter = _vtk.vtkVRMLExporter()
        exporter.SetRenderWindow(rw)
        exporter.SetFileName("./"+fileName)  # create mtl and obj file.
        exporter.Write()

    def exportScreenShot(self, fileName="screenshot.png", rgba=True):
        '''
        Write the render window view to an image file.

        Image types supported are:
        BMP, JPEG, PNM, PNG, PostScript, TIFF.
        The default parameters are used for all writers, change as needed.

        :param fileName: The file name, if no extension then PNG is assumed.
        :param renWin: The render window.
        :param rgba: Used to set the buffer type.
        :return:

        '''

        import os

        if fileName:
            # Select the writer to use.
            path, ext = os.path.splitext(fileName)
            ext = ext.lower()
            if not ext:
                ext = '.png'
                fileName = fileName + ext
            if ext == '.bmp':
                writer = _vtk.vtkBMPWriter()
            elif ext == '.jpg':
                writer = _vtk.vtkJPEGWriter()
            elif ext == '.pnm':
                writer = _vtk.vtkPNMWriter()
            elif ext == '.ps':
                if rgba:
                    rgba = False
                writer = _vtk.vtkPostScriptWriter()
            elif ext == '.tiff':
                writer = _vtk.vtkTIFFWriter()
            else:
                writer = _vtk.vtkPNGWriter()

            windowto_image_filter = _vtk.vtkWindowToImageFilter()
            windowto_image_filter.SetInput(self.renWin)
            windowto_image_filter.SetScale(1)  # image quality
            if rgba:
                windowto_image_filter.SetInputBufferTypeToRGBA()
            else:
                windowto_image_filter.SetInputBufferTypeToRGB()
                # Read from the front buffer.
                windowto_image_filter.ReadFrontBufferOff()
                windowto_image_filter.Update()

            writer.SetFileName(fileName)
            writer.SetInputConnection(windowto_image_filter.GetOutputPort())
            writer.Write()
        else:
            raise RuntimeError('Need a filename.')


    def addLogicalVolume(self, logical, mtra=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra=_np.array([0,0,0])) :
        if logical.type == "logical" :
            self.addLogicalVolumeBounding(logical)
            for [overlapmesh, overlaptype], i in zip(logical.mesh.overlapmeshes,
                                                     range(0, len(logical.mesh.overlapmeshes))):
                visOptions = self.setOverlapVisOptions(overlaptype)
                self.addMesh(logical.name, logical.solid.name + "_overlap" + str(i), overlapmesh, mtra, tra,
                             self.localmeshesOverlap, self.filtersOverlap,
                             self.mappersOverlap, self.physicalMapperMapOverlap, self.actorsOverlap,
                             self.physicalActorMapOverlap,
                             visOptions = visOptions, overlap = True)

        # recurse down scene hierarchy
        self.addLogicalVolumeRecursive(logical, mtra, tra)

    def addLogicalVolumeBounding(self, logical):
        # add logical solid as wireframe 
        lvm    = logical.mesh.localmesh
        lvmPD  = _Convert.pycsgMeshToVtkPolyData(lvm)
        lvmFLT = _vtk.vtkTriangleFilter()
        lvmFLT.AddInputData(lvmPD)        
        lvmMAP = _vtk.vtkPolyDataMapper()
        lvmMAP.ScalarVisibilityOff()
        lvmMAP.SetInputConnection(lvmFLT.GetOutputPort())        
        lvmActor = _vtk.vtkActor()
        lvmActor.SetMapper(lvmMAP)         
        lvmActor.GetProperty().SetRepresentationToWireframe()
        lvmActor.GetProperty().SetOpacity(0.5)
        self.actors.append(lvmActor)
        self.ren.AddActor(lvmActor)

    def addBooleanSolidRecursive(self, solid, mtra=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra=_np.array([0,0,0]), first = True) :


        if solid.type == "Union" or solid.type == "Subtraction" or solid.type == "Intersection" :

            if first:
                mesh = solid.pycsgmesh()
                visOptions = _VisOptions()
                visOptions.representation = "surface"
                visOptions.alpha = 1.0
                visOptions.color = [0.5, 0.5, 0.5]
                self.addMesh(solid.name, solid.name, mesh, mtra, tra, self.localmeshes,
                             self.filters, self.mappers, self.physicalMapperMap, self.actors,
                             self.physicalActorMap, visOptions=visOptions, overlap=False, cutters=False)
                first = False

            obj1 = solid.object1()
            obj2 = solid.object2()

            tran = solid.translation()
            rotn = solid.rotation()

            rotm = _transformation.tbxyz2matrix(rotn)
            new_mtra = mtra * rotm
            new_tra  = (_np.array(mtra.dot(tran)) + tra)[0]

            self.addBooleanSolidRecursive(obj1, mtra, tra, first)
            self.addBooleanSolidRecursive(obj2, new_mtra, new_tra, first)
        else :
            mesh = solid.pycsgmesh()
            visOptions = _VisOptions()
            visOptions.representation = "wireframe"
            visOptions.alpha = 0.5
            visOptions.color = [1,0,0]
            self.addMesh(solid.name, solid.name, mesh, mtra, tra, self.localmeshes,
                         self.filters, self.mappers, self.physicalMapperMap, self.actors,
                         self.physicalActorMap,visOptions=visOptions, overlap=False, cutters=False)


    def addLogicalVolumeRecursive(self, logical, mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra = _np.array([0,0,0])):
        for pv in logical.daughterVolumes:

            # get the local vtkPolyData
            if pv.logicalVolume.type != "assembly" :
                solid_name = pv.logicalVolume.solid.name
            else :
                solid_name = "none"
            pv_name = pv.name

            if pv.logicalVolume.type == "logical":
                _log.info('VtkViewer.addLogicalVolume> Daughter %s %s %s ' % (pv.name, pv.logicalVolume.name, pv.logicalVolume.solid.name))

            if pv.type == "placement":
                # pv transform
                pvmrot = _np.linalg.inv(_transformation.tbxyz2matrix(pv.rotation.eval()))
                if pv.scale :
                    pvmsca = _np.diag(pv.scale.eval())
                else :
                    pvmsca = _np.diag([1,1,1])
                pvtra = _np.array(pv.position.eval())
                
                # pv compound transform
                new_mtra = mtra * pvmsca * pvmrot
                new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                if pv.logicalVolume.type != "assembly" :
                    mesh = pv.logicalVolume.mesh.localmesh # TODO implement a check if mesh has changed
                    # mesh = _Mesh(pv.logicalVolume.solid).localmesh

                    if self.materialVisualisationOptions :
                        visOptions = self.materialVisualisationOptions[pv.logicalVolume.material.name]
                    else :
                        visOptions = pv.visOptions
                    self.addMesh(pv_name, solid_name, mesh, new_mtra, new_tra, self.localmeshes, self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions = visOptions, overlap = False)

                    # overlap meshes
                    for [overlapmesh,overlaptype], i in zip(pv.logicalVolume.mesh.overlapmeshes,range(0,len(pv.logicalVolume.mesh.overlapmeshes))) :
                        visOptions = self.setOverlapVisOptions(overlaptype)

                        self.addMesh(pv_name, solid_name+"_overlap"+str(i), overlapmesh, new_mtra, new_tra, self.localmeshesOverlap,
                                     self.filtersOverlap, self.mappersOverlap, self.physicalMapperMapOverlap, self.actorsOverlap,
                                     self.physicalActorMapOverlap, visOptions = visOptions, overlap =True)

                self.addLogicalVolumeRecursive(pv.logicalVolume,new_mtra,new_tra)

            elif pv.type == "replica" or pv.type == "division":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0])
                    pvtra = _np.array(trans[1])
                    
                    # pv compound transform
                    new_mtra = mtra * pvmrot
                    new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                    self.addMesh(pv_name, mesh.solid.name, mesh.localmesh, new_mtra, new_tra, self.localmeshes, self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions = pv.visOptions, overlap = False)
            elif pv.type == "parametrised":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0].eval())
                    pvtra = _np.array(trans[1].eval())

                    # pv compound transform
                    new_mtra = mtra * pvmrot
                    new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                    self.addMesh(pv_name, mesh.solid.name, mesh.localmesh, new_mtra, new_tra, self.localmeshes,
                                 self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions = pv.visOptions, overlap = False)

    def addMesh(self, pv_name, solid_name, mesh, mtra, tra, localmeshes, filters,
                mappers, mapperMap, actors, actorMap, visOptions = None, overlap = False, cutters = True):
        # VtkPolyData : check if mesh is in localmeshes dict
        _log.info('VtkViewer.addLogicalVolume> vtkPD')

        if localmeshes.has_key(solid_name) :
            vtkPD = localmeshes[solid_name]
        else : 
            vtkPD = _Convert.pycsgMeshToVtkPolyData(mesh)
            localmeshes[solid_name] = vtkPD

        if self.interpolation is not "none":
            normal_generator = _vtk.vtkPolyDataNormals()
            normal_generator.SetInputData(vtkPD)
            # normal_generator.ComputePointNormalsOn()
            # normal_generator.ComputeCellNormalsOn()
            normal_generator.SetSplitting(0)
            normal_generator.SetConsistency(0)
            normal_generator.SetAutoOrientNormals(0)
            normal_generator.SetComputePointNormals(1)
            normal_generator.SetComputeCellNormals(1)
            normal_generator.SetFlipNormals(0)
            normal_generator.SetNonManifoldTraversal(0)
            normal_generator.Update()
            vtkPD = normal_generator.GetOutput()

        # Filter : check if filter is in the filters dict
        _log.info('VtkViewer.addLogicalVolume> vtkFLT')
        filtername = solid_name+"_filter"
        if filters.has_key(filtername) :
            vtkFLT = filters[filtername]
        else :
            vtkFLT = _vtk.vtkTriangleFilter()
            vtkFLT.AddInputData(vtkPD)
            filters[filtername]  = vtkFLT

        # Mapper
        _log.info('VtkViewer.addLogicalVolume> vtkMAP')
        mappername = pv_name+"_mapper"
        vtkMAP = _vtk.vtkPolyDataMapper()
        vtkMAP.ScalarVisibilityOff()
        # TRIANGLE/NON-TRIANGLE FILTER
        #vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())
        vtkMAP.SetInputData(vtkPD)

        mappers.append(vtkMAP)

        if not mapperMap.has_key(mappername) :
            mapperMap[mappername] = vtkMAP
            
        # Actor
        actorname = pv_name+"_actor"             
        vtkActor = _vtk.vtkActor() 
        vtkActor.SetMapper(vtkMAP)

        if self.interpolation is not "none":
            if self.interpolation == "gouraud":
                vtkActor.GetProperty().SetInterpolationToGouraud()
            elif self.interpolation == "phong":
                vtkActor.GetProperty().SetInterpolationToPhong()
            elif self.interpolation == "flat":
                vtkActor.GetProperty().SetInterpolationToFlat()

        vtkTransform = _vtk.vtkMatrix4x4()
        vtkTransform.SetElement(0,0,mtra[0,0])
        vtkTransform.SetElement(0,1,mtra[0,1])
        vtkTransform.SetElement(0,2,mtra[0,2])
        vtkTransform.SetElement(1,0,mtra[1,0])
        vtkTransform.SetElement(1,1,mtra[1,1])
        vtkTransform.SetElement(1,2,mtra[1,2])
        vtkTransform.SetElement(2,0,mtra[2,0])
        vtkTransform.SetElement(2,1,mtra[2,1])
        vtkTransform.SetElement(2,2,mtra[2,2])
        vtkTransform.SetElement(0,3,tra[0])
        vtkTransform.SetElement(1,3,tra[1])
        vtkTransform.SetElement(2,3,tra[2])
        vtkTransform.SetElement(3,3,1)

        vtkActor.SetUserMatrix(vtkTransform)

        vtkTransFLT = _vtk.vtkTransformFilter()
        vtkTransform1 = _vtk.vtkTransform()
        vtkTransform1.SetMatrix(vtkTransform)
        vtkTransFLT.SetTransform(vtkTransform1)
        vtkTransFLT.SetInputConnection(vtkFLT.GetOutputPort())

        def makeCutterPlane(normal,color) :

            plane = _vtk.vtkPlane()
            plane.SetOrigin(0, 0, 0)
            plane.SetNormal(normal[0], normal[1], normal[2])
            vtkTransFLT = _vtk.vtkTransformFilter()
            vtkTransform1 = _vtk.vtkTransform()
            vtkTransform1.SetMatrix(vtkTransform)
            vtkTransFLT.SetTransform(vtkTransform1)
            vtkTransFLT.SetInputConnection(vtkFLT.GetOutputPort())

            cutter = _vtk.vtkCutter()
            cutter.SetCutFunction(plane)
            cutter.SetInputConnection(vtkTransFLT.GetOutputPort())
            cutter.Update()

            cutterMapper = _vtk.vtkPolyDataMapper()
            cutterMapper.ScalarVisibilityOff()
            cutterMapper.SetInputConnection(cutter.GetOutputPort())

            planeActor = _vtk.vtkActor()
            planeActor.SetMapper(cutterMapper)
            planeActor.GetProperty().SetLineWidth(4)
            planeActor.GetProperty().SetColor(color[0],color[1],color[2])
            planeActor.GetProperty().SetRepresentationToSurface()
            self.ren.AddActor(planeActor)

        def makeClipperPlane(normal) :
            plane = _vtk.vtkPlane()
            plane.SetOrigin(0, 0, 0)
            plane.SetNormal(normal[0], normal[1], normal[2])
            clipper = _vtk.vtkClipPolyData()
            clipper.SetInputConnection(vtkTransFLT.GetOutputPort())
            clipper.SetClipFunction(plane)
            clipper.InsideOutOn()

            clipperMapper = _vtk.vtkPolyDataMapper()
            clipperMapper.ScalarVisibilityOff()
            clipperMapper.SetInputConnection(clipper.GetOutputPort())

            clipperActor =_vtk.vtkActor()
            clipperActor.SetMapper(clipperMapper)
            clipperActor.GetProperty().SetColor(1.0, 1.0, 1.0)
            clipperActor.GetProperty().SetOpacity(1.0)
            clipperActor.SetScale(1, 1, 1)

            vtkActor.GetProperty().SetOpacity(0.0)
            self.ren.AddActor(clipperActor)  # selection part end

        if cutters :
            makeCutterPlane([1,0,0],[1,0,0])
            makeCutterPlane([0,1,0],[0,1,0])
            makeCutterPlane([0,0,1],[0,0,1])

        #makeClipperPlane([1,0,0])
        #makeClipperPlane([0,1,0])
        #makeClipperPlane([0,0,1])

        if overlap :
            overlapText = _vtk.vtkVectorText()
            overlapText.SetText("overlap")

            overlapMapper = _vtk.vtkPolyDataMapper()
            overlapMapper.SetInputConnection(overlapText.GetOutputPort())

            comFilter = _vtk.vtkCenterOfMass()
            comFilter.SetInputConnection(vtkTransFLT.GetOutputPort())
            comFilter.SetUseScalarsAsWeights(False);
            comFilter.Update()

            overlapActor = _vtk.vtkFollower()
            overlapActor.GetProperty().SetColor(visOptions.color)
            overlapActor.SetPosition(comFilter.GetCenter())
            overlapActor.SetMapper(overlapMapper)
            self.ren.ResetCameraClippingRange()
            overlapActor.SetCamera(self.ren.GetActiveCamera());
            self.ren.AddActor(overlapActor)

        if not actorMap.has_key(actorname) :
            actorMap[actorname] = vtkActor

        # check if there is a material visualisation options

        # set visualisation properties
        if visOptions :
            vtkActor.GetProperty().SetColor(visOptions.color[0],
                                            visOptions.color[1],
                                            visOptions.color[2])
            vtkActor.GetProperty().SetOpacity(visOptions.alpha)
            if visOptions.representation == "surface" :
                vtkActor.GetProperty().SetRepresentationToSurface()
            elif visOptions.representation == "wireframe" :
                vtkActor.GetProperty().SetRepresentationToWireframe()
        else : 
            vtkActor.GetProperty().SetColor(1,0,0)


        vtkActor.SetVisibility(visOptions.visible)
        actors.append(vtkActor)
        self.ren.AddActor(vtkActor)

    def view(self, interactive = True):
        # enable user interface interactor
        self.iren.Initialize()

        # Camera setup
        self.ren.ResetCamera()

        # Render
        self.renWin.Render()

        if interactive : 
            self.iren.Start()

    def setOverlapVisOptions(self, overlaptype):
        visOptions = _VisOptions()
        if overlaptype == _OverlapType.protrusion:
            visOptions.color = [1, 0, 0]
            visOptions.alpha = 1.0
        elif overlaptype == _OverlapType.overlap:
            visOptions.color = [0, 1, 0]
            visOptions.alpha = 1.0
        elif overlaptype == _OverlapType.coplanar:
            visOptions.color = [0, 0, 1]
            visOptions.alpha = 1.0

        return visOptions

def axesFromExtents(extent) :
    low  = _np.array(extent[0])
    high = _np.array(extent[1])
    diff = high-low
    centre = (high+low)/2.0
    length = diff.max()/2

    return length,centre
