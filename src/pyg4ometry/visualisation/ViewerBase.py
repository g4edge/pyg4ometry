import numpy as _np
import pyg4ometry.transformation as _transformation

class ViewerBase :
    def __init__(self):
        self.localmeshes        = {}
        self.localmeshesoverlap = {}
        self.instancePlacements = {}
        self.instanceVisOptions = {}
        self.instancePbrOptions = {}

    def addLogicalVolume(self, lv,
                         mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]]),
                         tra  = _np.array([0,0,0])):

        if lv.type == "logical" :
            self.addMesh(lv.name, lv.mesh)
            self.addInstance(lv.name, mtra, tra)
        elif lv.type == "assembly" :
            pass
        else :
            print("Unknown logical volume type")

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

                self.addLogicalVolume(pv.logicalVolume, mtra_new, tra_new)
                self.addVisOptions(pv.logicalVolume.name, pv.visOptions)

    def addMesh(self, lvname, mesh):
        if lvname in self.instancePlacements :
            pass
        else :
            self.localmeshes[lvname] = mesh

    def addInstance(self, lvname, transformation, translation):
        if lvname in self.instancePlacements:
            self.instancePlacements[lvname].append({"transformation":transformation,
                                                    "translation":translation})
        else :
            self.instancePlacements[lvname] = [{"transformation":transformation,
                                                "translation":translation}]

    def addVisOptions(self, lvname, visOptions):
        if lvname in self.instanceVisOptions:
            self.instanceVisOptions[lvname].append(visOptions)
        else :
            self.instanceVisOptions[lvname] = [visOptions]

    def addPbrOptions(self, lvname, pbrOptions):
        pass

    def __repr__(self):
        pass




