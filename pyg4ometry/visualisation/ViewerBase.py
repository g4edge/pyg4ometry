import numpy as _np
import pyg4ometry.transformation as _transformation
from pyg4ometry.visualisation.VisualisationOptions import VisualisationOptions as _VisOptions

class ViewerBase :
    '''
    Base class for all viewers and exporters. Handles unique meshes and their instances
    '''

    def __init__(self):
        self.localmeshes        = {} # unique meshes in scene
        self.localmeshesoverlap = {} # unique overlap meshes in scene
        self.instancePlacements = {} # instance placements
        self.instanceVisOptions = {} # instance vis options
        self.instancePbrOptions = {} # instqnce pbr options

    def addLogicalVolume(self, lv,
                         mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                         tra  = _np.array([0,0,0]),
                         visOptions = _VisOptions(representation="wireframe")):
        '''
        Add a logical volume to viewer (recursively)

        :param mtra: Transformation matrix for logical volume
        :type mtra: matrix(3,3)
        :param tra: Displacement for logical volume
        :type tra: array(3)
        '''

        if lv.type == "logical" and lv.mesh is not None:
            self.addMesh(lv.name, lv.mesh)
            self.addInstance(lv.name, mtra, tra)
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

                pv.visOptions.alpha = 0.1
                self.addLogicalVolume(pv.logicalVolume, mtra_new, tra_new, pv.visOptions)

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
            self.localmeshes[name] = mesh.localmesh

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

    def __repr__(self):
        pass




