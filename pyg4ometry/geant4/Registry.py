from collections import defaultdict as _defaultdict
import pyg4ometry.exceptions as _exceptions
from . import _Material as _mat
from . import solid


def solidName(var):
    if isinstance(var, solid.SolidBase):
        return var.name
    elif isinstance(var, str):
        return var


class Registry:
    """
    Object to store geometry for input and output. \
    All of the pyg4ometry classes can be used without \
    storing them in the Registry. The registry is used \
    to write the GDML output file. A registry needs to \
    be used in conjunction with GDML Define objects for \
    evaluation of expressions.
    """
    def __init__(self):
        self.materialList = []
        # note python3 dictionaries are ordered by default
        self.defineDict                   = {}
        self.materialDict                 = {}
        self.solidDict                    = {}
        self.logicalVolumeDict            = {}
        self.assemblyVolumeDict           = {}
        self.physicalVolumeDict           = {}
        self.surfaceDict                  = {}
        self.loopDict                     = {}

        self.logicalVolumeList            = [] # Ordered list of logical volumes (and assemblies) from world down to bottom

        self.solidUsageCountDict          = _defaultdict(int) # solidName1, solidName2
        self.volumeTypeCountDict          = _defaultdict(int) # logical, physical, assembly
        self.physicalVolumeCountDict      = _defaultdict(int) #
        self.surfaceTypeCountDict         = _defaultdict(int) # border, skin
        self.logicalVolumeMeshSkip        = []                # meshes to skip because they are inefficient
        self.userInfo                     = []                # Ordered list for the user info, which is not processed
        
        self.defineNameCount              = _defaultdict(int)
        self.materialNameCount            = _defaultdict(int)
        self.materialUsageCount           = _defaultdict(int)
        self.solidNameCount               = _defaultdict(int)
        self.logicalVolumeNameCount       = _defaultdict(int)
        self.assemblyVolumeNameCount      = _defaultdict(int)
        self.physicalVolumeNameCount      = _defaultdict(int)
        self.surfaceNameCount             = _defaultdict(int)


        self.solidTypeCountDict           = _defaultdict(int) # Box, Cons etc
        self.logicalVolumeUsageCountDict  = _defaultdict(int) # named logical usage in physical
        
        self.editedSolids                 = []               # Solids changed post-initialisation

        self.expressionParser = None

    def clear(self):
        """Empty all internal structures"""
        # to match constructor
        self.defineDict.clear()
        self.materialDict.clear()
        self.solidDict.clear()
        self.logicalVolumeDict.clear()
        self.assemblyVolumeDict.clear()
        self.physicalVolumeDict.clear()
        self.surfaceDict.clear()
        self.loopDict.clear()
        
        self.logicalVolumeList = []

        self.solidUsageCountDict.clear()
        self.volumeTypeCountDict.clear()
        self.physicalVolumeCountDict.clear()
        self.surfaceTypeCountDict.clear()
        self.logicalVolumeMeshSkip = []
        self.userInfo = []

        self.definNameCount.clear()
        self.materialNameCount.clear()
        self.materialUsageCount.clear()
        self.solidNameCount.clear()
        self.logicalVolumeNameCount.clear()
        self.assemblyVolumeNameCount.clear()
        self.physicalVolumeNameCount.clear()
        self.surfaceNameCount.clear()
        
        self.solidTypeCountDict.clear()
        self.logicalVolumeUsageCountDict.clear()

        self.editedSolids = []
        
    def getExpressionParser(self):
        if not self.expressionParser:
            from pyg4ometry.gdml.Expression import ExpressionParser
            self.expressionParser = ExpressionParser()

        return self.expressionParser

    def registerSolidEdit(self, solid):
        if solid.name in self.solidDict:
            self.editedSolids.append(solid.name)

    def addMaterial(self, material, dontWarnIfAlreadyAdded=False):
        """
        Register a material with this registry.

        :param material: Material object for storage
        :type material: Material
        """
        if material.name in self.materialDict:
            if material.type == "nist":
                return
            # there is the possibility of composite materials reusing the same
            # material or element, so we must tolerate this in this recursive function
            if dontWarnIfAlreadyAdded:
                pass
            else:
                raise _exceptions.IdenticalNameError(material.name, "material")
        else:
            self.materialDict[material.name] = material
            # Material and Element have a member 'components' but Isotope doesn't
            if hasattr(material, "components"):
                for component in material.components:
                    self.addMaterial(component[0])

        self.materialNameCount[material.name] += 1

    def transferMaterial(self, material, incrementRenameDict={}, userRenameDict=None):
        """
        Transfer a material to this registry. Doesn't handle any members'
        transferal - only the material itself.
        """
        import re as _re
        if userRenameDict :
            for find, replace in userRenameDict.items() :
                material.name = _re.sub(find, replace, material.name)

        if material.name in incrementRenameDict:
            return # it's already been transferred in this 'transfer' call, ignore
        if material.name in self.materialDict:
            if material.type == "nist":
                return # nist ones generally aren't added and allowed to pass through
            else:
                newName = material.name + "_" + str(self.materialNameCount[material.name])
                self.materialNameCount[material.name] += 1
                incrementRenameDict[newName] = material.name
                material.name = newName
                # Material and Element have a member 'components' but Isotope doesn't
                if hasattr(material, "components"):
                    for component in material.components:
                        self.transferMaterial(component[0], incrementRenameDict, userRenameDict)
        else:
            incrementRenameDict[material.name] = material.name
            # Material and Element have a member 'components' but Isotope doesn't
            if hasattr(material, "components"):
                for component in material.components:
                    self.transferMaterial(component[0], incrementRenameDict, userRenameDict)

        self.materialDict[material.name] = material
        material.registry = self

    def addSolid(self, solid):
        """
        Register a solid with this registry.

        :param solid: Solid object for storage
        :type solid: One of the geant4 solids
        """
        if solid.name in self.solidDict:
            raise _exceptions.IdenticalNameError(solid.name, "solid")
        else:
            self.solidDict[solid.name] = solid

        self.solidTypeCountDict[solid.type] += 1
        self.solidNameCount[solid.name] += 1

    def transferSolid(self, solid, incrementRenameDict={}, userRenameDict=None):
        """
        Transfer a solid to this registry. Doesn't handle any members'
        transferal - only the solid itself.
        
        :param solid: Solid object for storage
        :type solid: One of the geant4 solids
        """
        import re as _re
        if userRenameDict :
            for find, replace in userRenameDict.items() :
                solid.name = _re.sub(find, replace, solid.name)

        if solid.name in incrementRenameDict:
            return # it's already been transferred in this 'transfer' call, ignore
        if solid.name in self.solidDict:
            # we already have a solid called this, so uniquely name it by incrementing it
            newName = solid.name + "_" + str(self.solidNameCount[solid.name])
            self.solidNameCount[solid.name] += 1
            incrementRenameDict[newName] = solid.name
            solid.name = newName
        else:
            incrementRenameDict[solid.name] = solid.name

        self.solidDict[solid.name] = solid
        solid.registry = self
            
        self.solidTypeCountDict[solid.type] += 1
        self.solidNameCount[solid.name] += 1

    def addLogicalVolume(self, volume):
        """
        Register a logical volume with this registry. Also accepts Assembly Volumes.

        :param volume: LogicalVolume object for storage
        :type volume: LogicalVolume
        """
        if volume.name in self.logicalVolumeDict:
            raise _exceptions.IdenticalNameError(volume.name, "logical volume")
        else:
            self.logicalVolumeDict[volume.name] = volume

        self.logicalVolumeNameCount[volume.name]  += 1
        self.volumeTypeCountDict["logicalVolume"] += 1
        # material doesn't exist for an assembly volume, which this function is also used for
        if volume.type == "logical":
            self.materialUsageCount[volume.material.name] += 1
        elif volume.type == 'assembly':
            self.assemblyVolumeDict[volume.name] = volume
            self.assemblyVolumeNameCount[volume.name] += 1

    def transferLogicalVolume(self, volume, incrementRenameDict={}, userRenameDict=None):
        """
        Transfer a logical volume to this registry. Doesn't handle any members'
        transferal - only the logical volume itself.
        """
        import re as _re
        if userRenameDict :
            for find, replace in userRenameDict.items() :
                volume.name = _re.sub(find, replace, volume.name)

        if volume.name in incrementRenameDict:
            return # it's already been transferred in this 'transfer' call, ignore
        if volume.name in self.logicalVolumeDict:
            # we already have an LV called this, so uniquely name it by incrementing it
            newName =  volume.name + "_" + str(self.logicalVolumeNameCount[volume.name])
            self.logicalVolumeNameCount[volume.name] += 1
            incrementRenameDict[newName] = volume.name
            volume.name = newName
        else:
            incrementRenameDict[volume.name] = volume.name

        self.logicalVolumeDict[volume.name] = volume
        volume.registry = self

        self.logicalVolumeNameCount[volume.name] += 1
        self.volumeTypeCountDict["logicalVolume"] += 1

    def addPhysicalVolume(self, volume):
        """
        Registry a physical volume with this registry.

        :param volume: PhysicalVolume object for storage
        :type volume: PhysicalVolume
        """
        if volume.name in self.physicalVolumeDict:
            raise _exceptions.IdenticalNameError(volume.name,"physical volume")
        else:
            self.physicalVolumeDict[volume.name] = volume

        self.physicalVolumeNameCount[volume.name] += 1
        self.volumeTypeCountDict["physicalVolume"] += 1
        self.logicalVolumeUsageCountDict[volume.logicalVolume.name] += 1

    def transferPhysicalVolume(self, volume, incrementRenameDict={}, userRenameDict=None):
        """
        Transfer a physical volume to this registry. Doesn't handle any members'
        transferal - only the physical volume itself.
        """
        import re as _re
        if userRenameDict :
            for find, replace in userRenameDict.items() :
                volume.name = _re.sub(find, replace, volume.name)

        if volume.name in incrementRenameDict:
            return # it's already been transferred in this 'transfer' call, ignore
        if volume.name in self.physicalVolumeDict:
            # we already have a PV called this, so uniquely name it by incrementing it
            newName = volume.name + "_" + str(self.physicalVolumeNameCount[volume.name])
            self.physicalVolumeNameCount[volume.name] += 1
            incrementRenameDict[newName] = volume.name
            volume.name = newName
        else:
            incrementRenameDict[volume.name] = volume

        self.physicalVolumeDict[volume.name] = volume
        volume.registry = self

        self.physicalVolumeNameCount[volume.name] += 1
        self.volumeTypeCountDict["physicalVolume"] += 1
        self.logicalVolumeUsageCountDict[volume.logicalVolume.name] += 1

    def addSurface(self, surface):
        """
        Register a surface with this registry.

        :param surface: Surface
        :type surface:  pyg4ometry.geant4.BorderSurface or pyg4ometry.geant4.SkinSurface
        """
        if surface.name in self.surfaceDict:
            raise _exceptions.IdenticalNameError(surface.name, "surface")
        else:
            self.surfaceDict[surface.name] = surface

        self.surfaceTypeCountDict[surface.type] += 1
        self.surfaceNameCount[surface.name] += 1

    def transferSurface(self, surface, incrementRenameDict={}, userRenameDict=None):
        """
        Transfer a surface to this registry.
        """
        import re as _re
        if userRenameDict :
            for find, replace in userRenameDict.items() :
                surface.name = _re.sub(find, replace, surface.name)

        if surface.name in incrementRenameDict:
            return  # it's already been transferred in this 'transfer' call, ignore
        if surface.name in self.surfaceDict:
            # we already have a solid called this, so uniquely name it by incrementing it
            newName = surface.name + "_" + str(self.surfaceNameCount[surface.name])
            self.surfaceNameCount[surface.name] += 1
            incrementRenameDict[newName] = surface.name
            surface.name = newName
        else:
            incrementRenameDict[surface.name] = surface.name

        self.surfaceDict[surface.name] = surface
        surface.registry = self

        self.surfaceTypeCountDict[surface.type] += 1
        self.surfaceNameCount[surface.name] += 1

    def addAuxiliary(self, auxiliary):
            self.userInfo.append(auxiliary)

    def addDefine(self, define):
        """
        Register a define with this registry.

        :param define: Definition object for storage
        :type define: Constant, Quantity, Variable, Matrix
        """
        from pyg4ometry.gdml.Units import units as _units
        if define.name in _units:
            raise ValueError("Redefinition of a constant unit : {}".format(define.name))

        if define.name in self.defineDict:
            raise _exceptions.IdenticalNameError(define.name,"define")
        else:
            self.defineDict[define.name] = define

        self.defineNameCount[define.name] += 1

        return define.name # why do we need this?

    def transferDefine(self, define, incrementRenameDict={}, userRenameDict=None):
        """
        Transfer a single define from another registry to this one. No checking on previous registry or not.
        """
        import re as _re
        if userRenameDict :
            for find, replace in userRenameDict.items() :
                define.name = _re.sub(find, replace, define.name)

        if define.name in incrementRenameDict:
            return  # it's already been transferred in this 'transfer' call, ignore
        if define.name in self.defineDict:
            newName = define.name + "_" + str(self.defineNameCount[define.name])
            self.defineNameCount[define.name] += 1
            incrementRenameDict[newName] = newName
            define.name = newName
        else:
            incrementRenameDict[define.name] = define.name
        
        self.defineDict[define.name] = define
        define.registry = self

        self.defineNameCount[define.name] += 1

    def transferDefines(self, var, incrementRenameDict={}, userRenameDict=None):
        """
        This function tolerates all types of defines including vector ones.

        Transfer defines from one registry to another recursively. A define may not be part of
        the old registry so won't be added to this one. A define may be a vector or composite
        and its 'bits' may be in the (old) registry so each part should be checked.

        In "3x + 2", "x" would be a variable".  In "3.5*2" there would be no variables.
        """
        import pyg4ometry.gdml.Defines as _Defines
        import numpy as _np

        # If the variable is a position, rotation or scale
        if isinstance(var,_Defines.VectorBase):
            # check and transfer components all called x,y,z for each type
            for vi in (var.x, var.y, var.z):
                # any variables inside each component
                for v in vi.variables():
                    if v in self._registryOld.defineDict: # only if its in the other registry
                        self.transferDefines(self._registryOld.defineDict[v], incrementRenameDict, userRenameDict)

            if var.name in self._registryOld.defineDict:
                self.transferDefine(var, incrementRenameDict, userRenameDict)

        elif isinstance(var,_Defines.ScalarBase): # a normal expression
            for v in var.expr.variables():                 # loop over all variables needed for an expression
                if v in self._registryOld.defineDict:      # only if its in the other registry
                    self.transferDefine(self._registryOld.defineDict[v], incrementRenameDict, userRenameDict)

            if var.name in self._registryOld.defineDict:      # check if variable is stored in registry, if so need to be transferred
                self.transferDefine(var, incrementRenameDict, userRenameDict) # probably best to reuse here

        else:
            return

    def setWorld(self, worldIn):
        """
        The argument can either be the name of logical volume of the world
        or the pyg4ometry.geant4.LogicalVolume instance of the world volume.
        The term world is used to refer to the outermost volume of the hierarchy.
        """
        if type(worldIn) is str:
            # assume it's the name of the world volume
            self.worldName = worldIn
            self.worldVolume = self.logicalVolumeDict[worldIn]
            self.orderLogicalVolumes(worldIn)
            self.logicalVolumeList.append(worldIn)
        elif worldIn.__class__.__name__ == "LogicalVolume": # way to test without importing it
            self.worldName = worldIn.name
            self.worldVolume = worldIn
            if worldIn not in self.logicalVolumeDict:
                self.logicalVolumeDict[worldIn.name] = worldIn
            self.logicalVolumeList.append(worldIn.name)
        else:
            raise TypeError("Invalid type ", worldIn.__class__.__name__," - must be str or LogicalVolume")

    def _orderMaterialList(self, materials, materials_ordered=[]):
        for mat in materials:
            if isinstance(mat, _mat.Material) and mat not in materials_ordered:
                component_objects = [comp[0] for comp in mat.components]
                materials_ordered = self._orderMaterialList(component_objects, materials_ordered)
                materials_ordered.append(mat)
        return materials_ordered

    def orderMaterials(self):
        """
        Need to have a ordered list of all material entities for writing to
        GDML. GDML needs to have the isotopes/elements/materials defined in use order
        """
        for name in list(self.materialDict.keys()):  # Forces registered materials to
            if isinstance(self.materialDict[name], _mat.Material):           # recursively register their components too
                self.materialDict[name].set_registry(self, dontWarnIfAlreadyAdded=True)

        # Order is isotopes -> elements -> materials
        isotopes = []  # Isotopes and elements don't need internal ordering as no
        elements = []  # isotope of isotopes or element of elements
        materials = []  # Material do need internal ordering as material of materials is possible
        for name, obj in self.materialDict.items():
            if isinstance(obj, _mat.Isotope):
                isotopes.append(obj)
            elif isinstance(obj, _mat.Element):
                elements.append(obj)
            else:
                materials.append(obj)

        materials_ordered = self._orderMaterialList(materials)
        self.materialList = isotopes + elements + materials_ordered

    def orderLogicalVolumes(self, lvName, first=True):
        """
        Need to have an ordered list from most basic (solid) object upto physical/logical volumes for writing to
        GDML. GDML needs to have the solids/booleans/volumes defined in order
        """
        if first:
            self.logicalVolumeList = []

        lv = self.logicalVolumeDict[lvName]
        for daughter in lv.daughterVolumes:
            dlvName = daughter.logicalVolume.name
            try:
                self.logicalVolumeList.index(dlvName)
            except ValueError:
                self.orderLogicalVolumes(dlvName, False)
                self.logicalVolumeList.append(dlvName)

    def addVolumeRecursive(self, volume, collapseAssemblies=False, incrementRenameDict=None, userRenameDict=None):
        """
        Transfer a volume hierarchy to this registry. Any objects that had a registry set to
        another will be set to this one and will be owned by it effectively.
        :param volume: PhysicalVolume or LogicalVolume or AssemblyVolume.
        :param collapseAssemblies: if True, daughters of AssemblyVolume's will be attached directly to the mother of the assembly and the AssemblyVolume itself will be eliminated from the geometry tree
        :param incrementRenameDict: ignore - dictionary used internally for potentially incrementing names
        :param userRenameDict: a dictionary of find/replace regex strings to be used to rename volumes/materials/etc.

        In the case where some object or variable has a name (e.g. 'X') that already exists
        in this registry, it will be incremented to 'X_1'.
        """
        import pyg4ometry.geant4.LogicalVolume as _LogicalVolume
        import pyg4ometry.geant4.PhysicalVolume as _PhysicalVolume
        import pyg4ometry.geant4.AssemblyVolume as _AssemblyVolume

        if incrementRenameDict is None and collapseAssemblies == True and isinstance(volume, _AssemblyVolume) :
            raise RuntimeError('Registry:addVolumeRecursive : cannot collapse assemblies when top level volume is an AssemblyVolume')

        if incrementRenameDict is None:
            incrementRenameDict = {}
        self._registryOld = volume.registry

        if isinstance(volume, _PhysicalVolume):
            self.addVolumeRecursive(volume.logicalVolume, collapseAssemblies, incrementRenameDict, userRenameDict)

            # add members from physical volume
            self.transferDefines(volume.position, incrementRenameDict, userRenameDict)
            self.transferDefines(volume.rotation, incrementRenameDict, userRenameDict)
            if volume.scale:
                self.transferDefines(volume.scale, incrementRenameDict, userRenameDict)
            self.transferPhysicalVolume(volume, incrementRenameDict, userRenameDict)

        elif isinstance(volume, _LogicalVolume):
            # loop over all daughters
            assembliesToRemove = []
            for dv in volume.daughterVolumes:
                if collapseAssemblies and isinstance(dv.logicalVolume, _AssemblyVolume) :
                    positions = []
                    rotations = []
                    scales = []
                    names = []
                    self.addAndCollapseAssemblyVolumeRecursive(dv, volume, positions, rotations, scales, names, incrementRenameDict, userRenameDict)
                    assembliesToRemove.append( dv.name )
                else :
                    self.addVolumeRecursive(dv, collapseAssemblies, incrementRenameDict, userRenameDict)

            # if we're collapsing assembly volumes, prune any assembly daughters
            for assemblyName in assembliesToRemove :
                assembly = volume._daughterVolumesDict.pop(assemblyName)
                volume.daughterVolumes.remove(assembly)

            # add members from logical volume
            self.transferSolidDefines(volume.solid, incrementRenameDict, userRenameDict)
            self.transferSolid(volume.solid, incrementRenameDict, userRenameDict)
            self.transferMaterial(volume.material, incrementRenameDict, userRenameDict)
            self.transferLogicalVolume(volume, incrementRenameDict, userRenameDict)

        elif isinstance(volume, _AssemblyVolume):
            # loop over all daughters
            for dv in volume.daughterVolumes:
                self.addVolumeRecursive(dv, collapseAssemblies, incrementRenameDict, userRenameDict)

            # add members from logical volume
            self.transferLogicalVolume(volume, incrementRenameDict, userRenameDict)
        else:
            print("Volume type not supported yet for merging")

        return incrementRenameDict

    def addAndCollapseAssemblyVolumeRecursive(self, assemblyPV, motherVol, positions, rotations, scales, names, incrementRenameDict, userRenameDict):
        """
        Transfer and collapse an AssemblyVolume hierarchy to this registry.
        Daughter volumes are copied, renamed, and attached to the supplied
        mother LogicalVolume with the correct position/rotation.
        Any objects that had a registry set to another will be set to this one
        and will be owned by it effectively.
        :param assemblyPV: the PhysicalVolume that places an AssemblyVolume
        :param motherVol: the LogicalVolume to which all daughters of the AssemblyVolume (including any daughters of nested AssemblyVolume's) should be attached
        :param positions: a list (initially empty) to hold position objects for each AssemblyVolume in a hierarchy of nested assemblies (used to correctly set the transformation of daughters within the motherVol)
        :param rotations: a list (initially empty) to hold rotation objects for each AssemblyVolume in a hierarchy of nested assemblies (used to correctly set the transformation of daughters within the motherVol)
        :param scales: a list (initially empty) to hold scale objects for each AssemblyVolume in a hierarchy of nested assemblies (used to correctly set the transformation of daughters within the motherVol)
        :param names: a list (initially empty) to hold the names of each AssemblyVolume in a hierarchy of nested assemblies (used to set unique names for the daughters within the motherVol)
        :param incrementRenameDict: ignore - dictionary used internally for potentially incrementing names
        :param userRenameDict: a dictionary of find/replace regex strings to be used to rename volumes/materials/etc.
        """
        import numpy as _np
        import pyg4ometry.geant4.PhysicalVolume as _PhysicalVolume
        import pyg4ometry.geant4.AssemblyVolume as _AssemblyVolume
        import pyg4ometry.transformation as _transformation
        import pyg4ometry.gdml.Defines as _Defines

        positions.append( assemblyPV.position )
        rotations.append( assemblyPV.rotation )
        scales.append( assemblyPV.scale )
        names.append( assemblyPV.name )

        # find the transformations for this assembly in the reference frame of the mother
        # start with identity transformations and then aggregate the placement
        # info of the assemblies
        mtra = _np.matrix([[1,0,0],[0,1,0],[0,0,1]])
        tra = _np.array([0,0,0])
        for pos, rot, sca in zip(positions, rotations, scales) :
            assembly_mrot = _np.linalg.inv(_transformation.tbxyz2matrix(rot.eval()))
            assembly_pos = _np.array(pos.eval())
            if sca :
                assembly_sca = _np.diag(sca.eval())
            else :
                assembly_sca = _np.diag([1,1,1])

            new_mtra = mtra * assembly_sca * assembly_mrot
            new_tra = (_np.array(mtra.dot(assembly_pos)) + tra)[0]

            mtra = new_mtra
            tra = new_tra

        # loop through the daughter volumes and either recurse (if it is also
        # an assembly) or deal properly with an actual solid placement
        assemblyLV = assemblyPV.logicalVolume
        for dv in assemblyLV.daughterVolumes:
            if isinstance(dv.logicalVolume, _AssemblyVolume) :
                self.addAndCollapseAssemblyVolumeRecursive(dv, motherVol, list(positions), list(rotations), list(scales), list(names), incrementRenameDict, userRenameDict)
            else :
                # we need to copy and rename the volume since we could
                # potentially end up with many of the same pv (now with
                # different positions) being attached to the mother volume
                # NB we already set here the mother volume to be the new one
                names_copy = list(names)
                names_copy.reverse()
                dv_copy_name = dv.name
                for name in names_copy :
                    dv_copy_name =  name + '_' + dv_copy_name
                dv_copy = _PhysicalVolume( dv.rotation, dv.position, dv.logicalVolume, dv_copy_name, motherVol, None, dv.copyNumber, False, dv.scale)

                # redefine the position and rotation of the daughter volume to
                # be in the reference frame of the new mother volume, using the
                # aggregated assembly transforms calculated above and the
                # transforms of the pv itself
                dv_mrot = _np.linalg.inv(_transformation.tbxyz2matrix(dv_copy.rotation.eval()))
                dv_pos = _np.array(dv_copy.position.eval())
                if dv_copy.scale :
                    dv_sca = _np.diag(dv_copy.scale.eval())
                else :
                    dv_sca = _np.diag([1,1,1])

                new_mtra = mtra * dv_sca * dv_mrot
                new_tra = (_np.array(mtra.dot(dv_pos)) + tra)[0]

                new_rot = _transformation.matrix2tbxyz(_np.linalg.inv(new_mtra))
                new_pos = new_tra.tolist()

                # update the position and rotation information
                dv_copy.position = _Defines.Position( dv_copy.name + dv_copy.position.name.removeprefix(dv.name), new_pos[0], new_pos[1], new_pos[2],  "mm", self, False )
                dv_copy.rotation = _Defines.Rotation( dv_copy.name + dv_copy.rotation.name.removeprefix(dv.name), new_rot[0], new_rot[1], new_rot[2], "rad", self, False )

                # add this volume recursively to the registry
                self.addVolumeRecursive(dv_copy, True, incrementRenameDict, userRenameDict)

    def transferSolidDefines(self, solid, incrementRenameDict={}, userRenameDict=None):
        """
        For each parameter in a given solid (unique to each) check if it's
        a define and transfer that over.
        """
        # TODO make this work for all classes (using update variables method)

        if solid.type == "Subtraction" or solid.type == "Union" or solid.type == "Intersection" :
            self.transferSolidDefines(solid.obj1, incrementRenameDict, userRenameDict)
            self.transferSolidDefines(solid.obj2, incrementRenameDict, userRenameDict)
        elif solid.type == "MultiUnion" :
            for object in solid.objects :
                self.transferSolidDefines(object, incrementRenameDict, userRenameDict)

        for varName in solid.varNames :
            # skip unit variables
            if varName.find("unit") != -1:
                continue
            # skip slicing variables
            if varName.find("slice") != -1 and varName.find("pZslices") == -1 :
                continue
            # skip stack variables
            if varName.find("stack") != -1:
                continue

            def flatten(S):
                if S == []:
                    return S
                if isinstance(S[0], list):
                    return flatten(S[0]) + flatten(S[1:])
                return S[:1] + flatten(S[1:])

            var = getattr(solid,varName)

            if isinstance(var, (int, float, str)):  # int, float, str could not be in registry
                continue
            elif isinstance(var,list):              # list of variables
                var = flatten(var)
            else:
                var = [var]                         # single variable upgraded to list

            for v in var:                           # loop over variables
                self.transferDefines(v, incrementRenameDict, userRenameDict)

    def volumeTree(self, lvName):
        """Not sure what this method is used for"""
        lv = self.logicalVolumeDict[lvName]

    def solidTree(self, solidName):
        """Not sure what this method is used for"""
        solid = self.solidDict[solidName]

        if solid.type == 'union' or solid.type == 'intersecton' or solid.type == 'subtraction':
            self.solidTree(solid.obj1.name)
            self.solidTree(solid.obj2.name)

    def getWorldVolume(self) :         
        return self.worldVolume

    def printStats(self):
        print(self.solidTypeCountDict)
        print(self.logicalVolumeUsageCountDict)

    def toFlukaRegistry(self):
        import pyg4ometry.fluka as _f

        freg = _f.FlukaRegistry()

    def structureAnalysis(self, lv_name=None, debug=False, level=0, df=None):
        return AnalyseGeometryStructure(self, lv_name, debug, level, df)


