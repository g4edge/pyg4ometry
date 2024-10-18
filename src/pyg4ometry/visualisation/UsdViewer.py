from .ViewerHierarchyBase import ViewerHierarchyBase as _ViewerHierarchyBase

from pathlib import Path
from pxr import Usd, Gf, UsdGeom

import numpy as _np


class UsdViewer(_ViewerHierarchyBase):

    def __init__(self, filePath="./test.usd"):
        print(Usd.GetVersion())
        layer_path = str(filePath)
        print(f"USD Stage file path: {layer_path}")
        self.stage = Usd.Stage.CreateNew(layer_path)

        self.lvDict = {}

    def traverseHierarchy(self, LV=None, motherPrim=None):
        if not LV:
            LV = self.worldLV

        print(LV.name)

        if not motherPrim:
            primName = "/" + LV.name
            meshPrim = self.stage.DefinePrim(primName, "Mesh")

        else:
            primName = LV.name
            meshPrim = self.stage.DefinePrim(motherPrim.GetPath().AppendPath(primName), "Mesh")

        # add data to mesh
        m = LV.mesh.localmesh.toVerticesAndPolygons()
        meshPrim.GetAttribute("points").Set(m[0])
        meshPrim.GetAttribute("faceVertexCounts").Set([len(vl) for vl in m[1]])
        a = _np.array(m[1])
        a.reshape(a.shape[0] * a.shape[1])
        meshPrim.GetAttribute("faceVertexIndices").Set(a)

        for daughter in LV.daughterVolumes:
            daughterPrim = self.traverseHierarchy(daughter.logicalVolume, motherPrim=meshPrim)

            # daughter pos
            pos = daughter.position.eval()
            # daughter rot
            rot = daughter.rotation.eval()

            print(pos, rot)
            # Transformation
            xform = UsdGeom.Xformable(daughterPrim)
            # Translation
            xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
            # Rotate
            xform.AddRotateXYZOp().Set(Gf.Vec3d(*rot))

        return meshPrim

    def save(self):
        self.stage.Save()
