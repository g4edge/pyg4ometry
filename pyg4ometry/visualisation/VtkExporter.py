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
    def __init__(self, path='.'):

        #output directory path
        self.path = path

        # local meshes
        self.localmeshes = {}

        # material options dict
        self.materialVisualisationOptions = makeVisualisationOptionsDictFromPredefined(colour.ColourMap().fromPredefined())

    def add_logical_volume(self,
                           lv,
                           color_dico={'R': {}, 'G': {}, 'B': {}},
                           rotation=_np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                           translation=_np.array([0,0,0])
                           ):

        self._add_logical_volume_recursive(lv, rotation, translation, color_dico)

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

            self.addMesh(pv.name, solid_name, mesh, new_mtra, new_tra, self.localmeshes,
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

                writer = _vtk.vtkXMLPolyDataWriter()
                writer.SetDataModeToAscii()
                writer.SetInputData(transformPD.GetOutput())
                print(f"Trying to write file {self.path}/{pv_name}.vtp")
                writer.SetFileName(f"{self.path}/{pv_name}.vtp")
                writer.Write()

    def getMaterialVisOptions(self, name):
        if name.find("0x") != -1 :
            nameStrip = name[0:name.find("0x")]
        else :
            nameStrip = name
        return self.materialVisualisationOptions[nameStrip]