class GeometryComplexityInformation:
    def __init__(self):
        self.solids            = _defaultdict(int)
        self.nDaughtersPerLV   = _defaultdict(int)
        self.nDaughters        = {}
        self.booleanDepthCount = _defaultdict(int)
        self.booleanDepth      = _defaultdict(int)

    def printSummary(self, boolDepthLimit=3):
        print("Types of solids")
        solidsSorted = sorted(self.solids.items(),key=lambda x: x[1], reverse=True)
        for solidName,number in solidsSorted:
            print(solidName.ljust(20),':',number)
        
        print(" ")
        print("# of daughters".ljust(20),"count")
        for nDaughters in sorted(self.nDaughtersPerLV.keys()):
            print(str(nDaughters).ljust(20), ':', self.nDaughtersPerLV[nDaughters])

        print(" ")
        print("Depth of booleans".ljust(20),"count")
        for boolDepth in sorted(self.booleanDepthCount.keys()):
            print(str(boolDepth).ljust(20), ':', self.booleanDepthCount[boolDepth])

        print(" ")
        print("Booleans width depth over ",boolDepthLimit)
        print("Solid name".ljust(40),":","n Booleans")
        boolDepthSorted = sorted(self.booleanDepth.items(),key=lambda x: x[1], reverse=True)
        for solidName,boolDepth in boolDepthSorted:
            if boolDepth > boolDepthLimit:
                print(solidName.ljust(40),":",boolDepth)
        

