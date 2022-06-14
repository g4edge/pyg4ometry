import numpy as _np
import random as _random
import pyg4ometry.transformation as _transformation
from pyg4ometry.visualisation.VisualisationOptions import VisualisationOptions as _VisOptions
from pyg4ometry.visualisation.Mesh import Mesh as _Mesh


def _daughterSubtractedMesh(lv) :
    mm = lv.mesh.localmesh.clone() # mother mesh

    for d in lv.daughterVolumes :
        # skip over assemblies
        if d.logicalVolume.type == "assembly" :
            continue

        dp = d.position.eval()
        dr = d.rotation.eval()
        if d.scale is not None :
            ds = d.scale.eval()
        else :
            ds = [1,1,1]
        dm = d.logicalVolume.mesh.localmesh.clone()

        print(dp,dr)

        daa = _transformation.tbxyz2axisangle(dr)
        dm.rotate(daa[0], _transformation.rad2deg(daa[1]))
        dm.translate(dp)

        mm = mm.subtract(dm)


    return mm

class ViewerBase :
    '''
    Base class for all viewers and exporters. Handles unique meshes and their instances
    '''

    def __init__(self):
        # basic instancing structure
        self.localmeshes        = {} # unique meshes in scene
        self.localmeshesoverlap = {} # unique overlap meshes in scene
        self.instancePlacements = {} # instance placements
        self.instanceVisOptions = {} # instance vis options
        self.instancePbrOptions = {} # instqnce pbr options

        # subtract daughters of lv mesh
        self.bSubtractDaughters = False

        # material options dict
        self.materialVisOptions = {}
        self.materialPbrOptions = {}

    def setSubtractDaughters(self, subtractDaughters = True):
        self.bSubtractDaughters = subtractDaughters

    def addLogicalVolume(self, lv,
                         mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                         tra  = _np.array([0,0,0]),
                         visOptions = _VisOptions(representation="wireframe"),
                         depth=0):
        '''
        Add a logical volume to viewer (recursively)

        :param mtra: Transformation matrix for logical volume
        :type mtra: matrix(3,3)
        :param tra: Displacement for logical volume
        :type tra: array(3)
        '''

        if lv.type == "logical" and lv.mesh is not None:
            if not self.bSubtractDaughters :
                self.addMesh(lv.name, lv.mesh.localmesh)
            else :
                self.addMesh(lv.name, _daughterSubtractedMesh(lv))

            self.addInstance(lv.name, mtra, tra)

            materialName = lv.material.name
            materialName = materialName[0:materialName.find("0x")]

            if materialName in self.materialVisOptions :
                visOptions = self.materialVisOptions[materialName]
                visOptions.depth = depth
                self.addVisOptions(lv.name, visOptions)
            else :
                visOptions.depth = depth
                self.addVisOptions(lv.name, visOptions)
        elif lv.type == "assembly" :
            pass

        else :
            print("Unknown logical volume type or null mesh")

        for pv in lv.daughterVolumes :
            if pv.type == "placement":
                # pv transform
                pvmrot = _np.linalg.inv(_transformation.tbxyz2matrix(pv.rotation.eval()))
                if pv.scale:
                    pvmsca = _np.diag(pv.scale.eval())
                else:
                    pvmsca = _np.diag([1, 1, 1])

                pvtra = _np.array(pv.position.eval())

                # pv compound transform
                mtra_new = mtra * pvmsca * pvmrot
                tra_new  = (_np.array(mtra.dot(pvtra)) + tra)[0]

                #pv.visOptions.alpha = 1.0
                #pv.visOptions.colour = [_random.random(), _random.random(), _random.random()]
                self.addLogicalVolume(pv.logicalVolume, mtra_new, tra_new, pv.visOptions, depth+1)

    def addMesh(self, name, mesh):

        '''
        Add a single mesh

        :param name: Name of mesh (e.g logical volume name)
        :type name: str
        :param mesh: Mesh to be added
        :type mesh: CSG
        '''

        if name in self.instancePlacements :
            pass
        else :
            self.localmeshes[name] = mesh

    def addInstance(self, name, transformation, translation):
        '''
        Add a new instance for mesh with name

        :param name: name of mesh to add instance
        :type name: str
        :param transformation: Transformation matrix for instance
        :type transformation: matrix(3,3)
        :param translation: Translation for instance
        :type translation: array(3)

        '''


        if name in self.instancePlacements:
            self.instancePlacements[name].append({"transformation":transformation,
                                                    "translation":translation})
        else :
            self.instancePlacements[name] = [{"transformation":transformation,
                                                "translation":translation}]

    def addVisOptions(self, name, visOptions):
        '''
        Add vis options to mesh with name

        :param name: name of mesh
        :type name: str
        :param visOptions:
        :type visOptions: VisualisationOptions

        '''
        if name in self.instanceVisOptions:
            self.instanceVisOptions[name].append(visOptions)
        else :
            self.instanceVisOptions[name] = [visOptions]

    def addPbrOptions(self, name, pbrOptions):
        '''
        Add pbr options to mesh with name

        :param name: name of mesh
        :type name: str
        :param pbrOptions:
        :type pbrOptions: PbrOptions

        '''

        pass

    def addMaterialVisOption(self, materialName, visOptionInstance):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: material name to match
        :type materialName: str
        :param visOptionInstance: instance
        :type visOptionInstance: :class:`VisualisationOptions`
        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOptionInstance

    def addMaterialPbrOption(self, materialName, visOptionInstance):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: material name to match
        :type materialName: str
        :param visOptionInstance: instance
        :type visOptionInstance: :class:`VisualisationOptions`

        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOptionInstance

    def __repr__(self):
        pass




