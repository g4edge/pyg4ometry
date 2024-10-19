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

        self.lvNameToPrimDict = {}

    def traverseHierarchy(self, volume=None, motherPrim=None):

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

            pointsInMeters = _np.array(m[0])
            pointsInMeters = pointsInMeters / 1000.0
            meshPrim.GetAttribute("points").Set(pointsInMeters)
            meshPrim.GetAttribute("faceVertexCounts").Set([len(vl) for vl in m[1]])
            inds = _np.array(m[1])
            inds.reshape(inds.shape[0] * inds.shape[1])
            meshPrim.GetAttribute("faceVertexIndices").Set(inds)

            # loop over all daughters
            for daughter in volume.daughterVolumes:

                # check if lv and we have already encountered, if so use
                # existing prim
                if daughter.logicalVolume.name in self.lvNameToPrimDict:
                    daughterPrim = self.lvNameToPrimDict[daughter.logicalVolume.name]
                    print("primToInstance> ", daughterPrim)
                    daughterPrim.SetInstanceable(True)

                    instancePrim = self.stage.DefinePrim(
                        str(prim.GetPath()) + "/" + daughter.name, "Xform"
                    )
                    instancePrim.GetReferences().AddReference("", daughterPrim.GetPath())

                    pos = _np.array(daughter.position.eval()) / 1000.0  # convert to metres from mm
                    # daughter rot
                    rot = -_np.array(daughter.rotation.eval()) * 180 / _np.pi  # convert to degrees

                    # Transformation
                    xform = UsdGeom.Xformable(instancePrim)
                    # Translation
                    xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
                    # Rotate
                    xform.AddRotateZYXOp().Set(Gf.Vec3d(*rot))

                else:
                    daughterPrim = self.traverseHierarchy(daughter, motherPrim=prim)

                    # daughter pos
                    if daughter.type == "placement":
                        pos = (
                            _np.array(daughter.position.eval()) / 1000.0
                        )  # convert to metres from mm
                        # daughter rot
                        rot = (
                            -_np.array(daughter.rotation.eval()) * 180 / _np.pi
                        )  # convert to degrees

                        # Transformation
                        xform = UsdGeom.Xformable(daughterPrim)
                        # Translation
                        xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
                        # Rotate
                        xform.AddRotateZYXOp().Set(Gf.Vec3d(*rot))

        elif type(volume) is _pyg4.geant4.PhysicalVolume:
            print("physical")
            self.traverseHierarchy(volume.logicalVolume, motherPrim=prim)
        else:
            print("other")

        # make dict of LV/PV to prims for instancing
        if type(volume) is _pyg4.geant4.LogicalVolume:
            self.lvNameToPrimDict[volume.name] = prim

        return prim

    def save(self):
        self.stage.Save()
