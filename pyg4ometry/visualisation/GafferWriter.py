import numpy as _np
import pyg4ometry.transformation as _transformation

class GafferWriter :
    def __init__(self):
        self.materials = {}
        self.meshes    = {}
        self.instances = {}

    def addLogicalVolumeRecursive(self,
                                  logical,
                                  mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                                  tra = _np.array([0,0,0])):

        self.addMesh(logical)
        self.addInstance(logical, mtra, tra)

        for pv in logical.daughterVolumes :
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
                tra_new = (_np.array(mtra.dot(pvtra)) + tra)[0]

                self.addLogicalVolumeRecursive(pv.logicalVolume, mtra_new, tra_new)

    def addMesh(self, logical):
        if self.materials.has_key(logical.name) :
            pass
        else :
            self.materials[logical.name] = logical.material
            self.meshes[logical.name] = logical.mesh.localmesh

    def addInstance(self, logical, transformation, translation):
        if self.instances.has_key(logical.name) :
            self.instances[logical.name].append({"transformation":transformation,
                                                 "translation":translation})
        else :
            self.instances[logical.name] = [{"transformation":transformation,
                                             "translation":translation}]

    def write(self, outputDirectory):
        # make output directory

        # loop over meshes and write obj files

        # loop of instances and write JSON file

