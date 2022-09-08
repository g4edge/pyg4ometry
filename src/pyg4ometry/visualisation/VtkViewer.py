import numpy as _np
import vtk as _vtk
import pyg4ometry.exceptions as _exceptions
import pyg4ometry.transformation as _transformation
from   pyg4ometry.visualisation  import OverlapType as _OverlapType
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
from .VisualisationOptions import getPredefinedMaterialVisOptions as _getPredefinedMaterialVisOptions
from   pyg4ometry.visualisation import Convert as _Convert
import logging as _log
import random as _random

class VtkViewer:
    """
    Visualiser.

    :param size: (int,int) - (nPixelsHorizontal, nPixelsVeritcal), default (1024,1024)
    :param interpolation: (str) - one of "none", "flat", "gouraud", "phong"

    :Examples:

    >>> v = VtkViewer()
    >>> v.addLogicalVolume(someLV)
    >>> v.view()

    """
    # def __init__(self,size=(2048,1536), interpolation="none"):
    def __init__(self, size=(1024, 1024), interpolation="none", **kwargs):
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
        self.renWin.SetSize(size[0],size[1])

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
        self._xCutterOrigin = [0,0,0]
        self._yCutterOrigin = [0,0,0]
        self._zCutterOrigin = [0,0,0]
        self._xCutterNormal = [1,0,0]
        self._yCutterNormal = [0,1,0]
        self._zCutterNormal = [0,0,1]
        self.xcutters = []
        self.ycutters = []
        self.zcutters = []
        self.usercutters = []

        # axes
        self.axes = []

        # axes widget
        self.addAxesWidget()

        # material options dict
        self.materialVisOptions = None

        # interpolation for vertex shading
        interps = ("none", "flat", "gouraud", "phong")
        if interpolation not in interps:
            raise ValueError("Unrecognised interpolation option {}."
                             " Possible options are :{}".format(interpolation, ", ".join(interps)))
        self.interpolation = interpolation

    def addAxes(self, length = 20.0, origin = (0,0,0)):
        """
        Add x,y,z axis to the scene.
        
        :param length: float - length of each axis in mm
        :param origin: (float,float,float) - (x,y,z) of origin in mm
        """
        axes = _vtk.vtkAxesActor()

        # transform to move axes
        tran = _vtk.vtkTransform()
        tran.Translate(origin[0],origin[1], origin[2])
        axes.SetUserTransform(tran)

        self.axes.append(axes)
        axes.SetTotalLength(length,length,length)
        self.ren.AddActor(axes)

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

    def setOpacity(self, v, iActor=-1):
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

    def setRandomColours(self, seed = 0):

        _random.seed(seed)

        for a in self.actors:
            a.GetProperty().SetColor(_random.random(),
                                     _random.random(),
                                     _random.random())

    def setCutterOrigin(self, dimension, origin):
        """
        :param dimension: str - 'x', 'y', or 'z'
        :param origin: list([x,y,z])
        """
        if dimension == 'x':
            self._xCutterOrigin = origin
        elif dimension == 'y':
            self._yCutterOrigin = origin
        elif dimension == 'z':
            self._zCutterOrigin = origin
        else:
            raise ValueError("invalid dimension - x,y or z")

    def setCutterNormal(self, dimension, normal):
        """
        :param dimension: str - 'x', 'y', or 'z'
        :param normal: list([x,y,z]) -  should be unit vector
        """
        if dimension == 'x':
            self._xCutterNormal = normal
        elif dimension == 'y':
            self._yCutterNormal = normal
        elif dimension == 'z':
            self._zCutterNormal = normal
        else:
            raise ValueError("invalid dimension - x,y or z")

    def addMaterialVisOption(self, materialName, visOptionInstance):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: str - material name to match
        :param visOptionInstance: :class:`VisualisationOptions` instance
        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOptionInstance

    def setMaterialVisOptions(self, materialDict):
        """
        Replace the (by default None) dictionary for materials to colours
        :param materialDict: {"materialName": VisualisationOptions}

        See also :class:`VisualisationOptions`.
        """
        self.materialVisOptions = materialDict

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

    def exportGLTFScene(self,fileName="scene.gltf"):
        rw = _vtk.vtkRenderWindow()
        rw.AddRenderer(self.renWin.GetRenderers().GetFirstRenderer())

        exporter = _vtk.vtkGLTFExporter()
        exporter.SetRenderWindow(rw)
        exporter.InlineDataOn()
        exporter.SetFileName("./"+fileName)
        exporter.Write()

    def exportScreenShot(self, fileName="screenshot.png", rgba=True):
        """
        Write the render window view to an image file.

        Image types supported are:
        BMP, JPEG, PNM, PNG, PostScript, TIFF.
        The default parameters are used for all writers, change as needed.

        :param fileName: The file name, if no extension then PNG is assumed.
        :param renWin: The render window.
        :param rgba: Used to set the buffer type.
        :return:
        """
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


    def addLogicalVolume(self, logical, mtra=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra=_np.array([0,0,0]), recursive=True):
        if logical.type == "logical":
            self.addLogicalVolumeBounding(logical)
            for [overlapmesh, overlaptype], i in zip(logical.mesh.overlapmeshes,
                                                     range(0, len(logical.mesh.overlapmeshes))):
                visOptions = self.getOverlapVisOptions(overlaptype)
                self.addMesh(logical.name, logical.solid.name + "_overlap" + str(i), overlapmesh, mtra, tra,
                             self.localmeshesOverlap, self.filtersOverlap,
                             self.mappersOverlap, self.physicalMapperMapOverlap, self.actorsOverlap,
                             self.physicalActorMapOverlap,
                             visOptions=visOptions, overlap=True, cutters=False)

        if recursive:
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

    def addSolid(self, solid, rotation=[0,0,0], position=[0,0,0], representation="surface", colour=[0.5,0.5,0.5], opacity=0.2):
        """
        Add a solid to the view with an optional rotation and translation.

        :param solid: solid to add to the view
        :type  solid: any solid in pyg4ometry.geant4.solid
        :param rotation: list of TB rotation angles in radians
        :type  rotation: list(float, float, float) - 3 values
        :param position: translation in global from from centre in mm
        :type  position: list(float, float, float) - 3 values
        :param representation: the way to visualise it, e.g. 'surface' or 'wireframe'
        :type  representation: str
        :param colour: normalised rgb colour to use for the solid mesh
        :type  colour: list(float, float, float) - 3 values ranging from 0 - 1
        :param opacity: the opacity of the solid if surface style
        :type  opacity: float, from 0 to 1
        """
        mesh = solid.mesh()
        visOptions = _VisOptions()
        visOptions.representation = representation
        visOptions.alpha = opacity
        visOptions.color = colour
        mrot = _np.linalg.inv(_transformation.tbxyz2matrix(rotation))
        mtra = _np.array(position)
        self.addMesh(solid.name, solid.name, mesh, mrot, mtra, self.localmeshes,
                     self.filters, self.mappers, self.physicalMapperMap, self.actors,
                     self.physicalActorMap, visOptions=visOptions, overlap=False, cutters=False)

    def addBooleanSolidRecursive(self, solid, mtra=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]), tra=_np.array([0,0,0]), first=True):
        """
        :param solid: pyg4ometry.geant4.solid instance.
        :type  solid: pyg4ometry.geant4.solid.SolidBase

        Other parameters are for internal recursion and don't need to be provided.

        Render only a Boolean solid. If one of the constituent solids is also a Boolean, visualise those too. The
        resultant Boolean is shown in solid form and each constituent in a wireframe. In the case of a null mesh,
        only the constituents can be shown.
        """

        if solid.type == "Union" or solid.type == "Subtraction" or solid.type == "Intersection":

            if first:
                try:
                    mesh = solid.mesh()
                    visOptions = _VisOptions()
                    visOptions.representation = "surface"
                    visOptions.alpha = 1.0
                    visOptions.color = [0.5, 0.5, 0.5]
                    self.addMesh(solid.name, solid.name, mesh, mtra, tra, self.localmeshes,
                                self.filters, self.mappers, self.physicalMapperMap, self.actors,
                                self.physicalActorMap, visOptions=visOptions, overlap=False, cutters=False)
                    first = False
                except _exceptions.NullMeshError:
                    print(solid.name,"> null mesh... continuing")

            obj1 = solid.object1()
            obj2 = solid.object2()

            tran = solid.translation()
            rotn = solid.rotation()

            rotm = _transformation.tbxyz2matrix(rotn)
            new_mtra = mtra * rotm
            new_tra  = (_np.array(mtra.dot(tran)) + tra)[0]

            self.addBooleanSolidRecursive(obj1, mtra, tra, first)
            self.addBooleanSolidRecursive(obj2, new_mtra, new_tra, first)
        else:
            mesh = solid.mesh()
            visOptions = _VisOptions()
            visOptions.representation = "wireframe"
            visOptions.alpha = 0.5
            visOptions.color = [1,0,0]
            self.addMesh(solid.name, solid.name, mesh, mtra, tra, self.localmeshes,
                         self.filters, self.mappers, self.physicalMapperMap, self.actors,
                         self.physicalActorMap, visOptions=visOptions, overlap=False, cutters=False)


    def addMeshSimple(self, csgMesh, visOptions=_VisOptions(), clip=False, name = "mesh"):
        if clip:
            csgMesh = csgMesh.clone()
            verts, _, _ = csgMesh.toVerticesAndPolygons()
            x = _np.array([v[0] for v in verts])
            y = _np.array([v[1] for v in verts])
            z = _np.array([v[2] for v in verts])
            xsize = max(x) - min(x)
            ysize = max(y) - min(y)
            zsize = max(z) - min(z)
            t = -_np.array([min(x) + xsize/2.,
                            min(y) + ysize/2.,
                            min(z) + ysize/2.])
            csgMesh.translate(t)

        self.addMesh(name, name, csgMesh,
                     _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                     _np.array([0, 0, 0]),
                     self.localmeshes,
                     self.filters, self.mappers, self.physicalMapperMap, self.actors,
                     self.physicalActorMap, visOptions=visOptions, overlap=False, cutters=False)


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

                if pv.logicalVolume.type != "assembly" and pv.logicalVolume.mesh is not None :
                    mesh = pv.logicalVolume.mesh.localmesh # TODO implement a check if mesh has changed
                    # mesh = _Mesh(pv.logicalVolume.solid).localmesh

                    visOptions = self.getMaterialVisOptions(pv)
                    self.addMesh(pv_name, solid_name, mesh, new_mtra, new_tra, self.localmeshes, self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions=visOptions, overlap=False)

                    # overlap meshes
                    for [overlapmesh,overlaptype], i in zip(pv.logicalVolume.mesh.overlapmeshes,range(0,len(pv.logicalVolume.mesh.overlapmeshes))) :
                        visOptions = self.getOverlapVisOptions(overlaptype)

                        self.addMesh(pv_name, solid_name+"_overlap"+str(i), overlapmesh, new_mtra, new_tra, self.localmeshesOverlap,
                                     self.filtersOverlap, self.mappersOverlap, self.physicalMapperMapOverlap, self.actorsOverlap,
                                     self.physicalActorMapOverlap, visOptions=visOptions, overlap=True)

                self.addLogicalVolumeRecursive(pv.logicalVolume,new_mtra,new_tra)

            elif pv.type == "replica" or pv.type == "division":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0])
                    pvtra = _np.array(trans[1])
                    
                    # pv compound transform
                    new_mtra = mtra * pvmrot
                    new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                    # TBC - should pv.visOptions be used exclusively?
                    self.addMesh(pv_name, mesh.solid.name, mesh.localmesh, new_mtra, new_tra, self.localmeshes, self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions=pv.visOptions, overlap=False)
            elif pv.type == "parametrised":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0].eval())
                    pvtra = _np.array(trans[1].eval())

                    # pv compound transform
                    new_mtra = mtra * pvmrot
                    new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                    # TBC - should pv.visOptions be used exclusively?
                    self.addMesh(pv_name, mesh.solid.name, mesh.localmesh, new_mtra, new_tra, self.localmeshes, self.filters,
                                 self.mappers, self.physicalMapperMap, self.actors, self.physicalActorMap,
                                 visOptions=pv.visOptions, overlap=False)

    def addMesh(self, pv_name, solid_name, mesh, mtra, tra, localmeshes, filters,
                mappers, mapperMap, actors, actorMap, visOptions=None, overlap=False,
                cutters=True, clippers=False):
        # VtkPolyData : check if mesh is in localmeshes dict
        _log.info('VtkViewer.addLogicalVolume> vtkPD')

        if solid_name in localmeshes:
            vtkPD = localmeshes[solid_name]
        else :
            if clippers :
                clipper_min_x =  0
                clipper_min_y =  0
                clipper_min_z = -1e6

                clipper_max_x = 1e6
                clipper_max_y = 1e6
                clipper_max_z = 1e6

                clipper_d_x = clipper_max_x - clipper_min_x
                clipper_d_y = clipper_max_y - clipper_min_y
                clipper_d_z = clipper_max_z - clipper_min_z

                clipper_c_x = (clipper_max_x + clipper_min_x)/2.0
                clipper_c_y = (clipper_max_y + clipper_min_y)/2.0
                clipper_c_z = (clipper_max_z + clipper_min_z)/2.0

                import pyg4ometry

                reg = pyg4ometry.geant4.Registry()
                b = pyg4ometry.geant4.solid.Box("b",clipper_d_x, clipper_d_y, clipper_d_z,reg,"mm",False)
                bm = b.mesh()
                bm.translate([clipper_c_x,clipper_c_y,clipper_c_z])
                aa = pyg4ometry.transformation.matrix2axisangle(mtra)
                meshclone = mesh.clone()
                meshclone.rotate(aa[0],-aa[1]/_np.pi*180.)
                meshclone.translate([tra[0],tra[1],tra[2]])
                meshclone = meshclone.subtract(bm)
                meshclone.translate([-tra[0],-tra[1],-tra[2]])
                meshclone.rotate(aa[0],aa[1]/_np.pi*180.)
                vtkPD = _Convert.pycsgMeshToVtkPolyData(meshclone)

            else :
                vtkPD = _Convert.pycsgMeshToVtkPolyData(mesh)
                localmeshes[solid_name] = vtkPD

        if self.interpolation != "none":
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
        if filtername in filters:
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

        if not mappername in mapperMap:
            mapperMap[mappername] = vtkMAP
            
        # Actor
        actorname = pv_name+"_actor"             
        vtkActor = _vtk.vtkActor() 
        vtkActor.SetMapper(vtkMAP)
        vtkActor.name = actorname

        if self.interpolation != "none":
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

        def makeCutterPlane(origin, normal, color) :

            plane = _vtk.vtkPlane()
            plane.SetOrigin(*origin)
            plane.SetNormal(*normal)
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
            planeActor.GetProperty().SetColor(*color)
            planeActor.GetProperty().SetRepresentationToSurface()
            self.ren.AddActor(planeActor)

            return cutter

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
            clipperActor.GetProperty().SetOpacity(0.5)
            clipperActor.SetScale(1, 1, 1)

            vtkActor.GetProperty().SetOpacity(0.0)
            self.ren.AddActor(clipperActor)  # selection part end

        if cutters :
            self.xcutters.append(makeCutterPlane(self._xCutterOrigin, self._xCutterNormal, [1,0,0]))
            self.ycutters.append(makeCutterPlane(self._yCutterOrigin, self._yCutterNormal, [0,1,0]))
            self.zcutters.append(makeCutterPlane(self._zCutterOrigin, self._zCutterNormal, [0,0,1]))

        #if clippers :
        #    makeClipperPlane([1,0,0])
        #    makeClipperPlane([0,1,0])
        #    makeClipperPlane([0,0,1])

        if overlap :
            overlapText = _vtk.vtkVectorText()
            overlapText.SetText("overlap")

            overlapMapper = _vtk.vtkPolyDataMapper()
            overlapMapper.SetInputConnection(overlapText.GetOutputPort())

            comFilter = _vtk.vtkCenterOfMass()
            comFilter.SetInputConnection(vtkTransFLT.GetOutputPort())
            comFilter.SetUseScalarsAsWeights(False)
            comFilter.Update()

            overlapActor = _vtk.vtkFollower()
            overlapActor.GetProperty().SetColor(*visOptions.getColour())
            overlapActor.SetPosition(comFilter.GetCenter())
            overlapActor.SetMapper(overlapMapper)
            self.ren.ResetCameraClippingRange()
            overlapActor.SetCamera(self.ren.GetActiveCamera())
            self.ren.AddActor(overlapActor)

        if not actorname in actorMap:
            actorMap[actorname] = vtkActor

        # check if there is a material visualisation options

        # set visualisation properties
        if visOptions:
            vtkActor.GetProperty().SetColor(*visOptions.getColour())
            vtkActor.GetProperty().SetOpacity(visOptions.alpha)
            if visOptions.representation == "surface":
                vtkActor.GetProperty().SetRepresentationToSurface()
            elif visOptions.representation == "wireframe":
                vtkActor.GetProperty().SetRepresentationToWireframe()
        else:
            vtkActor.GetProperty().SetColor(1,0,0)

        vtkActor.SetVisibility(visOptions.visible)
        actors.append(vtkActor)
        self.ren.AddActor(vtkActor)

    def view(self, interactive=True, resetCamera=True ):
        # enable user interface interactor
        self.iren.Initialize()

        # Camera setup
        if resetCamera:
            self.ren.ResetCamera()

        # Render
        self.renWin.Render()

        if interactive:
            self.iren.Start()

    def _getCutterData(self, axis='x', scaling=1.0):
        if axis == 'x':
            cutters = self.xcutters
        elif axis == 'y':
            cutters = self.ycutters
        elif axis == 'z':
            cutters = self.zcutters
        else:
            raise ValueError("axis is not one of x,y,z")

        allX = []
        allY = []
        for c in cutters:
            pd = c.GetOutput()
            xs,ys = [],[]
            for i in range(0,pd.GetNumberOfCells(),1) :
                idl = _vtk.vtkIdList()
                pd.GetCellPoints(i,idl)
                x,y = [],[]
                for j in range(0,idl.GetNumberOfIds(),1) :
                    p = pd.GetPoint(idl.GetId(j))

                    if axis == 'x':
                        x.append(p[1]*scaling)
                        y.append(p[2]*scaling)
                    elif axis == 'y':
                        x.append(p[0]*scaling)
                        y.append(p[2]*scaling)
                    elif axis == 'z':
                        x.append(p[0]*scaling)
                        y.append(p[1]*scaling)
                if len(x) > 0 and len(y) > 0:
                    allX.append(x)
                    allY.append(y)
        return allX,allY

    def exportCutterSection(self, filename, normal='x', scaling=1.0):
        """
        Export the section lines in plane perpendicular to normal.
        Exported as json text. 
        
        :param filename: (str) - name of file to export to
        :param normal: (str) - one of "x", "y" or "z"
        :param scaling: (float) - multiplier for all cutter line coordinates on export

        :Examples:

        >>> v.exportCutterSection("xz-section.dat", normal="y", scaling=1000)
        """
        d = self._getCutterData(normal, scaling)
        import json
        f = open(filename, 'w')
        json.dump(d,f)
        f.close()

    def viewSection(self, dir='x'):
        import matplotlib.pyplot as _plt
        #from vtk.numpy_interface import dataset_adapter as dsa

        if dir == 'x':
            cutters = self.xcutters
        elif dir == 'y':
            cutters = self.ycutters
        elif dir == 'z':
            cutters = self.zcutters
        else:
            raise ValueError("Unknown direction " + dir)

        for c in cutters:
            pd = c.GetOutput()
            for i in range(0, pd.GetNumberOfCells(), 1):
                idl = _vtk.vtkIdList()
                pd.GetCellPoints(i, idl)

                x = []
                y = []

                for j in range(0, idl.GetNumberOfIds(), 1):
                    p = pd.GetPoint(idl.GetId(j))

                    if dir == 'x':
                        x.append(p[1])
                        y.append(p[2])
                    elif dir == 'y':
                        x.append(p[0])
                        y.append(p[2])
                    elif dir == 'z':
                        x.append(p[0])
                        y.append(p[1])

                _plt.plot(x, y, color='k')

    def addCutterPlane(self, position, normal, colour=None):
        """
        Add a cutting plane at position=[x,y,z] with normal [nx,ny,nz].

        :param position: [float, float, float] - (x,y,z) position in scene (mm)
        :param normal:   [float, float, float] - (nx,ny,z) normal unit vector
        :param colour: None or [float, float, float] - [r,g,b] in range [0:1]
        
        Cutters are stored in self.usercutters.
        """
        if colour is None:
            colour = [1, 0.6, 0.2]
        plane = _vtk.vtkPlane()
        plane.SetOrigin(*position)
        plane.SetNormal(*normal)
        vtkTransFLT = _vtk.vtkTransformFilter()
        vtkTransform1 = _vtk.vtkTransform()
        vtkTransFLT.SetTransform(vtkTransform1)

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
        planeActor.GetProperty().SetColor(*colour)
        planeActor.GetProperty().SetRepresentationToSurface()
        self.ren.AddActor(planeActor)
        self.usercutters.append(cutter)

    def addActor(self, actor):
        self.ren.AddActor(actor)

    def getOverlapVisOptions(self, overlaptype):
        visOptions = _VisOptions()
        if overlaptype == _OverlapType.protrusion:
            visOptions.colour = [1, 0, 0]
            visOptions.alpha = 1.0
        elif overlaptype == _OverlapType.overlap:
            visOptions.colour = [0, 1, 0]
            visOptions.alpha = 1.0
        elif overlaptype == _OverlapType.coplanar:
            visOptions.colour = [0, 0, 1]
            visOptions.alpha = 1.0

        return visOptions

    def getMaterialVisOptions(self, pv):
        # a dict evaluates to True if not empty
        if self.materialVisOptions:
            materialName = pv.logicalVolume.material.name
            # if 0x is in name, strip the appended pointer (common in exported GDML)
            if "0x" in materialName:
                materialName = materialName[0:materialName.find("0x")]
            # get with default
            v = self.materialVisOptions.get(materialName, pv.visOptions)
        else:
            v = self._getDefaultVis(pv)
        return v

    def _getDefaultVis(self, pv):
        return pv.visOptions

    def printViewParameters(self):
        activeCamera = self.ren.GetActiveCamera()
        print("Window size     ", self.renWin.GetSize())
        print("Focal point     ", activeCamera.GetFocalPoint())
        print("Camera position ", activeCamera.GetPosition())
        print("Focal distance  ", activeCamera.GetDistance())
        
