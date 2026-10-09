try:
    from pxr import Usd, Gf, UsdGeom, UsdShade, UsdUtils, Sdf
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
    meshPrim.GetAttribute("faceVertexIndices").Set(_np.array(m[1]))
    # a solid is a polyhedron, not the control cage of a smooth surface. USD subdivides a mesh
    # by default, which rounds off every edge and shrinks the volume.
    meshPrim.GetAttribute("subdivisionScheme").Set("none")


def visOptions2MaterialPrim(stage, visOptions, materialPrim):

    # create shader
    shader = UsdShade.Shader.Define(stage, materialPrim.GetPath().AppendPath("PreviewShader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
        Gf.Vec3f(*visOptions.usdOptions.diffuseColor)
    )
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
    def __init__(self, filePath="./test.usd", mergeByMaterial=False):
        """Write the geometry to *filePath*.

        A ".usdz" suffix writes a usdz package, the single file format viewers on phones and
        tablets expect. Any other suffix writes a plain USD layer.

        With *mergeByMaterial* the volumes are combined into one mesh per material when the
        file is saved, in place of the hierarchy of one mesh per volume. A geometry of a few
        thousand volumes then becomes a handful of meshes holding the same triangles. Viewers
        on phones and tablets need this: they compile a shader for every material they are
        given and stall, or give up, on a geometry written volume by volume. The hierarchy,
        the volume names and the placements are lost, so merge only for viewing.
        """
        super().__init__()
        if Usd is None:
            msg = "Failed to import open usd"
            raise RuntimeError(msg)

        self.filePath = str(filePath)
        # usdz is a zip of USD layers, so write a layer first and package it in save()
        self.layerPath = (
            _os.path.splitext(self.filePath)[0] + ".usdc"
            if self.filePath.endswith(".usdz")
            else self.filePath
        )
        self.stage = Usd.Stage.CreateNew(self.layerPath)
        # lengths are in mm and mesh2Prim divides by 1000, so the file is in metres. Without
        # this USD assumes its default of cm and the geometry loads 100 times too small.
        UsdGeom.SetStageMetersPerUnit(self.stage, 1)
        # Geant4 geometries are z up, USD assumes y
        UsdGeom.SetStageUpAxis(self.stage, UsdGeom.Tokens.z)

        self.mergeByMaterial = mergeByMaterial

        self.lvNameToPrimDict = {}
        self.lvNameToMaterialPrimDict = {}

        # moved below the root prim once traversal starts, so the stage has a single root
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
            # viewers place the default prim, and usdz requires exactly one root, so keep the
            # materials below it rather than beside it
            self.stage.SetDefaultPrim(prim)
            self.materialRootPath = str(prim.GetPath()) + "/Materials"
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

            vo = self.getVisOptionsLV(volume)
            visOptions2MaterialPrim(self.stage, vo, materialPrim)
            UsdShade.MaterialBindingAPI.Apply(meshPrim).Bind(materialPrim)

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

    def mergeMeshesByMaterial(self):
        """Replace the mesh of every volume with one merged mesh per material.

        Reads the meshes back from the stage, so every placement is already resolved and the
        merged points are in world coordinates. Volumes share a mesh when their shaders carry
        the same values: a material is defined per volume here, so grouping by name would
        merge nothing.
        """
        root = self.stage.GetDefaultPrim()
        cache = UsdGeom.XformCache()
        merged = {}
        for prim in self.stage.Traverse(Usd.TraverseInstanceProxies()):
            if not prim.IsA(UsdGeom.Mesh):
                continue
            mesh = UsdGeom.Mesh(prim)
            material = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
            points = _np.array(mesh.GetPointsAttr().Get())
            if points.size == 0:
                continue
            # USD transforms a point as a row vector, hence the order here
            xform = _np.array(cache.GetLocalToWorldTransform(prim))
            points = points @ xform[:3, :3] + xform[3, :3]
            counts = list(mesh.GetFaceVertexCountsAttr().Get())
            indices = _np.array(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1)

            # replicas, divisions and parameterised volumes are written without a material,
            # so they merge together and stay unbound rather than being dropped
            key = None
            if material:
                shader = UsdShade.Shader(material.GetPrim().GetChild("PreviewShader"))
                key = tuple(
                    (i.GetBaseName(), str(i.Get()))
                    for i in sorted(shader.GetInputs(), key=lambda i: i.GetBaseName())
                )
            if key not in merged:
                merged[key] = [material, [], [], [], 0]
            group = merged[key]
            group[1].append(points)
            group[2] += counts
            group[3].append(indices + group[4])
            group[4] += len(points)

        for child in root.GetChildren():
            if str(child.GetPath()) != self.materialRootPath:
                self.stage.RemovePrim(child.GetPath())

        for i, (material, points, counts, indices, _) in enumerate(merged.values()):
            mesh = UsdGeom.Mesh.Define(
                self.stage, root.GetPath().AppendPath(f"merged_mesh_{i:03d}")
            )
            mesh.CreatePointsAttr(_np.concatenate(points))
            mesh.CreateFaceVertexCountsAttr(counts)
            mesh.CreateFaceVertexIndicesAttr(_np.concatenate(indices))
            mesh.CreateSubdivisionSchemeAttr("none")
            if material:
                UsdShade.MaterialBindingAPI(mesh).Apply(mesh.GetPrim())
                UsdShade.MaterialBindingAPI(mesh).Bind(material)

    def save(self):
        if self.mergeByMaterial:
            self.mergeMeshesByMaterial()
        self.stage.Save()
        if self.filePath.endswith(".usdz"):
            UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(self.layerPath), self.filePath)
            _os.remove(self.layerPath)

    def view(self):
        _os.system(self.usdViewPath + " " + self.filePath)
