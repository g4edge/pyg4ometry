from xml.dom import getDOMImplementation
from ..geant4._Material import Material as _Material
from ..geant4._Material import Element as _Element
from ..geant4._Material import Isotope as _Isotope
from ..gdml import Defines as _Defines
from . import Expression as _Expression
import pyg4ometry.geant4 as _g4
import logging as _log

from pyg4ometry.geant4 import Expression as _Expression

class Writer(object):
    def __init__(self, prepend = ''):
        super(Writer, self).__init__()
        self.prepend = prepend

        self.imp = getDOMImplementation()
        self.doc = self.imp.createDocument(None,"gdml",None)
        self.top = self.doc.documentElement
        self.top.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
        self.top.setAttribute('xsi:noNamespaceSchemaLocation',
                              'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd')

        self.defines   = self.top.appendChild(self.doc.createElement('define'))
        self.materials = self.top.appendChild(self.doc.createElement('materials'))
        self.solids    = self.top.appendChild(self.doc.createElement('solids'))
        self.structure = self.top.appendChild(self.doc.createElement('structure'))
        self.userinfo  = self.top.appendChild(self.doc.createElement('userinfo'))
        self.setup     = self.top.appendChild(self.doc.createElement('setup'))

        self.materials_written = []
        self.solids_written    = []

        self.defineList        = []
        self.materialList      = []
        self.solidList         = []
        self.logicalVolumeList = []
        self.physicalVolumeList= []

    def addDetector(self, registry) :
        self.registry = registry

        if not self.registry.userInfo:
            # Geant4 version earlier than 10.1 do not support userinfo
            # If no user info is specified, remove the userinfo tag from the GDML document
            # This is done here, because the regsitry is not available at construction time
            self.top.removeChild([n for n in self.top.childNodes if n.tagName == "userinfo"][0])

        # Set the world again to force a refresh on the
        # ordering of logical volumes
        self.registry.setWorld(self.registry.worldName)

        # loop over defines
        for definition in registry.defineDict:
            _log.info('gdml.Writer.addDetector> define '+definition)
            define = self.registry.defineDict[definition]
            self.writeDefine(define)

        # loop over materials
        for mat in registry.materialDict:
            _log.info('gdml.Writer.addDetector> material '+mat)
            material = self.registry.materialDict[mat]
            self.writeMaterial(material)

        # loop over solids
        for solidId in registry.solidDict.keys():
            _log.info('gdml.Writer.addDetector> solid '+solidId)
            solid = registry.solidDict[solidId]
            self.writeSolid(solid)

        # loop over logical volumes
        for logicalName in registry.logicalVolumeList:
            _log.info('gdml.Writer.addDetector> logical '+logicalName)
            logical = registry.logicalVolumeDict[logicalName]
            if logical.type == "logical" : 
                self.writeLogicalVolume(logical)
                self.writeMaterial(logical.material)
            elif logical.type == "assembly" : 
                self.writeAssemblyVolume(logical)

        # loop over surfaces
        for surfaceName in registry.surfaceDict:
            _log.info('gdml.Writer.addDetector> surface '+surfaceName)
            surface = registry.surfaceDict[surfaceName]
            if surface.type == "bordersurface":
                self.writeBorderSurface(surface)
            elif surface.type == "skinsurface":
                self.writeSkinSurface(surface)

        for auxiliary in registry.userInfo:
            self.writeAuxiliary(auxiliary)


        self.setup.setAttribute("name","Default")
        self.setup.setAttribute("version","1.0")
        we = self.doc.createElement("world")
        # we.setAttribute("ref",self.prepend + registry.worldName+"_lv")
        we.setAttribute("ref",self.prepend + registry.worldName)
        self.setup.appendChild(we)

    def write(self, filename) :
        f = open(filename,'w')
        xmlString = self.doc.toprettyxml()
        f.write(xmlString)
        f.close()

    def writeGMADTesterNoBeamline(self, gmad, gdml):
        text = """test: placement, geometryFile="gdml:{}";
        beam, particle="e-",
        energy=250*GeV;
        option, physicsList="em";
        option, preprocessGDML=0;
        """.format(gdml)

        with open(gmad, "w") as f:
            f.write(text)

    def writeGmadTester(self, filenameGmad, filenameGDML,
                        writeDefaultLattice=False,
                        preprocessGDML=True):
        if writeDefaultLattice:
            self.writeDefaultLattice()

        s = f'e1: element, geometry="gdml:{filenameGDML}'
        if "GDML_Size_position_z" in self.registry.defineDict:
            s += '", l=' + str(self.registry.defineDict['GDML_Size_position_z'].value) + '*mm;\n'
        else:
            # be super tolerant incase the meshing fails - still write out
            try:
                ext = self.registry.worldVolume.mesh.getBoundingBox()
                dz = ext[1][2] - ext[0][2]
                s += '", l=' + str(dz) + '*mm;\n'
            except IndexError:
                s += '", l=20*m;\n'
        s += """l1: line = (e1);
use, period=l1;

sample, all;
beam, particle="e-",
      energy=250*GeV;
option, physicsList="em";
option, preprocessGDML=0;
"""
        if not preprocessGDML:
            s += "option, preprocessGDML=0;\n"
        f = open(filenameGmad, 'w')
        f.write(s)
        f.close()

    def writeDefaultLattice(self, filename='lattice.gmad'):
        s =  'l1: line = (e1);\n'
        s += 'use,period=l1;\n'
        s += 'sample, all;\n'
        s += 'beam, particle="e-",\n'
        s += 'energy=250.0*GeV;\n'
        f = open(filename, 'w')
        f.write(s)
        f.close()

    def checkDefineName(self, defineName) :
        pass

    def checkMaterialName(self, materialName) :
        pass

    def checkSolidName(self, solidName) :
        pass

    def checkLogicalVolumeName(self, logicalVolumeName) :
        pass

    def checkPhysicalVolumeName(self, physicalVolumeName):
        pass

    def writeVectorVariable(self, node, vector_var, allow_ref=True, suppress_trivial=True):
        """
        Writes an XML child node for a vector variable - position, roration, scale.
        If allow_ref is enabled, it will write a ref to a registry define where possible.
        If suppress_trivial is enabled it won't write vectors with all elements zero.
        """
        if vector_var is None: # If not defined, skip
            return

        vv = vector_var
        vtype = vv.__class__.__name__.lower()
        if allow_ref and vv.name in self.registry.defineDict:
            # If possible and allowed, write the variable as a reference to a define
            vn = self.doc.createElement("{}ref".format(vtype))
            vn.setAttribute("ref", vv.name)
        else:
            if suppress_trivial and not vv.nonzero():
                return # If allowed, do not write trivial positions

            vn = self.doc.createElement(vtype)
            if vv.name: # Write the name where possible
                vn.setAttribute('name', vv.name)
            vn.setAttribute('x', vv.x.expression)
            vn.setAttribute('y', vv.y.expression)
            vn.setAttribute('z', vv.z.expression)
            if vv.unit != "none": # Write the unit if it is valid
                vn.setAttribute('unit', vv.unit)

        node.appendChild(vn)
        return vn

    def writeDefine(self, define):
        if isinstance(define, _Defines.Constant):
            oe = self.doc.createElement('constant')
            oe.setAttribute('name',define.name)
            oe.setAttribute('value',str(define.expr.expression))
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Quantity):
            oe = self.doc.createElement('quantity')
            oe.setAttribute('name',define.name)
            oe.setAttribute('value',str(define.expr.expression))
            oe.setAttribute('type',define.type)
            if define.unit is not None:
                oe.setAttribute('unit',define.unit)
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Variable):
            oe = self.doc.createElement('variable')
            oe.setAttribute('name',define.name)
            oe.setAttribute('value',str(define.expr.expression))
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Matrix):
            oe = self.doc.createElement('matrix')
            oe.setAttribute('name',define.name)
            oe.setAttribute('coldim',str(define.coldim))
            oe.setAttribute('values', " ".join([val.expr.expression for val in define.values]))
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Expression):
            oe = self.doc.createElement('expression')
            oe.setAttribute('name',define.name)
            tn = self.doc.createTextNode(define.expr.expression)
            oe.appendChild(tn)
            self.defines.appendChild(oe)
        elif any([isinstance(define, d) for d in [_Defines.Position, _Defines.Rotation, _Defines.Scale]]):
            self.writeVectorVariable(self.defines, define, allow_ref=False, suppress_trivial=False)
        else:
            raise Exception("Unrecognised define type: {}".format(type(define)))

    def writeMaterialProps(self, material, oe):
        for pname, pref in material.properties.items():
            prop = self.doc.createElement('property')
            prop.setAttribute('name', str(pname))
            if not isinstance(pref, _Defines.Matrix):
                raise ValueError("Only references to matrices can be used for material property {}".format(pname))
            # If possible, write the variable as a reference to a define
            if not ( pref.name in self.registry.defineDict ):
                raise RuntimeError("Invalid ref!")
            prop.setAttribute('ref', str(pref.name))
            oe.appendChild(prop)

    def writeMaterial(self, material):
        if material.name in self.materials_written:
            return

        if isinstance(material, _Material) :
            oe = self.doc.createElement('material')
            oe.setAttribute('name', material.name)
            if material.state != "" and material.state != None :
                oe.setAttribute('state', material.state)

            # No need to add defines for NIST compounds or
            # materials which are simply names.
            if material.type != 'nist' and material.type != 'arbitrary':
                # <property tags must be at the start to be valid GDML
                self.writeMaterialProps(material, oe)

                # state variable tags must be at the start to be valid GDML
                for pname in material.state_variables:
                    if pname == "temperature":
                        tagname = 'T'
                    elif pname == "pressure":
                        tagname = 'P'
                    else:
                        continue

                    value = material.state_variables[pname]
                    if value is None:
                        continue

                    de = self.doc.createElement(tagname)
                    de.setAttribute('value', str(value))
                    de.setAttribute('unit', material.state_variables[pname + "_unit"])
                    oe.appendChild(de)

            de = self.doc.createElement('D')
            de.setAttribute('value', str(material.density))
            oe.appendChild(de)

            if material.type == 'simple':
                oe.setAttribute('Z', str(int(material.atomic_number)))
                se  = self.doc.createElement('atom')
                se.setAttribute('value', str(material.atomic_weight))
                oe.appendChild(se)
                self.materials.appendChild(oe)
            elif material.type == 'composite':
                for comp_info in  material.components:
                    name = comp_info[0].name
                    frac_type = comp_info[2]
                    self.writeMaterial(comp_info[0])
                    if frac_type == "massfraction":
                        se = self.doc.createElement('fraction')
                        se.setAttribute('ref', name)
                        se.setAttribute('n', self.getValueOrExpr(comp_info[1]))
                        oe.appendChild(se)
                    if frac_type == "natoms":
                        se = self.doc.createElement('composite')
                        se.setAttribute('ref', name)
                        se.setAttribute('n', str(int(comp_info[1])))
                        oe.appendChild(se)
                self.materials.appendChild(oe)

        elif isinstance(material, _Element):
            oe = self.doc.createElement('element')
            oe.setAttribute('name', material.name)
            oe.setAttribute('formula', material.symbol)
            if material.type == 'element-simple':
                oe.setAttribute('Z', str(int(material.Z)))
                se = self.doc.createElement('atom')
                se.setAttribute('value', str(material.A))
                oe.appendChild(se)
            elif material.type == 'element-composite':
                for comp_info in material.components:
                    name = comp_info[0].name
                    self.writeMaterial(comp_info[0])
                    se = self.doc.createElement('fraction')
                    se.setAttribute('ref', name)
                    se.setAttribute('n', self.getValueOrExpr(comp_info[1]))
                    oe.appendChild(se)
            self.materials.appendChild(oe)

        elif isinstance(material, _Isotope) :
            oe = self.doc.createElement('isotope')
            oe.setAttribute('name', material.name)
            oe.setAttribute('Z', str(int(material.Z)))
            oe.setAttribute('N', str(int(material.N)))
            se = self.doc.createElement('atom')
            #se.setAttribute('type', 'A')
            se.setAttribute('value', str(material.a))
            oe.appendChild(se)
            self.materials.appendChild(oe)

        if material.name not in self.materials_written:
            self.materials_written.append(material.name)

    def writeLogicalVolume(self, lv):
        we = self.doc.createElement('volume')
        # we.setAttribute('name', "{}{}_lv".format(self.prepend, lv.name, '_lv'))
        we.setAttribute('name',"{}{}".format(self.prepend,lv.name))
        mr = self.doc.createElement('materialref')
        if lv.material.name.find("G4") != -1 :
            mr.setAttribute('ref', lv.material.name)
        else :
            mr.setAttribute('ref', "{}{}".format(self.prepend, lv.material.name))
        we.appendChild(mr)

        sr = self.doc.createElement('solidref')
        sr.setAttribute('ref', "{}{}".format(self.prepend, lv.solid.name))
        we.appendChild(sr)

        if lv.auxiliary:
            for aux in lv.auxiliary:
                self.writeAuxiliary(aux, parent=we)

        for dv in lv.daughterVolumes :
            if dv.type == "placement":
                dve = self.writePhysicalVolume(dv)
            elif dv.type == "parametrised":
                dve = self.writeParametrisedVolume(dv)
            elif dv.type == "replica":
                dve = self.writeReplicaVolume(dv)
            elif dv.type == "division":
                dve = self.writeDivisionVolume(dv)
            else:
                raise ValueError("Unknown daughter volume type: {}".format(dv.type))
            we.appendChild(dve)

        self.structure.appendChild(we)

    def writeAuxiliary(self, aux, parent=None):

        ax = self.doc.createElement('auxiliary')
        ax.setAttribute('auxtype', aux.auxtype)
        ax.setAttribute('auxvalue', aux.auxvalue)
        if aux.auxunit:
            ax.setAttribute('auxunit', aux.auxunit)

        for sx in aux.subaux:
            self.writeAuxiliary(sx, ax)

        if parent is not None:
            parent.appendChild(ax)
        else:
            self.userinfo.appendChild(ax)

    def writeAssemblyVolume(self, lv) :
        we = self.doc.createElement('assembly')
        # we.setAttribute('name', "{}{}_lv".format(self.prepend, lv.name, '_lv'))
        we.setAttribute('name',"{}{}".format(self.prepend,lv.name))

        for dv in lv.daughterVolumes :
            dve = self.writePhysicalVolume(dv)
            we.appendChild(dve)

        self.structure.appendChild(we)

    def writePhysicalVolume(self, pv):
        pvol = self.doc.createElement('physvol')
        pvol.setAttribute('name',"{}{}".format(self.prepend, pv.name))
        vr = self.doc.createElement('volumeref')
        vr.setAttribute('ref',"{}{}".format(self.prepend, pv.logicalVolume.name))
        pvol.appendChild(vr)

        self.writeVectorVariable(pvol, pv.position)
        self.writeVectorVariable(pvol, pv.rotation)
        self.writeVectorVariable(pvol, pv.scale)

        if pv.copyNumber != 0:
            pvol.setAttribute('copynumber', str(int(float(pv.copyNumber))))

        return pvol

    def writeReplicaVolume(self, instance):
        rvol = self.doc.createElement('replicavol')
        rvol.setAttribute('number', str(int(float(instance.nreplicas))))

        vr = self.doc.createElement('volumeref')
        vr.setAttribute('ref',"{}{}".format(self.prepend, instance.logicalVolume.name))
        rvol.appendChild(vr)

        ra = self.doc.createElement('replicate_along_axis')
        ax = self.doc.createElement('direction')
        axes = {1 : "x", 2 : "y",  3 : "z", 4 : "rho", 5 : "phi"}
        ax.setAttribute(axes[instance.axis], "1")
        ra.appendChild(ax)

        wd = self.doc.createElement('width')
        wd.setAttribute("value", str(float(instance.width)))
        if instance.wunit:
            wd.setAttribute("unit", instance.wunit)
        ra.appendChild(wd)

        of = self.doc.createElement('offset')
        of.setAttribute("value", str(float(instance.offset)))
        if instance.ounit:
            of.setAttribute("unit", instance.ounit)
        ra.appendChild(of)

        rvol.appendChild(ra)

        return rvol

    def writeDivisionVolume(self, instance):
        dvol = self.doc.createElement('divisionvol')
        dvol.setAttribute('number', str(int(float(instance.ndivisions))))
        axes = {1 : "kXAxis", 2 : "kYAxis",  3 : "kZAxis", 4 : "kRho", 5 : "kPhi"}
        dvol.setAttribute('axis', axes[instance.axis])
        dvol.setAttribute('width', str(float(instance.width)))
        dvol.setAttribute('offset',  str(float(instance.width)))
        if instance.unit:
            dvol.setAttribute('unit', instance.unit)

        vr = self.doc.createElement('volumeref')
        vr.setAttribute('ref',"{}{}".format(self.prepend, instance.logicalVolume.name))
        dvol.appendChild(vr)

        return dvol

    def writeParametrisedVolume(self, instance):
        pvol = self.doc.createElement('paramvol')
        pvol.setAttribute('ncopies', str(int(float(instance.ncopies))))

        vr = self.doc.createElement('volumeref')
        vr.setAttribute('ref',"{}{}".format(self.prepend, instance.logicalVolume.name))
        pvol.appendChild(vr)

        pos_size = self.doc.createElement('parameterised_position_size')
        for i in range(int(float(instance.ncopies))):
            param_node = self.doc.createElement('parameters')
            param_node.setAttribute('number', str(i+1)) # As zero-indexed in python

            tr = instance.transforms[i]
            self.writeVectorVariable(param_node, tr[1]) # Position
            self.writeVectorVariable(param_node, tr[0]) # Rotation

            params = instance.paramData[i]

            # Map the internal member names to variable names in the output
            if isinstance(params, _g4.ParameterisedVolume.BoxDimensions):
                dim_solid = "box"
                dim_names = { "pX" : "x",
                              "pY" : "y",
                              "pZ" : "z"}

            elif isinstance(params, _g4.ParameterisedVolume.TubeDimensions):
                dim_solid = "tube"
                dim_names = { "pRMin" : "InR",
                              "pRMax" : "OutR",
                              "pDz"   : "hz",
                              "pSPhi" : "StartPhi",
                              "pDPhi" : "DeltaPhi"}

            elif isinstance(params, _g4.ParameterisedVolume.ConeDimensions):
                dim_solid = "cone"
                dim_names = { "pRMin1" : "rmin1",
                              "pRMax1" : "rmax1",
                              "pRMin2" : "rmin2",
                              "pRMax2" : "rmax2",
                              "pDz"    : "z",
                              "pSPhi"  : "startphi",
                              "pDPhi"  : "deltaphi"}

            elif isinstance(params, _g4.ParameterisedVolume.OrbDimensions):
                dim_solid = "orb"
                dim_names = { "pRMax" : "r" }

            elif isinstance(params, _g4.ParameterisedVolume.SphereDimensions):
                dim_solid = "sphere"
                dim_names = { "pRMin": "rmin",
                              "pRMax": "rmax",
                              "pSPhi": "startphi",
                              "pDPhi": "deltaphi",
                              "pSTheta": "starttheta",
                              "pDTheta": "deltatheta",}

            elif isinstance(params, _g4.ParameterisedVolume.TorusDimensions):
                dim_solid = "torus"
                dim_names = { "pRMin": "rmin",
                              "pRMax": "rmax",
                              "pRTor": "rtor",
                              "pSPhi": "startphi",
                              "pDPhi": "deltaphi",}

            elif isinstance(params, _g4.ParameterisedVolume.HypeDimensions):
                dim_solid = "hype"
                dim_names = {"innerRadius": "rmin",
                             "outerRadius": "rmax",
                             "innerStereo": "inst",
                             "outerStereo": "outst",
                             "lenZ": "z",}

            elif isinstance(params, _g4.ParameterisedVolume.TrdDimensions):
                dim_solid = "trd"
                dim_names = {"pX1": "x1",
                             "pX2": "x2",
                             "pY1": "y1",
                             "pY2": "y2",
                             "pZ": "z",}

            elif isinstance(params, _g4.ParameterisedVolume.TrapDimensions):
                dim_solid = "trap"
                dim_names = {"pDz": "z",
                             "pTheta": "theta",
                             "pDPhi": "phi",
                             "pDy1": "y1",
                             "pDx1": "x1",
                             "pDx2": "x2",
                             "pAlp1": "alpha1",
                             "pDy2": "y2",
                             "pDx3": "x3",
                             "pDx4": "x4",
                             "pAlp2": "alpha2",}

            elif isinstance(params, _g4.ParameterisedVolume.ParaDimensions):
                dim_solid = "para"
                dim_names = {"pX": "x",
                             "pY": "y",
                             "pZ": "z",
                            "pAlpha": "alpha",
                             "pTheta": "theta",
                             "pPhi": "phi",}

            elif isinstance(params, _g4.ParameterisedVolume.EllipsoidDimensions):
                dim_solid = "ellipsoid"
                dim_names = {"pxSemiAxis": "ax",
                             "pySemiAxis": "by",
                             "pzSemiAxis": "cz",
                             "pzBottomCut": "zcut1",
                             "pzTopCut": "zcut2",}

            elif isinstance(params, _g4.ParameterisedVolume.PolyconeDimensions):
                dim_solid = "polycone"
                dim_names = {"pSPhi": "startPhi",
                             "pDPhi": "openPhi",}

            elif isinstance(params, _g4.ParameterisedVolume.PolyhedraDimensions):
                dim_solid = "polyhedra"
                dim_names = {"pSPhi": "startPhi",
                             "pDPhi": "openPhi",
                             "numSide" : "numSide",}

            dim = self.doc.createElement('{}_dimensions'.format(dim_solid))
            for name in dim_names:
                dim.setAttribute(dim_names[name], self.getValueOrExprFromInstance(params,name))
            for unit in ["lunit", "aunit"]:
                if hasattr(params, unit):
                    dim.setAttribute(unit, getattr(params, unit))

            # Special handling of polysolids
            if dim_solid in ["polycone", "polyhedra"]:
                z_planes = list(zip(params.pZpl, params.pRMin, params.pRMax))
                dim.setAttribute("numRZ", str(len(z_planes)))
                for pl in z_planes:
                    zpl = self.doc.createElement('zplane')
                    zpl.setAttribute("z",    self.getValueOrExpr(pl[0]))
                    zpl.setAttribute("rmin", self.getValueOrExpr(pl[1]))
                    zpl.setAttribute("rmax", self.getValueOrExpr(pl[2]))
                    dim.appendChild(zpl)

            param_node.appendChild(dim)
            pos_size.appendChild(param_node)

        pvol.appendChild(pos_size)

        return pvol

    def writeSkinSurface(self, instance):
        surf = self.doc.createElement('skinsurface')
        surf.setAttribute('name', "{}{}".format(self.prepend, instance.name))
        surf.setAttribute('surfaceproperty', instance.surface_property.name)

        vr = self.doc.createElement('volumeref')
        vr.setAttribute('ref',"{}{}".format(self.prepend, instance.volumeref.name))
        surf.appendChild(vr)

        self.structure.appendChild(surf)

    def writeBorderSurface(self, instance):
        surf = self.doc.createElement('bordersurface')
        surf.setAttribute('name', "{}{}".format(self.prepend, instance.name))
        surf.setAttribute('surfaceproperty', instance.surface_property.name)

        pvr1 = self.doc.createElement('physvolref')
        pvr1.setAttribute('ref',"{}{}".format(self.prepend, instance.physref1.name))
        surf.appendChild(pvr1)
        pvr2 = self.doc.createElement('physvolref')
        pvr2.setAttribute('ref',"{}{}".format(self.prepend, instance.physref2.name))
        surf.appendChild(pvr2)

        self.structure.appendChild(surf)


    def writeSolid(self, solid):
        """
        Dispatch to correct member function based on type string in SolidBase.
        """
        if solid.name in self.solids_written:
            return # Do nothing if written already

        if hasattr(self, 'write'+solid.type):
            func = getattr(self, 'write'+solid.type) # get the member function
            func(solid) # call it with the solid instance as an argument
            self.solids_written.append(solid.name)
        else:
            raise ValueError("No such solid "+solid.type)

    # TODO got to be removed
    def getValueOrExpr(self, var) :
        # pyg4ometry expression (evaluatable string)
        if isinstance(var, _Expression):
            return str(var.expression)

        # Expression, Constant, Quantity or Variable
        elif isinstance(var, _Defines.Expression) or isinstance(var, _Defines.Constant) or isinstance(var, _Defines.Quantity) or isinstance(var, _Defines.Variable):
            if var.name in self.registry.defineDict:
                return var.name
            else :
                return str(var.expr.expression)
        else:
            return str(var)

    def getValueOrExprFromInstance(self, instance, variable, index=None):

        if not hasattr(instance, variable):
            raise AttributeError("") #TODO: Add error message

        # Indexed variable 
        if index is not None:
            try:
                var = getattr(instance,variable)[index]
            except IndexError:
                raise IndexError("") #TODO: Add error message

        else:
            var = getattr(instance, variable)

        return self.getValueOrExpr(var)

    def writeBox(self, instance):
        oe = self.doc.createElement('box')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('x',self.getValueOrExprFromInstance(instance,'pX'))
        oe.setAttribute('y',self.getValueOrExprFromInstance(instance,'pY'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pZ'))
        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def writeCons(self, instance):
        oe = self.doc.createElement('cone')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rmin1', self.getValueOrExprFromInstance(instance,'pRmin1'))
        oe.setAttribute('rmax1', self.getValueOrExprFromInstance(instance,'pRmax1'))
        oe.setAttribute('rmin2', self.getValueOrExprFromInstance(instance,'pRmin2'))
        oe.setAttribute('rmax2', self.getValueOrExprFromInstance(instance,'pRmax2'))
        oe.setAttribute('z', self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute('startphi', self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi', self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)
        self.solids.appendChild(oe)

    def writeCutTubs(self, instance):
        oe = self.doc.createElement('cutTube')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('z', self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute('rmin', self.getValueOrExprFromInstance(instance,'pRMin'))
        oe.setAttribute('rmax', self.getValueOrExprFromInstance(instance,'pRMax'))
        oe.setAttribute('startphi', self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi', self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('lowX', self.getValueOrExprFromInstance(instance,'pLowNorm',0))
        oe.setAttribute('lowY', self.getValueOrExprFromInstance(instance,'pLowNorm',1))
        oe.setAttribute('lowZ', self.getValueOrExprFromInstance(instance,'pLowNorm',2))
        oe.setAttribute('highX', self.getValueOrExprFromInstance(instance,'pHighNorm',0))
        oe.setAttribute('highY', self.getValueOrExprFromInstance(instance,'pHighNorm',1))
        oe.setAttribute('highZ', self.getValueOrExprFromInstance(instance,'pHighNorm',2))
        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)
        self.solids.appendChild(oe)

    def writeEllipsoid(self, instance):
        oe = self.doc.createElement('ellipsoid')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('ax', self.getValueOrExprFromInstance(instance,'pxSemiAxis'))
        oe.setAttribute('by', self.getValueOrExprFromInstance(instance,'pySemiAxis'))
        oe.setAttribute('cz', self.getValueOrExprFromInstance(instance,'pzSemiAxis'))
        oe.setAttribute('zcut1', self.getValueOrExprFromInstance(instance,'pzBottomCut'))
        oe.setAttribute('zcut2', self.getValueOrExprFromInstance(instance,'pzTopCut'))
        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def writeEllipticalCone(self, instance):
        oe = self.doc.createElement('elcone')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('dx', self.getValueOrExprFromInstance(instance,'pxSemiAxis'))
        oe.setAttribute('dy', self.getValueOrExprFromInstance(instance,'pySemiAxis'))
        oe.setAttribute('zmax', self.getValueOrExprFromInstance(instance,'zMax'))
        oe.setAttribute('zcut', self.getValueOrExprFromInstance(instance,'pzTopCut'))
        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def writeEllipticalTube(self, instance):
        oe = self.doc.createElement('eltube')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('dx', self.getValueOrExprFromInstance(instance,'pDx'))
        oe.setAttribute('dy', self.getValueOrExprFromInstance(instance,'pDy'))
        oe.setAttribute('dz', self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def createTwoDimVertex(self, x, y):
        td = self.doc.createElement('twoDimVertex')
        td.setAttribute('x', self.getValueOrExpr(x))
        td.setAttribute('y', self.getValueOrExpr(y))
        return td

    def createSection(self, zOrder, zPosition, xOffset, yOffset, scalingFactor):
        s = self.doc.createElement('section')

        s.setAttribute('zOrder', str(zOrder))
        s.setAttribute('zPosition', self.getValueOrExpr(zPosition))
        s.setAttribute('xOffset', self.getValueOrExpr(xOffset))
        s.setAttribute('yOffset', self.getValueOrExpr(yOffset))
        s.setAttribute('scalingFactor', self.getValueOrExpr(scalingFactor))

        return s

    def writeExtrudedSolid(self, instance):
        oe = self.doc.createElement('xtru')
        oe.setAttribute('name', self.prepend + instance.name)

        for vertex in instance.pPolygon:
            v = self.createTwoDimVertex(vertex[0], vertex[1])
            oe.appendChild(v)

        n = 0
        for zs in instance.pZslices : 
            z = zs[0]
            x = zs[1][0]
            y = zs[1][1]
            s = zs[2]
            sec = self.createSection(n, z, x, y, s)
            oe.appendChild(sec)            
            n += 1

        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def createrzPoint(self, r, z):
        rz = self.doc.createElement('rzpoint')
 
        rz.setAttribute('r',self.getValueOrExpr(r))
        rz.setAttribute('z', self.getValueOrExpr(z)) 

        return rz

    def writeGenericPolycone(self, instance):
        oe = self.doc.createElement('genericPolycone')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('startphi', self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi', self.getValueOrExprFromInstance(instance,'pDPhi')) 

        for r,z in zip(instance.pR, instance.pZ):
            p = self.createrzPoint(r, z)
            oe.appendChild(p)

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)
        self.solids.appendChild(oe)

    def writeGenericPolyhedra(self, instance) : 
        oe = self.doc.createElement('genericPolyhedra')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('startphi', self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi', self.getValueOrExprFromInstance(instance,'pDPhi')) 
        oe.setAttribute('numsides', self.getValueOrExprFromInstance(instance,'numSide')) 

        for r,z in zip(instance.pR, instance.pZ):
            p = self.createrzPoint(r, z)
            oe.appendChild(p)

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)
        self.solids.appendChild(oe)


    def createTriangularFacet(self, vertex1, vertex2, vertex3):
        tf = self.doc.createElement('triangular')
        tf.setAttribute('vertex1', str(vertex1))
        tf.setAttribute('vertex2', str(vertex2))
        tf.setAttribute('vertex3', str(vertex3))
        tf.setAttribute('type', 'ABSOLUTE')
        return tf

    def createQuadrangularFacet(self, vertex1, vertex2, vertex3, vertex4):
        qf = self.doc.createElement('quadrangular')
        qf.setAttribute('vertex1', str(vertex1))
        qf.setAttribute('vertex2', str(vertex2))
        qf.setAttribute('vertex3', str(vertex3))
        qf.setAttribute('vertex4', str(vertex4))
        qf.setAttribute('type', 'ABSOLUTE')
        return qf

    def writeTessellatedSolid(self, instance):
        oe = self.doc.createElement('tessellated')
        name     = instance.name
        oe.setAttribute('name', self.prepend + name)

        facet_makers = {3: self.createTriangularFacet,
                        4: self.createQuadrangularFacet}
        if instance.meshtype == instance.MeshType.Gdml:
            for f in instance.meshtess:
                oe.appendChild(facet_makers[len(f)](*f))

        elif instance.meshtype == instance.MeshType.Freecad:
            verts = instance.meshtess[0]
            facet = instance.meshtess[1]

            vert_names = []
            for vertex_id, v in enumerate(verts) :
                defname = "{}_{}".format(name, vertex_id)
                vert_names.append(defname)

                self.writeDefine(_Defines.Position(defname, v[0],v[1],v[2]))

            for f in facet :
                oe.appendChild(facet_makers[len(f)](*[vert_names[fi] for fi in f]))
                # oe.appendChild(self.createTriangularFacet(vert_names[f[0]],
                #                                           vert_names[f[1]],
                #                                           vert_names[f[2]]))
        else:
            facet = instance.meshtess

            for facet_id, f in enumerate(facet) :
                vertex_names = []
                for vertex_id, v in enumerate(f[0]):
                    defname = "{}_f{}_v{}".format(name, facet_id, vertex_id)
                    vertex_names.append(defname)
                    self.writeDefine(_Defines.Position(defname, v[0],v[1],v[2]))

                oe.appendChild(self.createTriangularFacet(vertex_names[0],
                                                          vertex_names[1],
                                                          vertex_names[2]))

        self.solids.appendChild(oe)

    def writeHype(self, instance):
        oe = self.doc.createElement('hype')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rmin', self.getValueOrExprFromInstance(instance,'innerRadius'))
        oe.setAttribute('rmax', self.getValueOrExprFromInstance(instance,'outerRadius'))
        oe.setAttribute('z',    self.getValueOrExprFromInstance(instance,'lenZ'))
        oe.setAttribute('inst', self.getValueOrExprFromInstance(instance,'innerStereo'))
        oe.setAttribute('outst', self.getValueOrExprFromInstance(instance,'outerStereo'))
        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)
        self.solids.appendChild(oe)

    def writeIntersection(self, instance):
        oe  = self.doc.createElement('intersection')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2name)
        oe.appendChild(cse)

        p = self.doc.createElement('position')
        p.setAttribute('name',self.prepend + instance.name+'_'+'position')
        p.setAttribute('x',str(instance.tra2[1].x.expression))
        p.setAttribute('y',str(instance.tra2[1].y.expression))
        p.setAttribute('z',str(instance.tra2[1].z.expression))
        self.defines.appendChild(p)

        r = self.doc.createElement('rotation')
        r.setAttribute('name',self.prepend + instance.name+'_'+'rotation')
        r.setAttribute('x', str(instance.tra2[0].x.expression))
        r.setAttribute('y', str(instance.tra2[0].y.expression))
        r.setAttribute('z', str(instance.tra2[0].z.expression))
        self.defines.appendChild(r)


        csce = self.doc.createElement('positionref')
        csce.setAttribute('ref',self.prepend + instance.name+'_'+'position')
        oe.appendChild(csce)

        csce1 = self.doc.createElement('rotationref')
        csce1.setAttribute('ref',self.prepend + instance.name+'_'+'rotation')
        oe.appendChild(csce1)

        self.solids.appendChild(oe)

    def writeOpticalSurface(self, instance):
        oe = self.doc.createElement('opticalsurface')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('model', instance.model)
        oe.setAttribute('finish', instance.finish)
        oe.setAttribute('type', instance.osType)
        oe.setAttribute('value', str(float(instance.value)))
        self.solids.appendChild(oe)

        self.writeMaterialProps(instance, oe)

    def writeOrb(self, instance):
        oe = self.doc.createElement('orb')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('r', self.getValueOrExprFromInstance(instance,'pRMax'))
        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def writePara(self, instance):
        oe = self.doc.createElement('para')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('x', self.getValueOrExprFromInstance(instance,'pX'))
        oe.setAttribute('y', self.getValueOrExprFromInstance(instance,'pY'))
        oe.setAttribute('z', self.getValueOrExprFromInstance(instance,'pZ'))
        oe.setAttribute('alpha', self.getValueOrExprFromInstance(instance,'pAlpha'))
        oe.setAttribute('theta', self.getValueOrExprFromInstance(instance,'pTheta'))
        oe.setAttribute('phi', self.getValueOrExprFromInstance(instance,'pPhi'))
        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)
        self.solids.appendChild(oe)

    def writeParaboloid(self, instance):
        oe = self.doc.createElement('paraboloid')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rlo', self.getValueOrExprFromInstance(instance,'pR1'))
        oe.setAttribute('rhi', self.getValueOrExprFromInstance(instance,'pR2'))
        oe.setAttribute('dz', self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def createzPlane(self, rInner, rOuter, zplane):
        d = self.doc.createElement('zplane')               
        
        d.setAttribute('rmin',self.getValueOrExpr(rInner))
        d.setAttribute('rmax',self.getValueOrExpr(rOuter))
        d.setAttribute('z', self.getValueOrExpr(zplane)) 

        # d.setAttribute('rmin',str(rInner.expr.expression))
        # d.setAttribute('rmax', str(rOuter.expr.expression))
        # d.setAttribute('z', str(zplane.expr.expression))
        
        return d

    def writePolycone(self, instance):
        oe = self.doc.createElement('polycone')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))

        i = instance
        for w,x,y in zip(i.pRMin, i.pRMax, i.pZpl):
            d = self.createzPlane(w,x,y)
            oe.appendChild(d)

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writePolyhedra(self, instance):
        oe = self.doc.createElement('polyhedra')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('numsides',self.getValueOrExprFromInstance(instance,'numSide'))

        i = instance
        for w,x,y in zip(i.rInner, i.rOuter, i.zPlane):
            d = self.createzPlane(w,x,y)
            oe.appendChild(d)

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeSphere(self, instance):
        oe = self.doc.createElement('sphere')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rmin',self.getValueOrExprFromInstance(instance,'pRmin'))
        oe.setAttribute('rmax',self.getValueOrExprFromInstance(instance,'pRmax'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('starttheta',self.getValueOrExprFromInstance(instance,'pSTheta'))
        oe.setAttribute('deltatheta',self.getValueOrExprFromInstance(instance,'pDTheta'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeGenericTrap(self, instance):
        oe = self.doc.createElement('arb8')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('v1x',self.getValueOrExprFromInstance(instance,'v1x'))
        oe.setAttribute('v1y',self.getValueOrExprFromInstance(instance,'v1y'))
        oe.setAttribute('v2x',self.getValueOrExprFromInstance(instance,'v2x'))
        oe.setAttribute('v2y',self.getValueOrExprFromInstance(instance,'v2y'))
        oe.setAttribute('v3x',self.getValueOrExprFromInstance(instance,'v3x'))
        oe.setAttribute('v3y',self.getValueOrExprFromInstance(instance,'v3y'))
        oe.setAttribute('v4x',self.getValueOrExprFromInstance(instance,'v4x'))
        oe.setAttribute('v4y',self.getValueOrExprFromInstance(instance,'v4y'))
        oe.setAttribute('v5x',self.getValueOrExprFromInstance(instance,'v5x'))
        oe.setAttribute('v5y',self.getValueOrExprFromInstance(instance,'v5y'))
        oe.setAttribute('v6x',self.getValueOrExprFromInstance(instance,'v6x'))
        oe.setAttribute('v6y',self.getValueOrExprFromInstance(instance,'v6y'))
        oe.setAttribute('v7x',self.getValueOrExprFromInstance(instance,'v7x'))
        oe.setAttribute('v7y',self.getValueOrExprFromInstance(instance,'v7y'))
        oe.setAttribute('v8x',self.getValueOrExprFromInstance(instance,'v8x'))
        oe.setAttribute('v8y',self.getValueOrExprFromInstance(instance,'v8y'))
        oe.setAttribute('dz',self.getValueOrExprFromInstance(instance,'dz'))

        oe.setAttribute("lunit",instance.lunit)

        self.solids.appendChild(oe)
        
    def createPosition(self,name, x, y, z):
        p = self.doc.createElement('position')
        p.setAttribute('name',str(name))
        p.setAttribute('x', x.expression)
        p.setAttribute('y', y.expression)
        p.setAttribute('z', z.expression)
        return p

    def writeTet(self, instance):
        j = instance
        oe = self.doc.createElement('tet')
        uniqueName = self.prepend + instance.name
        oe.setAttribute('name', uniqueName)
        v1 = self.createPosition(uniqueName + '_v1', j.anchor[0], j.anchor[1], j.anchor[2])
        self.defines.appendChild(v1)
        v2 = self.createPosition(uniqueName + '_v2', j.p2[0], j.p2[1], j.p2[2])
        self.defines.appendChild(v2)
        v3 = self.createPosition(uniqueName + '_v3', j.p3[0], j.p3[1], j.p3[2])
        self.defines.appendChild(v3)
        v4 = self.createPosition(uniqueName + '_v4', j.p4[0], j.p4[1], j.p4[2])
        self.defines.appendChild(v4)
        oe.setAttribute('vertex1', uniqueName + '_v1')
        oe.setAttribute('vertex2', uniqueName + '_v2')
        oe.setAttribute('vertex3', uniqueName + '_v3')
        oe.setAttribute('vertex4', uniqueName + '_v4')

        oe.setAttribute("lunit",instance.lunit)
        self.solids.appendChild(oe)

    def writeTorus(self, instance):
        oe = self.doc.createElement('torus')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rmin',self.getValueOrExprFromInstance(instance,'pRmin'))
        oe.setAttribute('rmax',self.getValueOrExprFromInstance(instance,'pRmax'))
        oe.setAttribute('rtor',self.getValueOrExprFromInstance(instance,'pRtor'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeTrap(self, instance):
        oe = self.doc.createElement('trap')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute('theta',self.getValueOrExprFromInstance(instance,'pTheta'))
        oe.setAttribute('phi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('y1',self.getValueOrExprFromInstance(instance,'pDy1'))
        oe.setAttribute('x1',self.getValueOrExprFromInstance(instance,'pDx1'))
        oe.setAttribute('x2',self.getValueOrExprFromInstance(instance,'pDx2'))
        oe.setAttribute('alpha1',self.getValueOrExprFromInstance(instance,'pAlp1'))
        oe.setAttribute('y2',self.getValueOrExprFromInstance(instance,'pDy2'))
        oe.setAttribute('x3',self.getValueOrExprFromInstance(instance,'pDx3'))
        oe.setAttribute('x4',self.getValueOrExprFromInstance(instance,'pDx4'))
        oe.setAttribute('alpha2',self.getValueOrExprFromInstance(instance,'pAlp2'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeTrd(self, instance):
        oe = self.doc.createElement("trd")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('x1',self.getValueOrExprFromInstance(instance,'pX1'))
        oe.setAttribute('x2',self.getValueOrExprFromInstance(instance,'pX2'))
        oe.setAttribute('y1',self.getValueOrExprFromInstance(instance,'pY1'))
        oe.setAttribute('y2',self.getValueOrExprFromInstance(instance,'pY2'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pZ'))

        oe.setAttribute("lunit",instance.lunit)

        self.solids.appendChild(oe)

    def writeTubs(self, instance):
        oe = self.doc.createElement("tube")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('rmin',self.getValueOrExprFromInstance(instance,'pRMin'))
        oe.setAttribute('rmax',self.getValueOrExprFromInstance(instance,'pRMax'))
        oe.setAttribute('z',   self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeTwistedBox(self, instance):
        oe = self.doc.createElement("twistedbox")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('PhiTwist', self.getValueOrExprFromInstance(instance,'twistedAngle'))
        oe.setAttribute('x',self.getValueOrExprFromInstance(instance,'pDx'))
        oe.setAttribute('y',self.getValueOrExprFromInstance(instance,'pDy'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pDz'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeTwistedTrd(self, instance):
        oe = self.doc.createElement("twistedtrd")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('PhiTwist',self.getValueOrExprFromInstance(instance,'twistedAngle'))
        oe.setAttribute('x1','2*'+ self.getValueOrExprFromInstance(instance,'pDx1'))
        oe.setAttribute('x2','2*'+ self.getValueOrExprFromInstance(instance,'pDx2'))
        oe.setAttribute('y1','2*'+ self.getValueOrExprFromInstance(instance,'pDy1'))
        oe.setAttribute('y2','2*'+ self.getValueOrExprFromInstance(instance,'pDy2'))
        oe.setAttribute('z','2*'+ self.getValueOrExprFromInstance(instance,'pDz'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)

    def writeTwistedTrap(self, instance):
        oe = self.doc.createElement("twistedtrap")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('PhiTwist',self.getValueOrExprFromInstance(instance,'twistedAngle'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute('Theta',self.getValueOrExprFromInstance(instance,'pTheta'))
        oe.setAttribute('Phi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('y1',self.getValueOrExprFromInstance(instance,'pDy1'))
        oe.setAttribute('x1',self.getValueOrExprFromInstance(instance,'pDx1'))
        oe.setAttribute('x2',self.getValueOrExprFromInstance(instance,'pDx2'))
        oe.setAttribute('y2',self.getValueOrExprFromInstance(instance,'pDy2'))
        oe.setAttribute('x3',self.getValueOrExprFromInstance(instance,'pDx3'))
        oe.setAttribute('x4',self.getValueOrExprFromInstance(instance,'pDx4'))
        oe.setAttribute('Alph',self.getValueOrExprFromInstance(instance,'pAlp'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)
        
    def writeTwistedTubs(self, instance):
        oe = self.doc.createElement("twistedtubs")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('endinnerrad',self.getValueOrExprFromInstance(instance,'endinnerrad'))
        oe.setAttribute('endouterrad',self.getValueOrExprFromInstance(instance,'endouterrad'))
        oe.setAttribute('zlen',self.getValueOrExprFromInstance(instance,'zlen'))
        oe.setAttribute('phi',self.getValueOrExprFromInstance(instance,'phi'))
        oe.setAttribute('twistedangle',self.getValueOrExprFromInstance(instance,'twistedangle'))

        oe.setAttribute("lunit",instance.lunit)
        oe.setAttribute("aunit",instance.aunit)

        self.solids.appendChild(oe)    

    def writeUnion(self, instance):
        self.writeSolid(instance.obj1) # Make sure the solids are written first
        self.writeSolid(instance.obj2)

        oe  = self.doc.createElement('union')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1.name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2.name)
        oe.appendChild(cse)

        instance.tra2[0].name = self.prepend + instance.name + "_rotation"
        instance.tra2[1].name = self.prepend + instance.name + "_translation"
        self.writeVectorVariable(oe, instance.tra2[1]) #position
        self.writeVectorVariable(oe, instance.tra2[0]) #rotation

        self.solids.appendChild(oe)

    def writeSubtraction(self, instance):
        self.writeSolid(instance.obj1) # Make sure the solids are written first
        self.writeSolid(instance.obj2)

        oe  = self.doc.createElement('subtraction')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1.name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2.name)
        oe.appendChild(cse)

        instance.tra2[0].name = self.prepend + instance.name + "_rotation"
        instance.tra2[1].name = self.prepend + instance.name + "_translation"
        self.writeVectorVariable(oe, instance.tra2[1]) # Position
        self.writeVectorVariable(oe, instance.tra2[0]) # Rotation

        self.solids.appendChild(oe)

    def writeIntersection(self, instance):
        self.writeSolid(instance.obj1) # Make sure the solids are written first
        self.writeSolid(instance.obj2)

        oe  = self.doc.createElement('intersection')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1.name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2.name)
        oe.appendChild(cse)

        instance.tra2[0].name = self.prepend + instance.name + "_rotation"
        instance.tra2[1].name = self.prepend + instance.name + "_translation"
        self.writeVectorVariable(oe, instance.tra2[1]) # Position
        self.writeVectorVariable(oe, instance.tra2[0]) # Rotation

        self.solids.appendChild(oe)

    def writeMultiUnion(self, instance) :
        for obj in instance.objects:
            self.writeSolid(obj) # Make sure the solids are written first

        oe  = self.doc.createElement('multiUnion')
        oe.setAttribute('name',self.prepend + instance.name)        

        # loop over objects
        for i, (solid, trans) in enumerate(zip(instance.objects,
                                               instance.transformations),
                                           start=1):
            ce = self.doc.createElement("multiUnionNode")
            nodename = f"{self.prepend}{instance.name}-node-{i}"
            ce.setAttribute("name", nodename)

            cse = self.doc.createElement("solid")
            cse.setAttribute("ref", solid.name)
            ce.appendChild(cse)

            position = trans[1]
            rotation = trans[0]
            positionElement = self.writeVectorVariable(ce, position) # position
            rotationElement = self.writeVectorVariable(ce, rotation) # rotation

            # her we provide default names if are none provided to satify
            # the GDML schema which silences warnings in Geant4.
            positionName = position.name
            if positionElement and not position.name:
                positionName = f"{nodename}-position"
                positionElement.setAttribute("name", positionName)
            rotationName = rotation.name
            if rotationElement and not rotation.name:
                rotationName = f"{nodename}-rotation"
                rotationElement.setAttribute("name", rotationName)

            oe.appendChild(ce)

        self.solids.appendChild(oe)

    def writeScaled(self, instance) :
        oe  = self.doc.createElement('scaledSolid')
        oe.setAttribute('name',self.prepend + instance.name)

        srf = self.doc.createElement('solidref')
        srf.setAttribute('ref', instance.solid.name)
        oe.appendChild(srf)

        scl = self.doc.createElement('scale')

        scl.setAttribute('x',self.getValueOrExprFromInstance(instance,'pX'))
        scl.setAttribute('y',self.getValueOrExprFromInstance(instance,'pY'))
        scl.setAttribute('z',self.getValueOrExprFromInstance(instance,'pZ'))

        oe.appendChild(scl)

        self.solids.appendChild(oe)
