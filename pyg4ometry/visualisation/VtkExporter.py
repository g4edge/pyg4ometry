import numpy as _np
import vtk as _vtk
import pyg4ometry.transformation as _transformation
from   pyg4ometry.visualisation  import OverlapType as _OverlapType
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
from   pyg4ometry.visualisation import Convert as _Convert
from pyg4ometry.visualisation import makeVisualisationOptionsDictFromPredefined
from pyg4ometry.visualisation import getPredefinedMaterialVisOptions as _getPredefinedMaterialVisOptions
import logging as _logging

_WITH_PARAVIEW = True
try:
    import paraview.simple as paras
except (ImportError, ImportWarning):
    _WITH_PARAVIEW = False
    msg = "paraview is required for this module to have full functionalities.\n"
    msg += "Not all methods will be available."
    _logging.log(20, msg)


class VtkExporter:
    def __init__(self, path='.'):
        """
        Args:
            path: output repository path
        """
        # directory path
        self.path = path

        # local meshes
        self.localmeshes = {}

        # list of elements
        self.elements = []

        # multi block dictionary
        self.mbdico = {}
        self.mbindexdico = {}

        # material options dict
        self.materialVisualisationOptions = makeVisualisationOptionsDictFromPredefined(_getPredefinedMaterialVisOptions())

    def export_to_Paraview(self, reg, fileName='Paraview_model.pvsm', model=True, df_model=None, df_color=None):
        """
        Method that exports the visible logical volumes of the registry reg into Paraview VTK files (.vtm)
        and creates a Paraview State file (.pvsm) for the Paraview Model.

        df_model and df_color are optional: if they are not given, the Paraview model will take the materials colors

        Args:
            reg: Registry
            fileName: Name of the Paraview State file (.pvsm)
            model: Boolean informing whether we work with a "model" GDML or a "simple" GDML
                True: it will consider that each daughter volume of the GDML world volume will need a .vtm file
                False: it will create one .vtm file for the whole GDML
            df_model: (optional) pandas.DataFrame linking the NAME of the element and their TYPE
            df_color: (optional) pandas.DataFrame linking the TYPE with its specific R G B color
        """
        if _WITH_PARAVIEW:
            self.export_to_VTK(reg, model, df_model, df_color)

            index = 0

            for element in self.elements:
                if "PREPEND" in element:
                    element_name = element[7:]
                else:
                    element_name = element
                xml = paras.XMLMultiBlockDataReader(registrationName=element_name,
                                              FileName=self.path + element + '.vtm', PointArrayStatus="Colors")
                paras.Show(xml, MapScalars=0)
                index += 1
                print((index / len(self.elements)) * 100, ' %')

            paras.Render()

            paras.AssignViewToLayout()

            paras.SaveState(self.path + fileName)

            for x in paras.GetSources().values():
                paras.Delete(x)
        else:
            raise AttributeError("export_to_Paraview is not available as you are missing the paraview module.")

    def export_to_VTK(self, reg, model=True, df_model=None, df_color=None):
        """
        Method that exports the visible logical volumes of the registry reg into Paraview VTK files (.vtm).

        Args:
            reg: Registry
            model: Boolean informing whether we work with a "model" GDML or a "simple" GDML
                True: it will consider that each daughter volume of the GDML world volume will need a .vtm file
                False: it will create one .vtm file for the whole GDML
            df_model: (optional) pandas.DataFrame linking the NAME of the element and their TYPE
            df_color: (optional) pandas.DataFrame linking the TYPE with its specific R G B color

        """
        world_volume = reg.getWorldVolume()

        if df_color is not None and df_model is not None:

            df_gdml = reg.structureAnalysis(world_volume.name)
            color_dico = self.fill_color_dico(df_gdml, df_model, df_color)
            self.add_logical_world_volume(world_volume, model, color_dico)

        else:
            self.add_logical_world_volume(world_volume, model)

    def fill_color_dico(self, df_gdml, df_model, df_color):
        """
        Method that fills a dictionary linking the logical volumes names and their respective
        color based on the pandas.DataFrame df_color linking the TYPE of the elements and
        their respective RGB color values.

        Args:
            df_gdml: pandas.DataFrame that represents the GDML Structure
            df_model: pandas.DataFrame linking the NAME of the element and their TYPE
            df_color: pandas.DataFrame linking the TYPE with its specific R G B color

        Returns: A dictionary with the keys R, G and B whose item is a dictionary
            with as keys the logical volumes names and as item the respective RGB value

        """
        import pandas as pd
        df_color.set_index('TYPE', inplace=True)
        df_gdml.set_index('mother', inplace=True)
        df_model.reset_index(inplace=True)
        df_export_color = pd.DataFrame(columns=["R", "G", "B"])
        for e in range(df_model.shape[0]):
            for lv_name in df_gdml.index:
                element_name = df_model.loc[e, 'NAME'].split('_centre')[0]
                if lv_name[:len(element_name)] == element_name:
                    if "coil" in lv_name:
                        df_export_color.at[lv_name, ["R", "G", "B"]] = df_color.loc['coil', ['R', 'G', 'B']].values
                    elif "beampipe" in lv_name:
                        df_export_color.at[lv_name, ["R", "G", "B"]] = df_color.loc['beampipe', ['R', 'G', 'B']].values
                    else:
                        element_type = df_model.loc[e, 'TYPE']
                        df_export_color.at[lv_name, ["R", "G", "B"]] = df_color.loc[
                            element_type, ['R', 'G', 'B']].values

        return df_export_color.to_dict()

    def add_logical_world_volume(self,
                           lv,
                           model,
                           color_dico={'R': {}, 'G': {}, 'B': {}},
                           rotation=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                           translation=_np.array([0,0,0])
                           ):
        """
        Method that receives the logical world volume and calls the necessary methods
        to write the .vtm file(s).

        Args:
            lv: Logical world volume
            model: Boolean informing whether we work with a "model" GDML or a "simple" GDML
                True: it will consider that each daughter volume of the GDML world volume will need a .vtm file
                False: it will create one .vtm file for the whole GDML
            color_dico: A dictionary with the keys R, G and B whose item is a dictionary
                with as keys the logical volumes names and as item the respective RGB value
            rotation: (optional) numpy.matrix
            translation: (optional) numpy.array

        """
        if model:
            self.add_logical_volume_recursive(lv, rotation, translation, color_dico)
        else:
            self.element_name = self.getElementName(lv.name)

            self.mbdico[self.element_name] = _vtk.vtkMultiBlockDataSet()
            self.mbdico[self.element_name].SetNumberOfBlocks(self.countVisibleDaughters(lv, self.element_name))
            self.mbindexdico[self.element_name] = 0

            self.add_logical_volume_recursive(lv, rotation, translation, color_dico, False)

        for element in self.mbdico.keys():

            self.elements.append(element)

            writer = _vtk.vtkXMLMultiBlockDataWriter()
            writer.SetDataModeToAscii()
            writer.SetInputData(self.mbdico[element])
            print(f"Trying to write file {element}.vtm")
            writer.SetFileName(f"{self.path}/{element}.vtm")
            writer.Write()


    def add_logical_volume_recursive(self, lv, rotation, translation, color_dico, first_level=True):
        """
        Method that receives a logical volume and add calls addMesh() on its mesh.
        The method is recursive and will be called on all the daughter logical volumes of the logical volume.

        Args:
            lv: Logical volume
            rotation: numpy.matrix
            translation: numpy.array
            color_dico: A dictionary with the keys R, G and B whose item is a dictionary
                with as keys the logical volumes names and as item the respective RGB value
            first_level: Boolean indicating if we are at the first level of recursivity

        """
        for pv in lv.daughterVolumes:

            if first_level:

                self.element_name = self.getElementName(pv.logicalVolume.name)

                if self.element_name not in self.mbdico.keys():
                    self.mbdico[self.element_name] = _vtk.vtkMultiBlockDataSet()
                    self.mbdico[self.element_name].SetNumberOfBlocks(self.countVisibleDaughters(lv, self.element_name))
                    self.mbindexdico[self.element_name] = 0

            solid_name = pv.logicalVolume.solid.name

            pvmrot = _np.linalg.inv(_transformation.tbxyz2matrix(pv.rotation.eval()))
            if pv.scale:
                pvmsca = _np.diag(pv.scale.eval())
            else:
                pvmsca = _np.diag([1, 1, 1])
            pvtra = _np.array(pv.position.eval())

            new_mtra = rotation * pvmsca * pvmrot
            new_tra = (_np.array(rotation.dot(pvtra)) + translation)[0]

            mesh = pv.logicalVolume.mesh.localmesh

            if self.materialVisualisationOptions:
                visOptions = self.getMaterialVisOptions(
                    pv.logicalVolume.material.name)
            else:
                visOptions = pv.visOptions

            if pv.logicalVolume.name in color_dico['R'].keys():
                colour = list(visOptions.colour)
                colour[0] = color_dico['R'][pv.logicalVolume.name]
                colour[1] = color_dico['G'][pv.logicalVolume.name]
                colour[2] = color_dico['B'][pv.logicalVolume.name]
                visOptions.colour = tuple(colour)

            self.addMesh(solid_name, mesh, new_mtra, new_tra, visOptions=visOptions)

            self.add_logical_volume_recursive(pv.logicalVolume, new_mtra, new_tra, color_dico, False)

    def addMesh(self, solid_name, mesh, rotation, translation, visOptions = None):

        """
        Method that converts the mesh into VtkPolyData (.vtp file)
        and gives it the correct rotation, translation and color.

        Args:
            solid_name: Name of the logical volume solid
            mesh: Mesh of the logical volume
            rotation: numpy.matrix
            translation: numpy.array
            visOptions: VisualisationOptions instance

        """

        if solid_name in self.localmeshes:
            vtkPD = self.localmeshes[solid_name]
        else:
            vtkPD = _Convert.pycsgMeshToVtkPolyData(mesh)
            self.localmeshes[solid_name] = vtkPD

        vtkTransform = _vtk.vtkMatrix4x4()
        vtkTransform.SetElement(0, 0, rotation[0, 0])
        vtkTransform.SetElement(0, 1, rotation[0, 1])
        vtkTransform.SetElement(0, 2, rotation[0, 2])
        vtkTransform.SetElement(1, 0, rotation[1, 0])
        vtkTransform.SetElement(1, 1, rotation[1, 1])
        vtkTransform.SetElement(1, 2, rotation[1, 2])
        vtkTransform.SetElement(2, 0, rotation[2, 0])
        vtkTransform.SetElement(2, 1, rotation[2, 1])
        vtkTransform.SetElement(2, 2, rotation[2, 2])
        vtkTransform.SetElement(0, 3, translation[0]/1000)
        vtkTransform.SetElement(1, 3, translation[1]/1000)
        vtkTransform.SetElement(2, 3, translation[2]/1000)
        vtkTransform.SetElement(3, 3, 1)

        transformPD = _vtk.vtkTransformPolyDataFilter()
        transform = _vtk.vtkTransform()
        transform.SetMatrix(vtkTransform)
        transform.Scale(1e-3, 1e-3, 1e-3)
        transformPD.SetTransform(transform)

        if visOptions:
            Colors = _vtk.vtkUnsignedCharArray()
            Colors.SetNumberOfComponents(3)
            Colors.SetName("Colors")
            for i in range(vtkPD.GetNumberOfPolys()):
                Colors.InsertNextTuple3(visOptions.colour[0]*255, visOptions.colour[1]*255, visOptions.colour[2]*255);

            vtkPD.GetCellData().SetScalars(Colors)
            vtkPD.Modified()

            if visOptions.visible:
                transformPD.SetInputData(vtkPD)
                transformPD.Update()

                self.mbdico[self.element_name].SetBlock(self.mbindexdico[self.element_name], transformPD.GetOutput())
                self.mbindexdico[self.element_name] += 1

    def getMaterialVisOptions(self, name):
        """
        Method that "cleans" the logical volume material string.

        Args:
            name: raw name of the logical volume material

        Returns: clean name of the logical volume material
        """
        if name.find("0x") != -1 :
            namestrip = name[0:name.find("0x")]
        else:
            namestrip = name

        if namestrip in self.materialVisualisationOptions.keys():
            return self.materialVisualisationOptions[namestrip]
        else:
            print(f"Warning, missing {namestrip} in materialVisualisationOptions, replace by default color")
            return self.materialVisualisationOptions['G4_C']

    def getElementName(self, logicalVolumeName):
        """
        Method that "cleans" the logical volume name string.
        Args:
            logicalVolumeName: raw name of the logical volume

        Returns: clean name of the logical volume
        """
        if "PREPENDworld_" in logicalVolumeName:
            return logicalVolumeName.split('PREPENDworld_')[1].split('0x')[0].split('_lv')[0]
        if "PREPEND_" in logicalVolumeName:
            return logicalVolumeName.split('PREPEND_')[1].split('0x')[0].split('_lv')[0]
        else:
            return logicalVolumeName.split('_container')[0].split('_e1')[0].split('_e2')[0].split('_even')[0].split('_outer')[0].split('_centre')[0].split('_collimator')[0].split('_beampipe')[0].split('0x')[0].split('_lv')[0].split('_bp')[0]

    def countVisibleDaughters(self, lv, element_name, n=0):
        """
        Method that counts the number of "visible" daughter logical volumes of the mother logical volume lv.
        Args:
            lv: logical volume
            element_name: name of the element
            n: number of "visible" daughter volumes

        Returns: n
        """
        for pv in lv.daughterVolumes:
            lv_name = self.getElementName(pv.logicalVolume.name)
            if lv_name == element_name:
                if self.getMaterialVisOptions(pv.logicalVolume.material.name).visible:
                    n += 1
                else:
                    n = self.countVisibleDaughters(pv.logicalVolume, element_name, n)
        return n
