import pyg4ometry as _pyg4
from .ViewerHierarchyBase import ViewerHierarchyBase as _ViewerHierarchyBase

from pathlib import Path
from pxr import Usd, Gf, UsdGeom

import numpy as _np


def mesh2Prim(mesh, meshPrim, scale=1000):
    m = mesh.toVerticesAndPolygons()
    pointsInMeters = _np.array(m[0])
    pointsInMeters = pointsInMeters / scale
    meshPrim.GetAttribute("points").Set(pointsInMeters)
    meshPrim.GetAttribute("faceVertexCounts").Set([len(vl) for vl in m[1]])
    inds = _np.array(m[1])
    inds.reshape(inds.shape[0] * inds.shape[1])
    meshPrim.GetAttribute("faceVertexIndices").Set(inds)


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

        print("traverseHierarchy> volume name : ", volume.name, volume.type)

        # if volume is a logical/physical
        if not motherPrim:
            prim = self.stage.DefinePrim("/" + volume.name, "Xform")
        else:
            prim = self.stage.DefinePrim(motherPrim.GetPath().AppendPath(volume.name), "Xform")

        if type(volume) is _pyg4.geant4.LogicalVolume:

            print("traverseHierarchy> process logical volume")

            # add mesh prim
            meshPrim = self.stage.DefinePrim(
                prim.GetPath().AppendPath(volume.name + "_mesh"), "Mesh"
            )
            print("traverseHierarchy> volume mesh prim : ", meshPrim.GetPath())

            # fill mesh prim
            mesh2Prim(volume.mesh.localmesh, meshPrim)

            # loop over all daughters
            for daughter in volume.daughterVolumes:

                # check if lv and we have already encountered, if so use
                # existing prim
                if daughter.logicalVolume.name in self.lvNameToPrimDict:
                    daughterPrim = self.lvNameToPrimDict[daughter.logicalVolume.name]
                    print("traverseHierarchy> primToInstance : ", daughterPrim)
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
            print("traverseHierarchy> process physical volume ")
            self.traverseHierarchy(volume.logicalVolume, motherPrim=prim)
        elif type(volume) is _pyg4.geant4.DivisionVolume:
            print("traverseHierarchy> process division volume")
        elif type(volume) is _pyg4.geant4.ReplicaVolume:
            print("traverseHierarchy> process replica volume")
        elif type(volume) is _pyg4.geant4.ParametrisedVolume:
            print("traverseHierarchy> process parametrised volume")
        else:
            print("traverseHierarchy> other")

        # make dict of LV/PV to prims for instancing
        if type(volume) is _pyg4.geant4.LogicalVolume:
            self.lvNameToPrimDict[volume.name] = prim

        return prim

    def save(self):
        self.stage.Save()
