import pyg4ometry as _pyg4
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

        print("LV name", LV.name)

        if not motherPrim:
            primName = "/" + LV.name
            lvPrim = self.stage.DefinePrim(primName, "Xform")
        else:
            primName = LV.name
            lvPrim = self.stage.DefinePrim(motherPrim.GetPath().AppendPath(primName), "Xform")

        print("Xform Prim path", lvPrim.GetPath())

        # add mesh prim
        meshPrim = self.stage.DefinePrim(lvPrim.GetPath().AppendPath(LV.name + "_mesh"), "Mesh")
        print("Mesh Prim path", meshPrim.GetPath())

        m = LV.mesh.localmesh.toVerticesAndPolygons()
        meshPrim.GetAttribute("points").Set(m[0])
        meshPrim.GetAttribute("faceVertexCounts").Set([len(vl) for vl in m[1]])
        a = _np.array(m[1])
        a.reshape(a.shape[0] * a.shape[1])
        meshPrim.GetAttribute("faceVertexIndices").Set(a)

        for daughter in LV.daughterVolumes:
            daughterPrim = self.traverseHierarchy(daughter.logicalVolume, motherPrim=lvPrim)

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

        return lvPrim

    def traverseHierarchy2(self, volume=None, motherPrim=None):

        if not volume:
            volume = self.worldLV

        print("volume name>", volume.name, type(volume))

        # if volume is a logical/physical
        if not motherPrim:
            prim = self.stage.DefinePrim("/" + volume.name, "Xform")
        else:
            prim = self.stage.DefinePrim(motherPrim.GetPath().AppendPath(volume.name), "Xform")

        if type(volume) is _pyg4.geant4.LogicalVolume:

            print("logical")

            # add mesh prim
            meshPrim = self.stage.DefinePrim(
                prim.GetPath().AppendPath(volume.name + "_mesh"), "Mesh"
            )
            print("volume mesh>", meshPrim.GetPath())

            m = volume.mesh.localmesh.toVerticesAndPolygons()
            meshPrim.GetAttribute("points").Set(m[0])
            meshPrim.GetAttribute("faceVertexCounts").Set([len(vl) for vl in m[1]])
            a = _np.array(m[1])
            a.reshape(a.shape[0] * a.shape[1])
            meshPrim.GetAttribute("faceVertexIndices").Set(a)

            for daughter in volume.daughterVolumes:
                daughterPrim = self.traverseHierarchy2(daughter, motherPrim=prim)

                # daughter pos
                if daughter.type == "placement":
                    pos = _np.array(daughter.position.eval())
                    # daughter rot
                    rot = -_np.array(daughter.rotation.eval()) * 180 / _np.pi

                    # Transformation
                    xform = UsdGeom.Xformable(daughterPrim)
                    # Translation
                    xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
                    # Rotate
                    xform.AddRotateZYXOp().Set(Gf.Vec3d(*rot))

        elif type(volume) is _pyg4.geant4.PhysicalVolume:
            print("physical")
            self.traverseHierarchy2(volume.logicalVolume, motherPrim=prim)
        else:
            print("other")

        return prim

    def save(self):
        self.stage.Save()
