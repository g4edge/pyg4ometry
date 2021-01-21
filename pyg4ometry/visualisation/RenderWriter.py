import os as _os
import shutil as _shutil
import numpy as _np
import pyg4ometry.transformation as _transformation
from . import Convert as _convert

class RenderWriter :
    def __init__(self):
        self.materials = {}
        self.meshes    = {}
        self.instances = {}

    def addLogicalVolumeRecursive(self,
                                  logical,
                                  mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                                  tra = _np.array([0,0,0])):

        if logical.type != "assembly" :
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
        if logical.name in self.materials:
            pass
        else :
            self.materials[logical.name] = logical.material
            self.meshes[logical.name] = logical.mesh.localmesh

    def addInstance(self, logical, transformation, translation):
        if logical.name in self.instances:
            self.instances[logical.name].append({"transformation":transformation,
                                                 "translation":translation})
        else :
            self.instances[logical.name] = [{"transformation":transformation,
                                             "translation":translation}]

    def write(self, outputDirectory):

        # make output directory
        #_shutil.rmtree(outputDirectory, ignore_errors = True)
        _os.mkdir(outputDirectory)

        # loop over meshes and write obj files
        for mk in self.meshes :
            _convert.pycsgMeshToObj(self.meshes[mk],outputDirectory+"/"+mk)

        # loop of instances and write ascii file
        f = open(outputDirectory+"/"+"0_instances.dat","w")
        for ik in self.instances:
            for instance in self.instances[ik] :
                instanceName     = ik
                instanceMaterial = str(self.materials[ik])
                # instanceTransformation = str(instance["transformation"]).replace("\n","").replace("[","").replace("]","")
                instanceTransformation = str(_transformation.matrix2tbxyz(instance["transformation"])).replace("\n", "").replace("[", "").replace("]","")
                instancePosition      = str(instance["translation"]).replace("\n","").replace("[","").replace("]","")

                f.write(instanceName+" "+instanceMaterial+" "+instanceTransformation+" "+instancePosition+"\n")
        f.close()
