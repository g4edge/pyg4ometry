import numpy as _np
import random as _random
import pyg4ometry.transformation as _transformation
from pyg4ometry.visualisation.VisualisationOptions import VisualisationOptions as _VisOptions
from   pyg4ometry.visualisation  import OverlapType as _OverlapType

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
        # init/clear structures
        ViewerBase.clear(self)

        # subtract daughters of lv mesh
        self.bSubtractDaughters = False

        # default vis options
        self.defaultVisOptions = None
        self.defaultOverlapVisOptions = None
        self.defaultCoplanarVisOptions = None
        self.defaultProtusionVisOptions = None

        # default pbr options

        # material options dict
        self.materialVisOptions = {} # dictionary for material vis options
        self.materialPbrOptions = {} # dictionary for material pbr options

    def clear(self):
        # basic instancing structure
        self.localmeshes        = {} # unique meshes in scene
        self.localmeshesoverlap = {} # unique overlap meshes in scene
        self.instancePlacements = {} # instance placements
        self.instanceVisOptions = {} # instance vis options
        self.instancePbrOptions = {} # instance pbr options

    def setSubtractDaughters(self, subtractDaughters = True):
        self.bSubtractDaughters = subtractDaughters

    def addLogicalVolume(self, lv,
                         mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                         tra  = _np.array([0,0,0]),
                         visOptions = _VisOptions(representation="wireframe"),
                         depth=0,
                         name = None):
        '''
        Add a logical volume to viewer (recursively)

        :param mtra: Transformation matrix for logical volume
        :type mtra: matrix(3,3)
        :param tra: Displacement for logical volume
        :type tra: array(3)
        :param visOptions: VisualisationOptions for the lv mesh
        :type visOptions: VisualisationOptions
        '''

        if lv.type == "logical" and lv.mesh is not None:

            # add mesh
            if not self.bSubtractDaughters :
                self.addMesh(lv.name, lv.mesh.localmesh)
            else :
                self.addMesh(lv.name, _daughterSubtractedMesh(lv))

            # add instance
            if name is None :
                name = "world"
            self.addInstance(lv.name, mtra, tra, name)

            materialName = lv.material.name
            materialName = materialName[0:materialName.find("0x")]

            # add vis options
            if materialName in self.materialVisOptions :
                visOptions = self.materialVisOptions[materialName]
                visOptions.depth = depth
                self.addVisOptions(lv.name, visOptions)
            else :
                visOptions.depth = depth
                self.addVisOptions(lv.name, visOptions)

            # add overlap meshes
            for [overlapmesh, overlaptype], i in zip(lv.mesh.overlapmeshes,
                                                     range(0, len(lv.mesh.overlapmeshes))):
                visOptions = self.getOverlapVisOptions(overlaptype)
                visOptions.depth = depth+10

                overlapName = lv.name+"_overlap_"+str(i)
                self.addMesh(overlapName, overlapmesh)
                self.addInstance(overlapName,  mtra, tra)
                self.addVisOptions(overlapName, visOptions)

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

                #pv.visOptions.colour = [_random.random(), _random.random(), _random.random()]
                self.addLogicalVolume(pv.logicalVolume, mtra_new, tra_new, pv.visOptions, depth+1, pv.name)
            elif pv.type == "replica" or pv.type == "division":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0])
                    pvtra = _np.array(trans[1])

                    # pv compound transform
                    new_mtra = mtra * pvmrot
                    new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                    self.addMesh(pv.name,mesh.localmesh)
                    self.addInstance(pv.name,new_mtra,new_tra, pv.name)
                    self.addVisOptions(pv.name,pv.visOptions)
            elif pv.type == "parametrised":
                for mesh, trans, i  in zip(pv.meshes, pv.transforms, range(0,len(pv.meshes),1)):

                    pv_name = pv.name+"_param_"+str(i)

                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0].eval())
                    pvtra = _np.array(trans[1].eval())

                    # pv compound transform
                    new_mtra = mtra * pvmrot
                    new_tra = (_np.array(mtra.dot(pvtra)) + tra)[0]

                    self.addMesh(pv_name,mesh.localmesh)
                    self.addInstance(pv_name,new_mtra,new_tra,pv_name)
                    self.addVisOptions(pv_name,pv.visOptions)

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

    def addInstance(self, name, transformation, translation, instanceName = ""):
        '''
        Add a new instance for mesh with name

        :param name: name of mesh to add instance
        :type name: str
        :param transformation: Transformation matrix for instance
        :type transformation: matrix(3,3)
        :param translation: Translation for instance
        :type translation: array(3)
        :param instanceName: Name of the instance e.g PV
        :type instanceName: str

        '''

        if name in self.instancePlacements:
            self.instancePlacements[name].append({"transformation":transformation,
                                                  "translation":translation,
                                                  "name":instanceName})
        else :
            self.instancePlacements[name] = [{"transformation":transformation,
                                              "translation":translation,
                                              "name":instanceName}]

    def addVisOptions(self, name, visOption):
        '''
        Add vis options to mesh with name

        :param name: name of mesh
        :type name: str
        :param visOptions:
        :type visOptions: VisualisationOptions

        '''
        if name in self.instanceVisOptions:
            self.instanceVisOptions[name].append(visOption)
        else :
            self.instanceVisOptions[name] = [visOption]

    def addPbrOptions(self, name, pbrOption):
        '''
        Add pbr options to mesh with name

        :param name: name of mesh
        :type name: str
        :param pbrOptions:
        :type pbrOptions: PbrOptions

        '''

        pass

    def addMaterialVisOption(self, materialName, visOption):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: material name to match
        :type materialName: str
        :param visOption: instance
        :type visOption: :class:`VisualisationOptions`
        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOption

    def addMaterialPbrOption(self, materialName, visOption):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: material name to match
        :type materialName: str
        :param visOption: instance
        :type visOption: :class:`VisualisationOptions`

        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOption

    def setDefaultVisOptions(self, visOption):
        self.defaultVisOptions = visOption

    def getDefaultVisOptions(self):
        return self.defaultVisOptions

    def getMaterialVisOptions(self, material):
        pass

    def setOverlapVisOption(self, visOption):
        self.defaultOverlapVisOptions = visOption

    def setCoplanarVisOption(self, visOption):
        self.defaultCoplanarVisOptions = visOption

    def setProtusionVisOption(self, visOption):
        self.defaultProtusionVisOptions = visOption

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

    def __repr__(self):
        pass




