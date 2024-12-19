try:
    from pxr import Usd, Gf, UsdGeom, UsdShade, Sdf
except ImportError:
    Usd = None

from .ViewerHierarchyBase import ViewerHierarchyBase as _ViewerHierarchyBase
import numpy as _np
import os as _os
from .. import geant4 as _g4


def mesh2Prim(mesh, meshPrim, scale=1000):
    m = mesh.toVerticesAndPolygons()
    pointsInMeters = _np.array(m[0])
    pointsInMeters = pointsInMeters / scale
    meshPrim.GetAttribute("points").Set(pointsInMeters)
    meshPrim.GetAttribute("faceVertexCounts").Set([len(vl) for vl in m[1]])
    inds = _np.array(m[1])
    inds.reshape(inds.shape[0] * inds.shape[1])
    meshPrim.GetAttribute("faceVertexIndices").Set(inds)


def visOptions2MaterialPrim(stage, visOptions, materialPrim):

    # create shader
    shader = UsdShade.Shader.Define(stage, materialPrim.GetPath().AppendPath("PreviewShader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    print(visOptions.usdOptions.diffuseColor)
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(*visOptions.usdOptions.diffuseColor)
    )
    print(visOptions.usdOptions.emissiveColor)
    shader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(*visOptions.usdOptions.emissiveColor)
    )
    shader.CreateInput("useSpecularWorkflow", Sdf.ValueTypeNames.Int).Set(
        visOptions.usdOptions.useSpecularWorkflow
    )
    shader.CreateInput("specularColor", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(*visOptions.usdOptions.specularColor)
    )
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(visOptions.usdOptions.metallic)
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(visOptions.usdOptions.roughness)
    shader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(visOptions.usdOptions.clearcoat)
    shader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(
        visOptions.usdOptions.clearcoatRoughness
    )  #
    shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(visOptions.usdOptions.opacity)  #
    shader.CreateInput("opacityThreshold", Sdf.ValueTypeNames.Float).Set(
        visOptions.usdOptions.opacityThreshold
    )  #
    shader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(visOptions.usdOptions.ior)  #
    shader.CreateInput("normal", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(*visOptions.usdOptions.normal)
    )
    shader.CreateInput("displacement", Sdf.ValueTypeNames.Float).Set(
        visOptions.usdOptions.displacement
    )  #
    shader.CreateInput("occlusion", Sdf.ValueTypeNames.Float).Set(
        visOptions.usdOptions.occlusion
    )  #

    # connect shader to material
    materialPrim.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")


