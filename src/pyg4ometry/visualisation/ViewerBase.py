import base64 as _base64
import copy as _copy
import numpy as _np
import random as _random
import logging as _log
from .. import pycgal as _pycgal
from .. import transformation as _transformation
from .VisualisationOptions import (
    VisualisationOptions as _VisOptions,
)
from .Mesh import OverlapType as _OverlapType

_log = _log.getLogger(__name__)


def _daughterSubtractedMesh(lv):
    mm = lv.mesh.localmesh.clone()  # mother mesh

    for d in lv.daughterVolumes:
        # skip over assemblies
        if d.logicalVolume.type == "assembly":
            continue

        dp = d.position.eval()
        dr = d.rotation.eval()
        if d.scale is not None:
            ds = d.scale.eval()
        else:
            ds = [1, 1, 1]
        dm = d.logicalVolume.mesh.localmesh.clone()

        daa = _transformation.tbxyz2axisangle(dr)
        dm.rotate(daa[0], _transformation.rad2deg(daa[1]))
        dm.translate(dp)

        mm = mm.subtract(dm)

    return mm


class ViewerBase:
    """
    Base class for all viewers and exporters. Handles unique meshes and their instances
    """

    def __init__(self):
        # init/clear structures
        ViewerBase.clear(self)

        # subtract daughters of lv mesh
        self.bSubtractDaughters = False

        # default vis options
        self.defaultVisOptions = _VisOptions()
        self.defaultOverlapVisOptions = None
        self.defaultCoplanarVisOptions = None
        self.defaultProtusionVisOptions = None

        # default pbr options

        # material options dict
        self.materialVisOptions = {}  # dictionary for material vis options
        self.materialPbrOptions = {}  # dictionary for material pbr options

    def clear(self):
        # basic instancing structure
        self.localmeshes = {}  # unique meshes in scene
        self.localmeshesoverlap = {}  # unique overlap meshes in scene
        self.instancePlacements = {}  # instance placements
        self.instanceVisOptions = {}  # instance vis options
        self.instancePbrOptions = {}  # instance pbr options

    def _getMaterialVis(self, materialName):
        materialVis = None
        # a dict evaluates to True if not empty
        if self.materialVisOptions:
            # if 0x is in name, strip the appended pointer (common in exported GDML)
            if "0x" in materialName:
                materialName = materialName[0 : materialName.find("0x")]
            # get with default
            materialVis = v = self.materialVisOptions.get(materialName, self.defaultVisOptions)
        return materialVis

    def getVisOptions(self, pv):
        """
        Return a set of vis options according to the precedence of pv, lv, material, default.
        """
        materialVis = None
        if pv.logicalVolume.type == "logical":
            materialVis = self._getMaterialVis(pv.logicalVolume.material.name)
        # take the first non-None set of visOptions
        orderOfPrecedence = [
            pv.visOptions,
            pv.logicalVolume.visOptions,
            materialVis,
            self.defaultVisOptions,
        ]
        return next(item for item in orderOfPrecedence if item is not None)

    def getVisOptionsLV(self, lv):
        """
        Return a set of vis options according to the precedence of pv, lv, material, default.
        """
        materialVis = self._getMaterialVis(lv.material.name)
        # take the first non-None set of visOptions
        orderOfPrecedence = [lv.visOptions, materialVis, self.defaultVisOptions]
        return next(item for item in orderOfPrecedence if item is not None)

    def setSubtractDaughters(self, subtractDaughters=True):
        self.bSubtractDaughters = subtractDaughters

    def addLogicalVolume(
        self,
        lv,
        mtra=_np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        tra=_np.array([0, 0, 0]),
        visOptions=_VisOptions(representation="wireframe"),
        depth=0,
        name=None,
    ):
        """
        Add a logical volume to viewer (recursively)

        :param mtra: Transformation matrix for logical volume
        :type mtra: matrix(3,3)
        :param tra: Displacement for logical volume
        :type tra: array(3)
        :param visOptions: VisualisationOptions for the lv mesh
        :type visOptions: VisualisationOptions
        """

        if lv.type == "logical" and lv.mesh is not None and lv.solid.type == "extruder":
            for extruName in lv.solid.g4_decomposed_extrusions:
                meshName = lv.name + "_" + extruName

                for extruDecom in lv.solid.g4_decomposed_extrusions[extruName]:
                    meshNameDecom = lv.name + "_" + extruName + "_" + extruDecom.name
                    self.addMesh(meshNameDecom, extruDecom.mesh())
                    self.addInstance(meshNameDecom, mtra, tra, name)
                    self.addVisOptions(meshNameDecom, visOptions)

        if lv.type == "logical" and lv.mesh is not None:
            # add mesh
            if not self.bSubtractDaughters:
                self.addMesh(lv.name, lv.mesh.localmesh)
            else:
                self.addMesh(lv.name, _daughterSubtractedMesh(lv))

            # add instance
            if name is None:
                name = "world"
            self.addInstance(lv.name, mtra, tra, name)

            vo = self.getVisOptionsLV(lv)
            self.addVisOptions(lv.name, vo)

            # add overlap meshes
            for [overlapmesh, overlaptype], i in zip(
                lv.mesh.overlapmeshes, range(len(lv.mesh.overlapmeshes))
            ):
                visOptions = self.getOverlapVisOptions(overlaptype)
                visOptions.depth = depth + 10

                overlapName = lv.name + "_overlap_" + str(i)
                self.addMesh(overlapName, overlapmesh)
                self.addInstance(overlapName, mtra, tra)
                self.addVisOptions(overlapName, visOptions)

        elif lv.type == "assembly":
            pass

        else:
            _log.warning("Unknown logical volume type or null mesh")

        for pv in lv.daughterVolumes:
            vo = self.getVisOptions(pv)
            if pv.type == "placement":
                # pv transform
                pvmrot = _np.linalg.inv(_transformation.tbxyz2matrix(pv.rotation.eval()))
                if pv.scale:
                    pvmsca = _np.diag(pv.scale.eval())
                else:
                    pvmsca = _np.diag([1, 1, 1])

                pvtra = _np.array(pv.position.eval())

                # pv compound transform
                mtra_new = mtra @ pvmrot @ pvmsca
                tra_new = mtra @ pvtra + tra

                self.addLogicalVolume(
                    pv.logicalVolume,
                    mtra_new,
                    tra_new,
                    vo,
                    depth + 1,
                    pv.name,
                )
            elif pv.type == "replica" or pv.type == "division":
                for mesh, trans in zip(pv.meshes, pv.transforms):
                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0])
                    pvtra = _np.array(trans[1])

                    # pv compound transform
                    new_mtra = mtra @ pvmrot
                    new_tra = mtra @ pvtra + tra

                    vo2 = _copy.deepcopy(vo)
                    vo2.depth += 1

                    self.addMesh(pv.name, mesh.localmesh)
                    self.addInstance(pv.name, new_mtra, new_tra, pv.name)
                    self.addVisOptions(pv.name, vo2)
            elif pv.type == "parametrised":
                for mesh, trans, i in zip(pv.meshes, pv.transforms, range(0, len(pv.meshes), 1)):
                    pv_name = pv.name + "_param_" + str(i)

                    # pv transform
                    pvmrot = _transformation.tbxyz2matrix(trans[0].eval())
                    pvtra = _np.array(trans[1].eval())

                    # pv compound transform
                    new_mtra = mtra @ pvmrot
                    new_tra = mtra @ pvtra + tra

                    vo2 = _copy.deepcopy(vo)
                    vo2.depth += 1

                    self.addMesh(pv_name, mesh.localmesh)
                    self.addInstance(pv_name, new_mtra, new_tra, pv_name)
                    self.addVisOptions(pv_name, vo2)

    def addFlukaRegions(self, fluka_registry, max_region=1000000):
        icount = 0
        for k in fluka_registry.regionDict:
            _log.debug("ViewerBase.addFlukaRegions> %s", k)
            m = fluka_registry.regionDict[k].mesh()

            if m is not None:
                self.addMesh(k, m)
                self.addInstance(
                    k,
                    _np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                    _np.array([0, 0, 0]),
                    k + "_instance",
                )
                self.addVisOptions(k, _VisOptions())

            icount += 1

            if icount > max_region:
                break

    def addMesh(self, name, mesh):
        """
        Add a single mesh

        :param name: Name of mesh (e.g logical volume name)
        :type name: str
        :param mesh: Mesh to be added
        :type mesh: CSG
        """

        if name in self.instancePlacements:
            pass
        else:
            self.localmeshes[name] = mesh

    def addInstance(self, name, transformation, translation, instanceName=""):
        """
        Add a new instance for mesh with name

        :param name: name of mesh to add instance
        :type name: str
        :param transformation: Transformation matrix for instance
        :type transformation: array(3,3)
        :param translation: Translation for instance
        :type translation: array(3)
        :param instanceName: Name of the instance e.g PV
        :type instanceName: str

        """

        if name in self.instancePlacements:
            self.instancePlacements[name].append(
                {
                    "transformation": transformation,
                    "translation": translation,
                    "name": instanceName,
                }
            )
        else:
            self.instancePlacements[name] = [
                {
                    "transformation": transformation,
                    "translation": translation,
                    "name": instanceName,
                }
            ]

    def addVisOptions(self, name, visOption):
        """
        Add vis options to mesh with name

        :param name: name of mesh
        :type name: str
        :param visOptions:
        :type visOptions: VisualisationOptions

        """
        if name in self.instanceVisOptions:
            self.instanceVisOptions[name].append(visOption)
        else:
            self.instanceVisOptions[name] = [visOption]

    def addPbrOptions(self, name, pbrOption):
        """
        Add pbr options to mesh with name

        :param name: name of mesh
        :type name: str
        :param pbrOptions:
        :type pbrOptions: PbrOptions

        """

    def addMaterialVisOption(self, materialName, visOption):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: material name to match
        :type materialName: str
        :param visOption: instance
        :type visOption: :class:`VisualisationOptions`
        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOption

    def addMaterialPbrOption(self, materialName, visOption):
        """
        Append a visualisation option instance to the dictionary of materials.

        :param materialName: material name to match
        :type materialName: str
        :param visOption: instance
        :type visOption: :class:`VisualisationOptions`

        """
        if self.materialVisOptions is None:
            self.materialVisOptions = {}

        self.materialVisOptions[materialName] = visOption

    def setDefaultVisOptions(self, visOption):
        self.defaultVisOptions = visOption

    def getDefaultVisOptions(self):
        return self.defaultVisOptions

    def getMaterialVisOptions(self, material):
        pass

    def setOverlapVisOption(self, visOption):
        self.defaultOverlapVisOptions = visOption

    def setCoplanarVisOption(self, visOption):
        self.defaultCoplanarVisOptions = visOption

    def setProtusionVisOption(self, visOption):
        self.defaultProtusionVisOptions = visOption

    def getOverlapVisOptions(self, overlaptype):
        visOptions = _VisOptions()
        if overlaptype == _OverlapType.protrusion:
            visOptions.colour = [1, 0, 0]
            visOptions.alpha = 1.0
        elif overlaptype == _OverlapType.overlap:
            visOptions.colour = [0, 1, 0]
            visOptions.alpha = 1.0
        elif overlaptype == _OverlapType.coplanar:
            visOptions.colour = [0, 0, 1]
            visOptions.alpha = 1.0

        return visOptions

    def removeInvisible(self):
        """Remove wireframe or transparent instances from self"""
        toRemove = []

        for k in self.localmeshes:
            pyg4VisOpt = self.instanceVisOptions[k][0]
            pyg4_rep = pyg4VisOpt.representation
            pyg4_alp = pyg4VisOpt.alpha

            if pyg4_rep == "wireframe" or pyg4_alp == 0:
                toRemove.append(k)

        for k in toRemove:
            self.localmeshes.pop(k)
            self.instancePlacements.pop(k)
            self.instanceVisOptions.pop(k)

    def scaleScene(self, scaleFactor):
        for k in self.localmeshes:
            self.localmeshes[k].scale([scaleFactor, scaleFactor, scaleFactor])

        for k in self.instancePlacements:
            for p in self.instancePlacements[k]:
                p["translation"] = p["translation"] * scaleFactor

    def exportGLTFScene(self, gltfFileName="test.gltf", singleInstance=False):
        """Export entire scene as gltf file, filename extension dictates binary (glb) or readable json (gltf)
        singleInstance is a Boolean flag to supress all but one instance"""

        try:
            from pygltflib import (
                GLTF2,
                Scene,
                Material,
                PbrMetallicRoughness,
                Buffer,
                BufferView,
                Accessor,
                Mesh,
                Attributes,
                Primitive,
                Node,
                ARRAY_BUFFER,
                ELEMENT_ARRAY_BUFFER,
                FLOAT,
                UNSIGNED_INT,
                SCALAR,
                VEC3,
            )
        except ImportError:
            _log.error("pygltflib needs to be installed for export : 'pip install pygltflib'")
            return

        materials = []
        buffers = []
        bufferViews = []
        accessors = []
        meshes = []
        nodes = []
        scenes = []

        # loop over meshes
        iBuffer = 0
        key_iBuffer = {}
        for k in self.localmeshes:
            key_iBuffer[k] = iBuffer

            # get mesh
            csg = self.localmeshes[k]

            scale = 1 - 0.001 * self.instanceVisOptions[k][0].depth
            csg.scale([scale, scale, scale])

            inf = csg.info()

            vAndPs = csg.toVerticesAndPolygons()
            verts = vAndPs[0]
            tris = vAndPs[1]

            verts = _np.array(verts).astype(_np.float32)
            tris = _np.array(tris).astype(_np.uint32)

            verts_binary_blob = verts.flatten().tobytes()
            tris_binary_blob = tris.flatten().tobytes()

            pyg4VisOpt = self.instanceVisOptions[k][0]

            pyg4_color = pyg4VisOpt.colour
            pyg4_alpha = pyg4VisOpt.alpha
            pyg4_rep = pyg4VisOpt.representation

            pbrMetallicRoughness = PbrMetallicRoughness(
                baseColorFactor=[
                    _random.random(),
                    _random.random(),
                    _random.random(),
                    1.0,
                ],
                metallicFactor=_random.random(),
                roughnessFactor=_random.random(),
            )
            # alphaMode = "OPAQUE"

            # if pyg4_rep == "wireframe" :
            #    alphaMode = "BLEND"
            #    alphaCutoff = pyg4_alpha

            materials.append(Material(pbrMetallicRoughness=pbrMetallicRoughness))

            buffers.append(
                Buffer(
                    uri="data:application/octet-stream;base64,"
                    + str(_base64.b64encode(tris_binary_blob + verts_binary_blob).decode("utf-8")),
                    byteLength=len(tris_binary_blob) + len(verts_binary_blob),
                )
            )

            bufferViews.append(
                BufferView(
                    buffer=iBuffer,
                    byteLength=len(tris_binary_blob),
                    target=ELEMENT_ARRAY_BUFFER,
                )
            )
            bufferViews.append(
                BufferView(
                    buffer=iBuffer,
                    byteOffset=len(tris_binary_blob),
                    byteLength=len(verts_binary_blob),
                    target=ARRAY_BUFFER,
                )
            )
            accessors.append(
                Accessor(
                    bufferView=2 * iBuffer,
                    componentType=UNSIGNED_INT,
                    count=tris.size,
                    type=SCALAR,
                    max=[int(tris.max())],
                    min=[int(tris.min())],
                )
            )
            accessors.append(
                Accessor(
                    bufferView=2 * iBuffer + 1,
                    componentType=FLOAT,
                    count=int(verts.size / 3),
                    type=VEC3,
                    max=verts.max(axis=0).tolist(),
                    min=verts.min(axis=0).tolist(),
                )
            )
            meshes.append(
                Mesh(
                    primitives=[
                        Primitive(
                            attributes=Attributes(POSITION=2 * iBuffer + 1),
                            indices=2 * iBuffer,
                            material=iBuffer,
                        )
                    ]
                )
            )

            iBuffer += 1

        # loop over instances
        iMesh = 0
        for k in self.instancePlacements:
            iInstance = 0
            for p in self.instancePlacements[k]:
                t = p["translation"]
                r = p["transformation"]
                aa = _transformation.matrix2axisangle(r)
                axis = aa[0]
                angle = aa[1]

                nodes.append(
                    Node(
                        name=k + "_" + str(iInstance),
                        mesh=iMesh,
                        translation=[float(t[0]), float(t[1]), float(t[2])],
                        rotation=[
                            axis[0] * _np.sin(angle / 2),
                            axis[1] * _np.sin(angle / 2),
                            axis[2] * _np.sin(angle / 2),
                            _np.cos(angle / 2),
                        ],
                    )
                )

                # Only make a single instance
                if singleInstance:
                    break

                iInstance += 1

            iMesh += 1

        scene = Scene(nodes=list(range(0, len(nodes), 1)))
        scenes.append(scene)

        gltf = GLTF2(
            scene=0,
            scenes=scenes,
            nodes=nodes,
            meshes=meshes,
            accessors=accessors,
            bufferViews=bufferViews,
            buffers=buffers,
            materials=materials,
        )

        if str(gltfFileName).find("gltf") != -1:
            gltf.save_json(gltfFileName)
        elif str(gltfFileName).find("glb") != -1:
            glb = b"".join(gltf.save_to_bytes())
            f = open(gltfFileName, "wb")
            f.write(glb)
            f.close()
        else:
            _log.error("ViewerBase::exportGLTFScene> unknown gltf extension")

    def exportGLTFAssets(self, gltfFileName="test.gltf"):
        """Export all the assets (meshes) without all the instances. The position of the asset is
        the position of the first instance"""

        self.exportGLTFScene(gltfFileName, singleInstance=True)

    def exportThreeJSScene(self, fileNameBase="test", lightBoxHDR="concrete_tunnel_02_4k.hdr"):
        """
        html based on https://threejs.org/examples/#webgl_loader_gltf
        HRDI https://polyhaven.com/a/concrete_tunnel_02

        npm install node
        wget https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/concrete_tunnel_02_4k.exr
        conver EXR to HDR e.g. https://convertio.co/exr-hdr/
        python -m http.server 8000
        open test.html
        """
        from importlib_resources import files

        from jinja2 import Template

        gltfFileName = fileNameBase + ".gltf"
        htmlFileName = fileNameBase + ".html"
        cssFileName = fileNameBase + ".css"

        self.exportGLTFScene(gltfFileName)

        data = {
            "model_gltf_file": gltfFileName,
            "scene_hdr": lightBoxHDR,
            "css_file": cssFileName,
        }

        threeHTMLTemplate = files(__name__).joinpath("threejs.html")
        threeCSSTemplate = files(__name__).joinpath("threejs.css")

        with open(threeHTMLTemplate) as file:
            template = Template(file.read())
            renderedTemplate = template.render(data)
            with open(htmlFileName, "w") as outfile:
                outfile.write(renderedTemplate)

        with open(threeCSSTemplate) as file:
            template = Template(file.read())
            renderedTemplate = template.render(data)
            with open(cssFileName, "w") as outfile:
                outfile.write(renderedTemplate)

    def dumpMeshQuality(self):
        for localmeshkey in self.localmeshes:
            mesh = self.localmeshes[localmeshkey]

            if _pycgal.CGAL.is_triangle_mesh(mesh.sm):
                print(  # noqa: T201
                    localmeshkey,
                    mesh,
                    mesh.polygonCount(),
                    mesh.vertexCount(),
                    mesh.area(),
                    mesh.volume(),
                )
            else:
                print(localmeshkey)  # noqa: T201

    def __repr__(self):
        return "ViewerBase"