class VtkViewerColoured(VtkViewer):
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
        super().__init__(*args, **kwargs)
        self.materialVisOptions = {}

        self._defaultVis = _VisOptions()
        self._defaultVis.randomColour = defaultColour == "random"
        if type(defaultColour) is list:
            self._defaultVis.colour = defaultColour

        # loop over dictionary of material vis options - if value is list(rgba)
        # convert to vis options instance, make invisible if alpha is 0
        if materialVisOptions:
            for k,v in materialVisOptions.items():
                if type(v) is list or type(v) is tuple:
                    vi = _VisOptions()
                    vi.colour = v[:3]
                    if any([i>1 for i in vi.colour]):
                        vi.colour = [i/255.0 for i in vi.colour]
                    if len(v) > 3:
                        vi.alpha = v[3]
                        vi.visible = vi.alpha != 0
                    self.materialVisOptions[k] = vi
                else:
                    self.materialVisOptions[k] = v

    def _getDefaultVis(self, pv):
        return self._defaultVis

# for backwards compatibility for old name
PubViewer = VtkViewerColoured

class VtkViewerColouredMaterial(PubViewer):
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


def axesFromExtents(extent):
    low  = _np.array(extent[0])
    high = _np.array(extent[1])
    diff = high-low
    centre = (high+low)/2.0
    length = diff.max()/2

    return length,centre

