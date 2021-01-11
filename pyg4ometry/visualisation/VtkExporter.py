import numpy as _np
import vtk as _vtk
import pyg4ometry.transformation as _transformation
from   pyg4ometry.visualisation  import OverlapType     as _OverlapType
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
from   pyg4ometry.visualisation import Convert as _Convert
from pyg4ometry.visualisation import makeVisualisationOptionsDictFromPredefined
import logging as _log
import random
from . import colour

class VtkExporter:
    def __init__(self, size=(1024, 1024), interpolation="none"):
        # create a renderer
        self.ren = _vtk.vtkRenderer()

        # create a rendering window
        self.renWin = _vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)

        # create a rendering window interactor
        self.iren = _vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)

        # add the custom style
        style = MouseInteractorNamePhysicalVolume(self.ren, self)
        style.SetDefaultRenderer(self.ren)
        self.iren.SetInteractorStyle(style)

        self.ren.SetBackground(1.0, 1.0, 1.0)
        self.renWin.SetSize(size[0], size[1])

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

        # cutters
        self.xcutters = []
        self.ycutters = []
        self.zcutters = []

        # axes
        self.axes = []

        # axes widget
        self.addAxesWidget()

        # material options dict
        self.materialVisualisationOptions = makeVisualisationOptionsDictFromPredefined(colour.ColourMap().fromPredefined())

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

    def add_logical_volume(self,
                           lv,
                           rotation=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                           translation=_np.array([0,0,0])
                           ):
        if lv.type == "logical" :
            self.addLogicalVolumeBounding(lv)
            for [overlapmesh, overlaptype], i in zip(lv.mesh.overlapmeshes,
                                                     range(0, len(lv.mesh.overlapmeshes))):
                visOptions = self.setOverlapVisOptions(overlaptype)
                self.addMesh(lv.name, lv.solid.name + "_overlap" + str(i), overlapmesh, rotation, translation,
                             self.localmeshesOverlap, self.filtersOverlap,
                             self.mappersOverlap, self.physicalMapperMapOverlap, self.actorsOverlap,
                             self.physicalActorMapOverlap,
                             visOptions = visOptions, overlap = True, cutters=False)

        self._add_logical_volume_recursive(lv, rotation, translation)

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

    def _add_logical_volume_recursive(self, lv, rotation, translation):
        for pv in lv.daughterVolumes:

            if pv.logicalVolume.type != "assembly":
                solid_name = pv.logicalVolume.solid.name
            else:
                solid_name = "none"

            if pv.logicalVolume.type == "logical":
                _log.info('VtkViewer.addLogicalVolume> Daughter %s %s %s ' % (pv.name, pv.logicalVolume.name, pv.logicalVolume.solid.name))

            if pv.type == "placement":
                # pv transform
                pvmrot = _np.linalg.inv(_transformation.tbxyz2matrix(pv.rotation.eval()))
                if pv.scale:
                    pvmsca = _np.diag(pv.scale.eval())
                else:
                    pvmsca = _np.diag([1, 1, 1])
                pvtra = _np.array(pv.position.eval())

                # pv compound transform
                new_mtra = rotation * pvmsca * pvmrot
                new_tra = (_np.array(rotation.dot(pvtra)) + translation)[0]

                if pv.logicalVolume.type != "assembly":
                    mesh = pv.logicalVolume.mesh.localmesh

                    if self.materialVisualisationOptions:
                        visOptions = self.getMaterialVisOptions(
                            pv.logicalVolume.material.name)
                    else:
                        visOptions = pv.visOptions


                    self.addMesh(pv.name, solid_name, mesh, new_mtra, new_tra, self.localmeshes, self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions=visOptions, overlap=False)

                    # overlap meshes
                    for [overlapmesh, overlaptype], i in zip(pv.logicalVolume.mesh.overlapmeshes,
                                                             range(0, len(pv.logicalVolume.mesh.overlapmeshes))):
                        visOptions = self.setOverlapVisOptions(overlaptype)

                        self.addMesh(pv.name, solid_name + "_overlap" + str(i), overlapmesh, new_mtra, new_tra,
                                     self.localmeshesOverlap,
                                     self.filtersOverlap, self.mappersOverlap, self.physicalMapperMapOverlap,
                                     self.actorsOverlap,
                                     self.physicalActorMapOverlap, visOptions=visOptions, overlap=True)

                self._add_logical_volume_recursive(pv.logicalVolume, new_mtra, new_tra)

            elif pv.type == "replica" or pv.type == "division":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0])
                    pvtra = _np.array(trans[1])

                    # pv compound transform
                    new_mtra = rotation * pvmrot
                    new_tra = (_np.array(rotation.dot(pvtra)) + translation)[0]

                    self.addMesh(pv.name, mesh.solid.name, mesh.localmesh, new_mtra, new_tra, self.localmeshes,
                                 self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions=pv.visOptions, overlap=False)
            elif pv.type == "parametrised":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0].eval())
                    pvtra = _np.array(trans[1].eval())

                    # pv compound transform
                    new_mtra = rotation * pvmrot
                    new_tra = (_np.array(rotation.dot(pvtra)) + translation)[0]

                    self.addMesh(pv.name, mesh.solid.name, mesh.localmesh, new_mtra, new_tra, self.localmeshes,
                                 self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions=pv.visOptions, overlap=False)

    def addMesh(self, pv_name, solid_name, mesh, mtra, tra, localmeshes, filters,
                mappers, mapperMap, actors, actorMap, visOptions = None, overlap = False,
                cutters = True, clippers = False):

        # VtkPolyData : check if mesh is in localmeshes dict
        _log.info('VtkViewer.addLogicalVolume> vtkPD')

        if solid_name in localmeshes:
            vtkPD = localmeshes[solid_name]
        else:
            vtkPD = _Convert.pycsgMeshToVtkPolyData(mesh)
            localmeshes[solid_name] = vtkPD

        if self.interpolation is not "none":
            normal_generator = _vtk.vtkPolyDataNormals()
            normal_generator.SetInputData(vtkPD)
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
        filtername = solid_name + "_filter"
        if filtername in filters:
            vtkFLT = filters[filtername]
        else:
            vtkFLT = _vtk.vtkTriangleFilter()  # TODO HERE
            vtkFLT.AddInputData(vtkPD)  # TODO HERE
            filters[filtername] = vtkFLT

        # Mapper
        _log.info('VtkViewer.addLogicalVolume> vtkMAP')
        mappername = pv_name + "_mapper"
        vtkMAP = _vtk.vtkPolyDataMapper()
        vtkMAP.ScalarVisibilityOff()
        # TRIANGLE/NON-TRIANGLE FILTER
        # vtkMAP.SetInputConnection(vtkFLT.GetOutputPort())
        vtkMAP.SetInputData(vtkPD)

        mappers.append(vtkMAP)

        if not mappername in mapperMap:
            mapperMap[mappername] = vtkMAP

        # Actor
        actorname = pv_name + "_actor"
        vtkActor = _vtk.vtkActor()
        vtkActor.SetMapper(vtkMAP)
        vtkActor.name = actorname

        if self.interpolation is not "none":
            if self.interpolation == "gouraud":
                vtkActor.GetProperty().SetInterpolationToGouraud()
            elif self.interpolation == "phong":
                vtkActor.GetProperty().SetInterpolationToPhong()
            elif self.interpolation == "flat":
                vtkActor.GetProperty().SetInterpolationToFlat()

        if not actorname in actorMap:
            actorMap[actorname] = vtkActor

        # check if there is a material visualisation options

        # set visualisation properties
        if visOptions :
            vtkActor.GetProperty().SetColor(visOptions.color[0],
                                            visOptions.color[1],
                                            visOptions.color[2])
            if visOptions.visible:
                vtkActor.GetProperty().SetOpacity(visOptions.alpha)
            else:
                vtkActor.GetProperty().SetOpacity(0)

            if visOptions.representation == "surface" :
                vtkActor.GetProperty().SetRepresentationToSurface()
            elif visOptions.representation == "wireframe" :
                vtkActor.GetProperty().SetRepresentationToWireframe()
        else :
            vtkActor.GetProperty().SetColor(1,0,0)


        vtkActor.SetVisibility(visOptions.visible)
        actors.append(vtkActor)
        self.ren.AddActor(vtkActor)


        vtkTransform = _vtk.vtkMatrix4x4()
        vtkTransform.SetElement(0, 0, mtra[0, 0])
        vtkTransform.SetElement(0, 1, mtra[0, 1])
        vtkTransform.SetElement(0, 2, mtra[0, 2])
        vtkTransform.SetElement(1, 0, mtra[1, 0])
        vtkTransform.SetElement(1, 1, mtra[1, 1])
        vtkTransform.SetElement(1, 2, mtra[1, 2])
        vtkTransform.SetElement(2, 0, mtra[2, 0])
        vtkTransform.SetElement(2, 1, mtra[2, 1])
        vtkTransform.SetElement(2, 2, mtra[2, 2])
        vtkTransform.SetElement(0, 3, tra[0]/1000)
        vtkTransform.SetElement(1, 3, tra[1]/1000)
        vtkTransform.SetElement(2, 3, tra[2]/1000)
        vtkTransform.SetElement(3, 3, 1)

        vtkActor.SetUserMatrix(vtkTransform)

        transformPD = _vtk.vtkTransformPolyDataFilter()
        transform = _vtk.vtkTransform()
        transform.SetMatrix(vtkTransform)
        transform.Scale(1e-3, 1e-3, 1e-3)
        transformPD.SetTransform(transform)

        if visOptions:
            Colors = _vtk.vtkUnsignedCharArray();
            Colors.SetNumberOfComponents(3);
            Colors.SetName("Colors");
            for i in range(vtkPD.GetNumberOfPolys()):
                Colors.InsertNextTuple3(visOptions.color[0]*255, visOptions.color[1]*255, visOptions.color[1]*255);

            vtkPD.GetCellData().SetScalars(Colors)
            vtkPD.Modified()

            if visOptions.visible:
                transformPD.SetInputData(vtkPD)
                transformPD.Update()

                writer = _vtk.vtkXMLPolyDataWriter()
                writer.SetDataModeToAscii()
                writer.SetInputData(transformPD.GetOutput())
                print(f"Trying to write file ./{pv_name}.vtp")
                writer.SetFileName(f"./vtp_files/{pv_name}.vtp")
                writer.Write()




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

    def getMaterialVisOptions(self, name):
        if name.find("0x") != -1 :
            nameStrip = name[0:name.find("0x")]
        else :
            nameStrip = name
        return self.materialVisualisationOptions[nameStrip]

    def view(self, interactive = True, resetCamera = True ):
        # enable user interface interactor
        self.iren.Initialize()

        # Camera setup
        if resetCamera :
            self.ren.ResetCamera()

        # Render
        self.renWin.Render()

        if interactive :
            self.iren.Start()

class MouseInteractorNamePhysicalVolume(_vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, renderer, vtkviewer):
        self.AddObserver("RightButtonPressEvent", self.rightButtonPressEvent)

        self.renderer = renderer
        self.vtkviewer = vtkviewer

    def rightButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = _vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)


        actor = picker.GetActor()
        # If an actor was right clicked
        if actor:
            actorMap = self.vtkviewer.physicalActorMap
            try:
                name = next((x[0] for x in actorMap.items() if x[1] is actor))
            # E.g. the axes actor or some other actor we don't wish to name.
            except StopIteration:
                pass
            else:
                name = name[:name.find("_actor")]
                print(f"{type(self.vtkviewer).__name__}> selected> {name}")
