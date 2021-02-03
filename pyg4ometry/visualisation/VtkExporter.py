import numpy as _np
import vtk as _vtk
import pyg4ometry.transformation as _transformation
from   pyg4ometry.visualisation  import OverlapType     as _OverlapType
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
from   pyg4ometry.visualisation import Convert as _Convert
from pyg4ometry.visualisation import makeVisualisationOptionsDictFromPredefined
import random
from . import colour
import os,binascii
import pandas as pd

class VtkExporter:
    def __init__(self, path='.'):

        #output directory path
        self.path = path

        # local meshes
        self.localmeshes = {}

        # list of elements
        self.elements = []

        #multi block dictionary
        self.mbdico = {}
        self.mbindexdico = {}

        # material options dict
        self.materialVisualisationOptions = makeVisualisationOptionsDictFromPredefined(colour.ColourMap().fromPredefined())

    def export_to_Paraview(self, reg, model=True, df_model=None, df_color=None):
        """

        Args:
            reg:
            model:
            df_model:
            df_color:

        Returns:

        """

        world_volume = reg.getWorldVolume()

        if df_color is not None and df_model is not None:

            df_gdml = reg.structureAnalysis(world_volume.name)
            df_color.set_index('TYPE', inplace=True)
            color_dico = self.fill_color_dico(df_gdml, df_model, df_color)
            self.add_logical_volume(world_volume, model, color_dico)

        else:
            self.add_logical_volume(world_volume, model)

    def fill_color_dico(self, df_gdml, df_model, df_color):

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

    def add_logical_volume(self,
                           lv,
                           model,
                           color_dico={'R': {}, 'G': {}, 'B': {}},
                           rotation=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                           translation=_np.array([0,0,0])
                           ):

        if model:
            self._add_logical_world_volume(lv, rotation, translation, color_dico)
        else:
            self.element_name = self.getElementName(lv.name)

            self.mbdico[self.element_name] = _vtk.vtkMultiBlockDataSet()
            self.mbdico[self.element_name].SetNumberOfBlocks(self.countVisibleDaughters(lv, self.element_name, 0))
            self.mbindexdico[self.element_name] = 0

            self._add_logical_volume_recursive(lv, rotation, translation, color_dico)

        for element in self.mbdico.keys():

            self.elements.append(element)

            writer = _vtk.vtkXMLMultiBlockDataWriter()
            writer.SetDataModeToAscii()
            writer.SetInputData(self.mbdico[element])
            print(f"Trying to write file {element}.vtm")
            writer.SetFileName(f"{self.path}/{element}.vtm")
            writer.Write()

    def _add_logical_world_volume(self, lv, rotation, translation, color_dico):

        for pv in lv.daughterVolumes:

            self.element_name = self.getElementName(pv.logicalVolume.name)

            if self.element_name not in self.mbdico.keys():

                self.mbdico[self.element_name] = _vtk.vtkMultiBlockDataSet()
                self.mbdico[self.element_name].SetNumberOfBlocks(self.countVisibleDaughters(lv, self.element_name, 0))
                self.mbindexdico[self.element_name] = 0


            solid_name = pv.logicalVolume.solid.name

            # pv.type always placement when comes from BDSIM export
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

            mesh = pv.logicalVolume.mesh.localmesh

            if self.materialVisualisationOptions:
                visOptions = self.getMaterialVisOptions(
                    pv.logicalVolume.material.name)
            else:
                visOptions = pv.visOptions

            if pv.logicalVolume.name in color_dico['R'].keys():
                visOptions.color[0] = color_dico['R'][pv.logicalVolume.name]
                visOptions.color[1] = color_dico['G'][pv.logicalVolume.name]
                visOptions.color[2] = color_dico['B'][pv.logicalVolume.name]

            self.addMesh(pv.logicalVolume.name, solid_name, mesh, new_mtra, new_tra, self.localmeshes,
                         visOptions=visOptions)

            self._add_logical_volume_recursive(pv.logicalVolume, new_mtra, new_tra, color_dico)

    def _add_logical_volume_recursive(self, lv, rotation, translation, color_dico):

        for pv in lv.daughterVolumes:

            solid_name = pv.logicalVolume.solid.name

            # pv.type always placement when comes from BDSIM export
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

            mesh = pv.logicalVolume.mesh.localmesh

            if self.materialVisualisationOptions:
                visOptions = self.getMaterialVisOptions(
                    pv.logicalVolume.material.name)
            else:
                visOptions = pv.visOptions

            if pv.logicalVolume.name in color_dico['R'].keys():
                visOptions.color[0] = color_dico['R'][pv.logicalVolume.name]
                visOptions.color[1] = color_dico['G'][pv.logicalVolume.name]
                visOptions.color[2] = color_dico['B'][pv.logicalVolume.name]

            self.addMesh(pv.logicalVolume.name, solid_name, mesh, new_mtra, new_tra, self.localmeshes,
                         visOptions=visOptions)

            self._add_logical_volume_recursive(pv.logicalVolume, new_mtra, new_tra, color_dico)

    def addMesh(self, pv_name, solid_name, mesh, mtra, tra, localmeshes, visOptions = None):

        if solid_name in localmeshes:
            vtkPD = localmeshes[solid_name]
        else:
            vtkPD = _Convert.pycsgMeshToVtkPolyData(mesh)
            localmeshes[solid_name] = vtkPD

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
                Colors.InsertNextTuple3(visOptions.color[0]*255, visOptions.color[1]*255, visOptions.color[2]*255);

            vtkPD.GetCellData().SetScalars(Colors)
            vtkPD.Modified()

            if visOptions.visible:
                transformPD.SetInputData(vtkPD)
                transformPD.Update()

                self.mbdico[self.element_name].SetBlock(self.mbindexdico[self.element_name], transformPD.GetOutput())
                self.mbindexdico[self.element_name] += 1

    def getMaterialVisOptions(self, name):

        if name.find("0x") != -1 :
            nameStrip = name[0:name.find("0x")]
        else :
            nameStrip = name

        if nameStrip in self.materialVisualisationOptions.keys():
            return self.materialVisualisationOptions[nameStrip]
        else:
            print(f"Attention, missing {nameStrip} in materialVisualisationOptions, replace by default color")
            return self.materialVisualisationOptions['G4_C']

    def getElementName(self, logicalVolumeName):

        if "PREPENDworld_" in logicalVolumeName:
            return logicalVolumeName.split('PREPENDworld_')[1].split('0x')[0].split('_lv')[0]
        if "PREPEND_" in logicalVolumeName:
            return logicalVolumeName.split('PREPEND_')[1].split('0x')[0].split('_lv')[0]
        else:
            return logicalVolumeName.split('_container')[0].split('_e1')[0].split('_e2')[0].split('_even')[0].split('_outer')[0].split('_centre')[0].split('_collimator')[0].split('_beampipe')[0].split('0x')[0].split('_lv')[0].split('_bp')[0]

    def countVisibleDaughters(self, lv, element_name, n):

        for pv in lv.daughterVolumes:
            lv_name = self.getElementName(pv.logicalVolume.name)
            if lv_name == element_name:
                if self.getMaterialVisOptions(pv.logicalVolume.material.name).visible:
                    n += 1
                else:
                    n = self.countVisibleDaughters(pv.logicalVolume, element_name, n)
        return n