def viewLogicalVolumeDifference(referenceLV, otherLV, otherTranslation=[0,0,0], otherRotation=[0,0,0], viewDifference=True):
    """
    :param referenceLV: LogicalVolume instance to view viewed in red.
    :type  referenceLV: pyg4ometry.geant4.LogicalVolume.
    :param referenceLV: LogicalVolume instance to view viewed in blue.
    :type  referenceLV: pyg4ometry.geant4.LogicalVolume.
    :param otherTranslation: Translation (in native units, mm) of otherLV w.r.t. referenceLV
    :type  otherTranslation: [float, float, float]
    :param otherRotation: Rotation (in native units, rad) of other LV w.r.t. referenceLV.
    :type  otherRotation: [float, float, float]

    View the shapes of 2 logical volumes without their contents. The reference one will be red and
    the 'other' one will be blue.

    The other one may optionally be translated and rotated (Tait-Bryant x,y,z) relative to the reference.
    """
    lvr = referenceLV
    lvo = otherLV
    v = VtkViewer()

    visOptions1 = _VisOptions()
    visOptions1.colour = [1.0, 0.0, 0.0] # red
    visOptions1.alpha = 0.4
    mtra = _np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    v.addMesh("referenceLV", lvr.solid.name, lvr.mesh.localmesh, mtra, _np.array([0, 0, 0]),
              v.localmeshes, v.filters, v.mappers, v.physicalMapperMap, v.actors, v.physicalActorMap,
              visOptions=visOptions1, overlap=False)

    visOptions2 = _VisOptions()
    visOptions2.colour = [0.0, 0.0, 1.0]  # blue
    visOptions2.alpha = 0.4
    oRotation = _transformation.tbxyz2matrix(otherRotation)
    oTranslation = _np.array(otherTranslation)
    v.addMesh("otherLV", lvo.solid.name, lvo.mesh.localmesh, oRotation, oTranslation,
              v.localmeshes, v.filters, v.mappers, v.physicalMapperMap, v.actors, v.physicalActorMap,
              visOptions=visOptions2, overlap=False)

    if viewDifference:
        oMeshClone = lvo.mesh.localmesh.clone()
        #aa = oRotation
        import pyg4ometry
        #print(pyg4ometry.pycgal.geom.Vector(aa[0]))
        aa = _transformation.matrix2axisangle(oRotation)
        tra = oTranslation
        oMeshClone.rotate(aa[0], -aa[1] / _np.pi * 180.)
        oMeshClone.translate([tra[0], tra[1], tra[2]])
        differenceMesh = oMeshClone.subtract(lvr.mesh.localmesh.clone())
        visOptions3 = _VisOptions()
        visOptions3.colour = [0.0, 1.0, 0.0]  # blue
        visOptions3.alpha = 0.8
        v.addMesh("difference-mesh", "difference-solid", differenceMesh, mtra, _np.array([0, 0, 0]),
                  v.localmeshes, v.filters, v.mappers, v.physicalMapperMap, v.actors, v.physicalActorMap,
                  visOptions=visOptions3, overlap=False)

    v.view()
    return v