class UsdViewer(_ViewerHierarchyBase):

    def __init__(self, filePath="./test.usd"):
        if Usd is None:
            msg = "Failed to import open usd"
            raise RuntimeError(msg)

        self.filePath = filePath

        print(Usd.GetVersion())
        layer_path = str(filePath)
        print(f"USD Stage file path: {layer_path}")
        self.stage = Usd.Stage.CreateNew(layer_path)

        self.lvNameToPrimDict = {}
        self.lvNameToMaterialPrimDict = {}

        self.materialRootPath = "/Materials"

        self.scaleFactor = 0.9999

    def setUsdviewPath(self, usdViewPath):
        self.usdViewPath = usdViewPath

    def traverseHierarchy(self, volume=None, motherPrim=None, scale=1000.00):

        if not volume:
            volume = self.worldLV

        print("traverseHierarchy> volume name : ", volume.name, volume.type)

        # if volume is a logical/physical
        if not motherPrim:
            prim = self.stage.DefinePrim("/" + volume.name, "Xform")
        else:
            prim = self.stage.DefinePrim(motherPrim.GetPath().AppendPath(volume.name), "Xform")

        if type(volume) is _g4.LogicalVolume:

            print("traverseHierarchy> process logical volume")

            # add mesh prim
            meshPrim = self.stage.DefinePrim(
                prim.GetPath().AppendPath(volume.name + "_mesh"), "Mesh"
            )
            print("traverseHierarchy> volume mesh prim : ", meshPrim.GetPath())

            # fill mesh prim
            mesh2Prim(volume.mesh.localmesh, meshPrim, scale=scale)

            # material for logical
            materialPrim = UsdShade.Material.Define(
                self.stage, self.materialRootPath + "/" + volume.name + "_mat"
            )

            visOptions2MaterialPrim(self.stage, volume.visOptions, materialPrim)
            UsdShade.MaterialBindingAPI(meshPrim).Bind(materialPrim)

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
                    daughterPrim = self.traverseHierarchy(
                        daughter, motherPrim=prim, scale=scale * self.scaleFactor
                    )

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
        elif type(volume) is _g4.PhysicalVolume:
            print("traverseHierarchy> process physical volume ")
            self.traverseHierarchy(
                volume.logicalVolume, motherPrim=prim, scale=scale * self.scaleFactor
            )
        elif type(volume) is _g4.DivisionVolume:
            print("traverseHierarchy> process division volume")
            for i, m, t in zip(range(len(volume.meshes)), volume.meshes, volume.transforms):
                print(i, m, t)

                paramPrim = self.stage.DefinePrim(
                    prim.GetPath().AppendPath(volume.name + "_mesh" + str(i)), "Mesh"
                )
                mesh2Prim(m.localmesh, paramPrim, scale=scale * self.scaleFactor)

                pos = _np.array(t[1]) / 1000.0  # convert to metres from mm
                # daughter rot
                rot = _np.array(t[0]) * 180 / _np.pi  # convert to degrees

                # Transformation
                xform = UsdGeom.Xformable(paramPrim)
                # Translation
                xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
                # Rotate
                xform.AddRotateZYXOp().Set(Gf.Vec3d(*rot))
        elif type(volume) is _g4.ReplicaVolume:
            print("traverseHierarchy> process replica volume")
            for i, m, t in zip(range(len(volume.meshes)), volume.meshes, volume.transforms):
                print(i, m, t)

                paramPrim = self.stage.DefinePrim(
                    prim.GetPath().AppendPath(volume.name + "_mesh" + str(i)), "Mesh"
                )
                mesh2Prim(m.localmesh, paramPrim, scale=scale * self.scaleFactor)

                pos = _np.array(t[1]) / 1000.0  # convert to metres from mm
                # daughter rot
                rot = _np.array(t[0]) * 180 / _np.pi  # convert to degrees

                # Transformation
                xform = UsdGeom.Xformable(paramPrim)
                # Translation
                xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
                # Rotate
                xform.AddRotateZYXOp().Set(Gf.Vec3d(*rot))
        elif type(volume) is _g4.ParameterisedVolume:
            print("traverseHierarchy> process parametrised volume")
            for i, m, t in zip(range(len(volume.meshes)), volume.meshes, volume.transforms):
                print(i, m, t)

                paramPrim = self.stage.DefinePrim(
                    prim.GetPath().AppendPath(volume.name + "_mesh" + str(i)), "Mesh"
                )
                mesh2Prim(m.localmesh, paramPrim, scale=scale * self.scaleFactor)

                pos = _np.array(t[1].eval()) / 1000.0  # convert to metres from mm
                # daughter rot
                rot = _np.array(t[0].eval()) * 180 / _np.pi  # convert to degrees

                # Transformation
                xform = UsdGeom.Xformable(paramPrim)
                # Translation
                xform.AddTranslateOp().Set(Gf.Vec3d(*pos))
                # Rotate
                xform.AddRotateZYXOp().Set(Gf.Vec3d(*rot))

        else:
            print("traverseHierarchy> other")

        # make dict of LV/PV to prims for instancing
        if type(volume) is _g4.LogicalVolume:
            self.lvNameToPrimDict[volume.name] = prim

        return prim

    def save(self):
        self.stage.Save()

    def view(self):
        _os.system(self.usdViewPath + " " + self.filePath)