def AnalyseGeometryComplexity(logicalVolume):
    """
    Analyse a geometry tree starting from a logical volume.
    Produces an instance of :class:`GeometryComplexityInformation` with
    summary information. Provides:
    
    * count per solid type
    * number of daughters per logical volume
    * dictionary of N daughters for each logical volume name
    * depth count of Boolean solids

    ie a Boolean of a Boolean returns 2, a Boolean of two primitives returns 1

    * a dictionary of boolean depth for each logical volume name

    Example: ::

        info = AnalyseGeometryComplexity(lv)
        info.printSummary()
    """
    result = GeometryComplexityInformation()
    result = _UpdateComplexity(logicalVolume, result)
    return result

def _UpdateComplexity(lv, info):
    if lv.type != "assembly" :
        info.solids[lv.solid.type] += 1

    info.nDaughters[lv.name] = len(lv.daughterVolumes)
    info.nDaughtersPerLV[len(lv.daughterVolumes)] +=1

    booleanTypes = ['Union', 'Subtraction', 'Intersection']
    
    def _CountDaughterBooleanSolids(solid, number=0):
        for solid in [solid.obj1, solid.obj2]:
            if solid.type in booleanTypes:
                number += 1
                number = _CountDaughterBooleanSolids(solid, number)
        return number           

    if lv.type != "assembly" and lv.solid.type in booleanTypes:
        nBooleans = 1
        nBooleans = _CountDaughterBooleanSolids(lv.solid, nBooleans)
        info.booleanDepthCount[nBooleans] += 1
        info.booleanDepth[lv.name] = nBooleans

    # recurse
    for pv in lv.daughterVolumes:
        info = _UpdateComplexity(pv.logicalVolume, info)
    
    return info

def AnalyseGeometryStructure(registry, lv_name=None, debug=False, level=0, df=None):
    # do the heavy import only in the function
    import pandas as _pd
    reg = registry #shortcut
    if lv_name is None:
        lv_name = reg.getWorldVolume().name

    if df is None:
        reg.logicalVolumeList = []
        df = _pd.DataFrame(columns=['level', 'mother', 'material', 'daughters', 'mother_lv', 'daughters_lv'])

    mother_lv = reg.logicalVolumeDict[lv_name]
    mother = mother_lv.name
    daughters_lv = [daughter.logicalVolume for daughter in mother_lv.daughterVolumes]
    daughters = [daughter.name for daughter in daughters_lv]
    material = mother_lv.material.name.split('0')[0]

    df = df.append({'level': level, 'mother_lv': mother_lv, 'mother': mother, 'daughters_lv': daughters_lv,
                    'daughters': daughters, 'material': material}, ignore_index=True)

    if debug:
        print("\nlevel:", level)
        print("mother:", mother)
        print("daughters: ", len(daughters), " ", daughters)

    level += 1

    for daughters in mother_lv.daughterVolumes:
        lv_name = daughters.logicalVolume.name
        try:
            reg.logicalVolumeList.index(lv_name)
        except ValueError:
            df = reg.structureAnalysis(lv_name, debug, level, df)
            reg.logicalVolumeList.append(lv_name)

    return df

def DumpGeometryStructureTree(lv, depth=0) :
    print(4*(depth-1)*' '+4*'-'+'>'+lv.name)

    for dv in lv.daughterVolumes :
        print(4*(depth+1)*' '+4*'-'+'>' + dv.name+" (pv)")

        DumpGeometryStructureTree(dv.logicalVolume, depth+3)