from collections import defaultdict      as _defaultdict
import re                                as _re
from   xml.dom import minidom            as _minidom
import xml.parsers.expat                 as _expat
from . import Defines                    as _defines
import logging                           as _log
import pyg4ometry.geant4                          as _g4

class Reader(object):
    def __init__(self, fileName, registryOn = True):
        super(Reader, self).__init__()
        self.filename   = fileName    
        self.registryOn = registryOn    

        if self.registryOn : 
            self._registry = _g4.Registry()

        self._physVolumeNameCount = _defaultdict(int)
        
        # load file
        self.load()

    def load(self):
        _log.info('Reader.load>')
        self._physVolumeNameCount.clear()

        # open file 
        data  = open(self.filename)

        # Render out the ENTITY includes
        # Only look at the starting block - no need to iterate over the whole file
        start_block = ""
        for line in data:
            if line.startswith("<gdml"):
                break
            start_block += line
        data.seek(0) # Reset the file iterator

        # Extract the information from entities and store in a dict
        entities = {}
        en_block = _re.search('<!DOCTYPE(\s+)gdml([\s\S]*)>', start_block)

        try:
            ents = en_block.group(0).split("<")
        except AttributeError: # No entities
            ents = []

        for en in ents:
            if "ENTITY" in en:
                name =  en.split()[1]
                filename = _re.search(r'[^\"]+', " ".join(en.split()[3:])).group(0)
                with open(filename, 'r') as content_file:
                    #ensure the contents are properly prepared for parsing
                    contents = str()
                    for l in content_file:
                        l = l.strip()
                        if(l.endswith(">")):
                            end=""
                        else:
                            end=" "
                        if(len(l) != 0):
                            contents += (l+end)
                entities[name] = (filename, contents)

        #remove all newline charecters and whitespaces outside tags
        fs = str()
        for l in data:
            l = l.strip()
            # Render out entities in those lines
            if l.startswith("&"):
                name =  _re.search(r'&([\s\S]+)\;', l).group(1)
                fs += entities[name][1]
                continue

            if(l.endswith(">")):
                end=""
            else:
                end=" "
            if(len(l) != 0):
                fs += (l+end)

        # parse xml
        _log.info('Reader.load> minidom parse')
        try :
            xmldoc = _minidom.parseString(fs)
        except _expat.ExpatError as ee : 
            print(ee.args)
            print(ee.args[0])
            column = int(ee.args[0].split()[-1])
            print(column,fs[column-10:min(len(fs),column+100)])
            print("        ^^^^ ")
            raise _expat.ExpatError()
        _log.info('Reader.load> parse')

        # parse xml for defines, materials, solids and structure (#TODO optical surfaces?)
        self.parseDefines(xmldoc)
        self.parseMaterials(xmldoc)
        self.parseSolids(xmldoc)
        self.parseStructure(xmldoc)
        self.parseUserInfo(xmldoc)

        data.close()

    def getRegistry(self) : 
        return self._registry

    def parseDefines(self, xmldoc) : 
        self.xmldefines = xmldoc.getElementsByTagName("define")[0]

        for df in self.xmldefines.childNodes :
            try :
                define_type  = df.tagName
            except AttributeError :
                # comment so continue
                continue

            name         = df.attributes["name"].value
            attrs        = df.attributes

            keys       = attrs.keys()
            vals       = [attr.value for attr in attrs.values()]
            def_attrs  = {key: val for (key,val) in zip(keys, vals)}

            # parse positions and rotations
            def getXYZ(def_attrs) :
                x = def_attrs.get("x", "0.0")
                y = def_attrs.get("y", "0.0")
                z = def_attrs.get("z", "0.0")
                u = def_attrs.get("unit", None)
                return (x,y,z,u)

            # parse matricies
            def getMatrix(def_attrs) :
                try : 
                    coldim = def_attrs['coldim']
                except KeyError : 
                    coldim = 0

                #                try : 
                values = def_attrs['values'].split()
                #               except KeyError : 
                #                   values = []
                
                return (coldim, values)

            if(define_type == "constant"):
                value = def_attrs['value']
                _defines.Constant(name, value, self._registry)
            elif(define_type == "quantity"):
                value = def_attrs['value']
                unit  = def_attrs['unit']
                qtype  = def_attrs['type']
                _defines.Quantity(name, value, unit, qtype, self._registry)
            elif(define_type == "variable"):
                value = def_attrs['value']
                _defines.Variable(name, value, self._registry)
            elif(define_type == "expression"):
                value = df.childNodes[0].nodeValue
                _defines.Expression(name, value, self._registry, True)
            elif(define_type == "position"):
                (x,y,z,u) = getXYZ(def_attrs)
                unit = u if u else "mm"
                _defines.Position(name, x, y, z, unit, self._registry)
            elif(define_type == "rotation"):
                (x,y,z,u) = getXYZ(def_attrs)
                unit = u if u else "rad"
                _defines.Rotation(name, x, y, z, unit, self._registry)
            elif(define_type == "scale"):
                (x,y,z,u) = getXYZ(def_attrs)
                unit = u if u else "none"
                _defines.Scale(name, x, y, z, unit, self._registry)
            elif(define_type == "matrix"):
                (coldim, values) = getMatrix(def_attrs)
                _defines.Matrix(name,coldim,values, self._registry)
            else:
                print("Warning : unrecognised define: ", define_type)

    def parseVector(self, node, type = "position", addRegistry=True) : 
        try : 
             name = node.attributes['name'].value 
        except KeyError : 
            name = '' 
        try :
            x    = node.attributes['x'].value
        except KeyError :
            x    = '0'
        try :
            y    = node.attributes['y'].value
        except KeyError :
            y    = '0'
        try :
            z    = node.attributes['z'].value
        except KeyError :
            z    = '0'
        try : 
            unit = node.attributes['unit'].value
        except KeyError : 
            unit = None
        
        if type == 'position':
            u = unit if unit else "mm"
            return _defines.Position(name,x,y,z,u,self._registry,addRegistry) 
        elif type == 'positionref':
            return self._registry.defineDict[node.attributes['ref'].value]
        elif type == 'rotation':
            u = unit if unit else "rad"
            return _defines.Rotation(name,x,y,z,u,self._registry,addRegistry)
        elif type == 'rotationref':
            return self._registry.defineDict[node.attributes['ref'].value]
        elif type == 'scale':
            u = unit if unit else "none"
            return _defines.Scale(name,x,y,z,u,self._registry,addRegistry)
        elif type == 'scaleref':
            return self._registry.defineDict[node.attributes['ref'].value]

        #    def parseMatrix(self, node) : 
        #        pass

    def parseMaterials(self, xmldoc):
        materials = []
        elements  = []
        isotopes  = []

        self.materialdef = xmldoc.getElementsByTagName("materials")[0]

        for node in self.materialdef.childNodes :
            if node.nodeType != node.ELEMENT_NODE:
                # probably a comment node, skip
                continue

            mat_type  = node.tagName

            name   = node.attributes["name"].value
            attrs  = node.attributes

            keys       = attrs.keys()
            vals       = [attr.value for attr in attrs.values()]
            def_attrs  = {key: val for (key,val) in zip(keys, vals)}

            if mat_type == "isotope":
                for chNode in node.childNodes:
                    if chNode.nodeType != chNode.ELEMENT_NODE:
                        continue # comment

                    if chNode.tagName=="atom":
                        def_attrs["a"] = chNode.attributes["value"].value

                isotopes.append(def_attrs)

            elif mat_type == "element":
                components = []
                for chNode in node.childNodes:
                    if chNode.nodeType != chNode.ELEMENT_NODE:
                        continue # comment

                    if chNode.tagName == "atom":
                        def_attrs["a"] = chNode.attributes["value"].value

                    elif chNode.tagName == "fraction":
                        keys = chNode.attributes.keys()
                        vals = [attr.value for attr in chNode.attributes.values()]
                        comp = {key: val for (key,val) in zip(keys, vals)}
                        comp["comp_type"] = "fraction"
                        components.append(comp)

                def_attrs["components"] = components
                elements.append(def_attrs)

            elif mat_type == "material":
                components = []
                properties = {}

                try :
                    state = node.attributes["state"].value
                except :
                    state = None
                for chNode in node.childNodes:
                    if chNode.nodeType != chNode.ELEMENT_NODE:
                        continue # comment

                    if chNode.tagName == "D":
                        def_attrs["density"] = chNode.attributes["value"].value

                    elif chNode.tagName == "T":
                        def_attrs["temperature"] = chNode.attributes["value"].value
                        try:
                            def_attrs["temperature_unit"] = chNode.attributes["unit"].value
                        except KeyError:
                            def_attrs["temperature_unit"] = "K"

                    elif chNode.tagName == "P":
                        def_attrs["pressure"] = chNode.attributes["value"].value
                        try:
                            def_attrs["pressure_unit"] = chNode.attributes["unit"].value
                        except KeyError:
                            def_attrs["pressure_unit"] = "pascal"

                    elif chNode.tagName == "atom":
                        def_attrs["a"] = chNode.attributes["value"].value

                    elif chNode.tagName == "composite":
                        keys = chNode.attributes.keys()
                        vals = [attr.value for attr in chNode.attributes.values()]
                        comp = {key: val for (key,val) in zip(keys, vals)}
                        comp["comp_type"] = "composite"
                        components.append(comp)

                    elif chNode.tagName == "fraction":
                        keys = chNode.attributes.keys()
                        vals = [attr.value for attr in chNode.attributes.values()]
                        comp = {key: val for (key,val) in zip(keys, vals)}
                        comp["comp_type"] = "fraction"
                        components.append(comp)

                    elif chNode.tagName=="property":
                        try :
                            properties[chNode.attributes["name"].value] = chNode.attributes["value"].value
                        except KeyError :
                            pass

                        try :
                            properties[chNode.attributes["name"].value] = chNode.attributes["ref"].value
                        except KeyError :
                            pass

                def_attrs["components"] = components
                def_attrs["properties"] = properties
                materials.append(def_attrs)

            else:
                print("Urecognised define: ", mat_type)

        self._makeMaterials(materials, elements, isotopes)

    def _makeMaterials(self, materials, elements, isotopes):
        isotope_dict = {}
        element_dict = {} # No material dict as materials go into the registry

        # Build the objects in order
        for isotope in isotopes:
            name = str(isotope.get("name", ""))
            Z    = float(isotope.get("Z", 0))
            N    = float(isotope.get("N", ""))
            a    = float(isotope.get("a", 0.0))

            iso = _g4.Isotope(name, Z, N, a, registry=self._registry)

        for element in elements:
            name = str(element.get("name", ""))
            symbol = str(element.get("formula", ""))

            if not element["components"]:
                Z    = float(element.get("Z", 0))
                a    = float(element.get("a", 0.0))
                ele = _g4.ElementSimple(name, symbol, Z, a, registry=self._registry)

            else:
                n_comp = len(element["components"])
                ele = _g4.ElementIsotopeMixture(name, symbol, n_comp, registry=self._registry)

                for comp in element["components"]:
                    ref = str(comp.get("ref", ""))
                    abundance = float(comp.get("n", 0.0))
                    ele.add_isotope(self._registry.materialDict[ref], abundance)

        for material in materials:
            name = str(material.get("name", ""))
            state = str(material.get("state",""))
            density = float(material.get("density", 0.0))

            if not material["components"]:
                Z    = float(material.get("Z", 0))
                a    = float(material.get("a", 0.0))
                mat = _g4.MaterialSingleElement(name, Z, a, density, registry=self._registry, tolerateZeroDensity=True)
                mat.set_state(state)

            else:
                n_comp = len(material["components"])
                comp_type = str(material["components"][0]["comp_type"])
                mat = _g4.MaterialCompound(name, density, n_comp, registry=self._registry, tolerateZeroDensity=True)
                mat.set_state(state)

                for comp in material["components"]:
                    ref = str(comp.get("ref", ""))
                    if ref not in self._registry.materialDict:
                        # If it is pre-defined material, no declaration would have been encountered
                        # Try to register the material as predefined
                        try:
                            _g4.MaterialPredefined(ref, registry=self._registry)

                        except ValueError:
                            raise ValueError("Component {} not defined"
                                             "for composite material {}".format(ref, name))

                    if comp_type == "fraction":
                        # abundance = float(comp.get("n", 0.0))
                        abundance = _defines.Expression("n", comp.get("n", 0.0),self._registry,False)

                        target = self._registry.materialDict[ref]
                        if isinstance(target, _g4.Material):
                            mat.add_material(target, abundance)
                        else:
                            mat.add_element_massfraction(target, abundance)

                    elif comp_type == "composite":
                        natoms = int(comp.get("n", 0))
                        mat.add_element_natoms(self._registry.materialDict[ref], natoms)

                    else:
                        raise ValueError("Unrecognised material component type: {}".format(comp_type))

            # Set the optional variables of state
            if "temperature" in material:
                mat.set_temperature(float(material["temperature"]), material["temperature_unit"])

            if "pressure" in material:
                mat.set_pressure(float(material["pressure"]), material["pressure_unit"])

            # Set the optional properties
            properties = material.get("properties")
            for pname, pref in properties.items():
                if pref not in self._registry.defineDict or not isinstance( self._registry.defineDict[pref], _defines.Matrix ):
                    raise ValueError("Referenced matrix {} not defined for property {} on material {}".format(pref, pname, name))
                mat.addProperty(pname, self._registry.defineDict[pref])

    def parseUserInfo(self,xmldoc):
        try:
            self.userinfo = xmldoc.getElementsByTagName("userinfo")[0]
        except IndexError:
            self.userinfo = None
            return

        for chnode in self.userinfo.childNodes:
            if chnode.nodeType != chnode.ELEMENT_NODE:
                # probably a comment node, skip
                continue
            self._parseAuxiliary(chnode)

    def _parseAuxiliary(self, xmlnode, register=True):

        aux_list = []
        for chnode in xmlnode.childNodes:
            if chnode.nodeType != chnode.ELEMENT_NODE:
                # probably a comment node, skip
                continue
            aux_list.append(self._parseAuxiliary(chnode, register=False))

        if xmlnode.tagName == "auxiliary":
            aux_type = xmlnode.attributes['auxtype'].value
            aux_value = xmlnode.attributes['auxvalue'].value

            try :
                aux_unit = xmlnode.attributes['auxunit'].value
            except KeyError :
                aux_unit = ""

            registry = self._registry if register else None
            aux = _defines.Auxiliary(aux_type, aux_value ,registry, aux_unit)
            for ax in aux_list:
                aux.addSubAuxiliary(ax)
            return aux

    def parseSolids(self,xmldoc) :

        self.xmlsolids = xmldoc.getElementsByTagName("solids")[0]
        
        for node in self.xmlsolids.childNodes : 
            try : 
                solid_type = node.tagName 
            except AttributeError : 
                continue # node is probably a comment so continue 

            if solid_type == 'box' :               # solid test 001
                self.parseBox(node)
            elif solid_type == 'tube' :            # solid test 002 
                self.parseTube(node)
            elif solid_type == 'cutTube' :         # solid test 003
                self.parseCutTube(node)                 
            elif solid_type == 'cone' :            # solid test 004 (problem when rmin1 == rmin2 != 0)
                self.parseCone(node)
            elif solid_type == 'para' :            # solid test 005
                self.parsePara(node) 
            elif solid_type == 'trd' :             # solid test 006 
                self.parseTrd(node) 
            elif solid_type == 'trap' :            # solid test 007 
                self.parseTrap(node)
            elif solid_type == 'sphere' :          # solid test 008 
                self.parseSphere(node)
            elif solid_type == 'orb' :             # solid test 009 
                self.parseOrb(node)
            elif solid_type == 'torus' :           # solid test 010 
                self.parseTorus(node)
            elif solid_type == 'polycone' :        # solid test 011 
                self.parsePolycone(node)
            elif solid_type == 'genericPolycone' : # solid test 012 
                self.parseGenericPolycone(node) 
            elif solid_type == 'polyhedra' :       # solid test 013 
                self.parsePolyhedra(node)
            elif solid_type == 'genericPolyhedra' :# solid test 014  
                self.parseGenericPolyhedra(node) 
            elif solid_type == 'eltube' :          # solid test 015 
                self.parseEllipticalTube(node)
            elif solid_type == 'ellipsoid' :       # solid test 016 
                self.parseEllipsoid(node)
            elif solid_type == 'elcone' :          # solid test 017 
                self.parseEllipticalCone(node) 
            elif solid_type == 'paraboloid' :      # solid test 018 
                self.parseParaboloid(node)
            elif solid_type == 'hype' :            # solid test 019 
                self.parseHype(node)
            elif solid_type == 'tet' :             # solid test 020 
                self.parseTet(node)
            elif solid_type == 'xtru' :            # solid test 021 
                self.parseExtrudedSolid(node)
            elif solid_type == 'twistedbox' :      # solid test 022 
                self.parseTwistedBox(node)
            elif solid_type == 'twistedtrap' :     # solid test 023 
                self.parseTwistedTrap(node)  
            elif solid_type == 'twistedtrd' :      # solid test 024 
                self.parseTwistedTrd(node) 
            elif solid_type == 'twistedtubs' :     # solid test 025 
                self.parseTwistedTubs(node)
            elif solid_type == 'arb8' :            # solid test 026 
                self.parseGenericTrap(node) 
            elif solid_type == 'tessellated' :     # solid test 027 
                self.parseTessellatedSolid(node)
            elif solid_type == 'union' :           # solid test 028 
                self.parseUnion(node) 
            elif solid_type == 'subtraction' :     # solid test 029 
                self.parseSubtraction(node) 
            elif solid_type == 'intersection' :    # solid test 030 
                self.parseIntersection(node) 
            elif solid_type == 'multiUnion' :      # solid test 031 
                self.parseMultiUnion(node)
            elif solid_type == 'opticalsurface' : 
                self.parseOpticalSurface(node)
            elif solid_type == "scaledSolid":
                self.parseScaledSolid(node)
            elif solid_type == 'loop' :           
                pass
                # self.parseSolidLoop(node)
            else : 
                print(solid_type, node.attributes['name'].value)

    def parseBox(self, node) : 
        solid_name = node.attributes['name'].value 
        x = _defines.Expression(solid_name+'_pX','{}'.format(node.attributes['x'].value),self._registry)
        y = _defines.Expression(solid_name+'_pY','{}'.format(node.attributes['y'].value),self._registry)
        z = _defines.Expression(solid_name+'_pZ','{}'.format(node.attributes['z'].value),self._registry)
        try : 
            unit = node.attributes['lunit'].value
        except KeyError : 
            unit = "mm"
              
        _g4.solid.Box(solid_name,x,y,z,self._registry,unit)

    def parseTube(self, node) : 
        solid_name = node.attributes['name'].value 

        try :
            rmin = _defines.Expression(solid_name+'_pRMin',node.attributes['rmin'].value,self._registry)
        except KeyError :
            rmin = _defines.Expression(solid_name+'_pRMin',"0",self._registry)
        try :
            sphi = _defines.Expression(solid_name+'_pSPhi',node.attributes['startphi'].value,self._registry)
        except KeyError : 
            sphi = _defines.Expression(solid_name+'_pSPhi',"0",self._registry)

        rmax = _defines.Expression(solid_name+'_pRMax',node.attributes['rmax'].value,self._registry)
        z    = _defines.Expression(solid_name+'_pDz',node.attributes['z'].value,self._registry)
        dphi = _defines.Expression(solid_name+'_pDPhi',node.attributes['deltaphi'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.Tubs(solid_name,rmin,rmax,z, sphi, dphi, self._registry, lunit, aunit)


    def parseCutTube(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            rmin = _defines.Expression(solid_name+'_pRMin',node.attributes['rmin'].value,self._registry)
        except KeyError : 
            rmin = _defines.Expression(solid_name+'_pRMin',"0",self._registry)
            
        rmax = _defines.Expression(solid_name+'_pRMax',node.attributes['rmax'].value,self._registry)
        dz   = _defines.Expression(solid_name+'_pDz',node.attributes['z'].value,self._registry)
        try : 
            sphi = _defines.Expression(solid_name+'_pSPhi',node.attributes['startphi'].value,self._registry)
        except KeyError :
            sphi = _defines.Expression(solid_name+'_pSPhi',"0",self._registry)
        
        dphi = _defines.Expression(solid_name+'_pDPhi',node.attributes['deltaphi'].value,self._registry)
        lx   = _defines.Expression(solid_name+'_plNorm_x',node.attributes['lowX'].value,self._registry)
        ly   = _defines.Expression(solid_name+'_plNorm_y',node.attributes['lowY'].value,self._registry)
        lz   = _defines.Expression(solid_name+'_plNorm_z',node.attributes['lowZ'].value,self._registry)
        hx   = _defines.Expression(solid_name+'_phNorm_x',node.attributes['highX'].value,self._registry)
        hy   = _defines.Expression(solid_name+'_phNorm_y',node.attributes['highY'].value,self._registry)
        hz   = _defines.Expression(solid_name+'_phNorm_z',node.attributes['highZ'].value,self._registry)

        lNorm = [lx, ly, lz] 
        hNorm = [hx, hy, hz]

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"
        
        _g4.solid.CutTubs(solid_name, rmin, rmax, dz, sphi, dphi, lNorm, hNorm, self._registry, lunit, aunit)
        

    def parseCone(self,node) : 
        solid_name = node.attributes['name'].value         

        try : 
            rmin1 = _defines.Expression(solid_name+"_pRMin1",node.attributes['rmin1'].value,self._registry) 
        except KeyError : 
            rmin1 = _defines.Expression(solid_name+"_pRMin1","0",self._registry) 
        try :
            rmin2 = _defines.Expression(solid_name+"_pRMin2",node.attributes['rmin2'].value,self._registry) 
        except KeyError : 
            rmin2 = _defines.Expression(solid_name+"_pRMin2","0",self._registry) 
        try :
            sphi  = _defines.Expression(solid_name+"_pSPhi",node.attributes['startphi'].value,self._registry) 
        except KeyError : 
            sphi  = _defines.Expression(solid_name+"_pSPhi","0",self._registry) 

        rmax1 = _defines.Expression(solid_name+"_pRMax1",node.attributes['rmax1'].value,self._registry) 
        rmax2 = _defines.Expression(solid_name+"_pRMax2",node.attributes['rmax2'].value,self._registry) 
        dz    = _defines.Expression(solid_name+"_pDz",node.attributes['z'].value,self._registry)
        dphi  = _defines.Expression(solid_name+"_pDPhi",node.attributes['deltaphi'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.Cons(solid_name, rmin1, rmax1, rmin2, rmax2, dz, sphi, dphi, self._registry, lunit, aunit)        

    def parsePara(self,node) : 
        solid_name = node.attributes['name'].value         

        x     = _defines.Expression(solid_name+'_pX',node.attributes['x'].value,self._registry) 
        y     = _defines.Expression(solid_name+'_pY',node.attributes['y'].value,self._registry) 
        z     = _defines.Expression(solid_name+'_pZ',node.attributes['z'].value,self._registry) 
        phi   = _defines.Expression(solid_name+'_pPhi',node.attributes['phi'].value,self._registry) 
        alpha = _defines.Expression(solid_name+'_pAlpha',node.attributes['alpha'].value,self._registry) 
        theta = _defines.Expression(solid_name+'_pTheta',node.attributes['theta'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.Para(solid_name, x, y, z, alpha, theta, phi, self._registry, lunit, aunit)

    def parseTrd(self, node) : 
        solid_name = node.attributes['name'].value
        
        x1 = _defines.Expression(solid_name+"_px1",node.attributes['x1'].value,self._registry)
        x2 = _defines.Expression(solid_name+"_px2",node.attributes['x2'].value,self._registry)
        y1 = _defines.Expression(solid_name+"_py1",node.attributes['y1'].value,self._registry)
        y2 = _defines.Expression(solid_name+"_py2",node.attributes['y2'].value,self._registry)
        z  = _defines.Expression(solid_name+"_z",node.attributes['z'].value,self._registry) 

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        _g4.solid.Trd(solid_name, x1, x2, y1, y2, z, self._registry, lunit)

    def parseTrap(self, node) : 
        solid_name = node.attributes['name'].value
        
        dz    = _defines.Expression(solid_name+"_pDz",node.attributes['z'].value,self._registry)
        theta = _defines.Expression(solid_name+"_pTheta",node.attributes['theta'].value,self._registry) 
        dphi  = _defines.Expression(solid_name+"_pDphi",node.attributes['phi'].value,self._registry)
        dx1   = _defines.Expression(solid_name+"_pDx1",node.attributes['x1'].value,self._registry)
        dx2   = _defines.Expression(solid_name+"_pDx2",node.attributes['x2'].value,self._registry)
        dx3   = _defines.Expression(solid_name+"_pDx3",node.attributes['x3'].value,self._registry)
        dx4   = _defines.Expression(solid_name+"_pDx4",node.attributes['x4'].value,self._registry)
        dy1   = _defines.Expression(solid_name+"_pDy1",node.attributes['y1'].value,self._registry)
        dy2   = _defines.Expression(solid_name+"_pDy2",node.attributes['y2'].value,self._registry)
        alp1  = _defines.Expression(solid_name+"_pAlp1",node.attributes['alpha1'].value,self._registry)
        alp2  = _defines.Expression(solid_name+"_pAlp2",node.attributes['alpha2'].value,self._registry)

        try :
            lunit = node.attributes['lunit'].value
        except KeyError :
            lunit = "mm"

        try :
            aunit = node.attributes['aunit'].value
        except KeyError :
            aunit = "rad"

        _g4.solid.Trap(solid_name,dz,theta,dphi,dy1,dx1,dx2,alp1,dy2,dx3,dx4,alp2,self._registry ,lunit, aunit)

    def parseSphere(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            rmin = _defines.Expression(solid_name+"_pRMin",node.attributes['rmin'].value,self._registry) 
        except KeyError : 
            rmin = _defines.Expression(solid_name+"_pRMin","0",self._registry)
        try : 
            startphi = _defines.Expression(solid_name+"_pSPhi",node.attributes['startphi'].value,self._registry) 
        except KeyError : 
            startphi = _defines.Expression(solid_name+"_pSPhi","0",self._registry) 
        try : 
            starttheta = _defines.Expression(solid_name+"_pSTheta",node.attributes['starttheta'].value,self._registry)
        except KeyError : 
            starttheta = _defines.Expression(solid_name+"_pSTheta","0",self._registry)

        try :
            lunit = node.attributes['lunit'].value
        except KeyError :
            lunit = "mm"

        try :
            aunit = node.attributes['aunit'].value
        except KeyError :
            aunit = "rad"

        rmax       = _defines.Expression(solid_name+"_pRMax",node.attributes['rmax'].value,self._registry)
        deltaphi   = _defines.Expression(solid_name+"_pDPhi",node.attributes['deltaphi'].value,self._registry)
        deltatheta = _defines.Expression(solid_name+"_pDTheta",node.attributes['deltatheta'].value,self._registry)

        _g4.solid.Sphere(solid_name, rmin, rmax, startphi, deltaphi, starttheta, deltatheta, self._registry, lunit, aunit)

    def parseOrb(self, node) : 
        solid_name = node.attributes['name'].value 
        
        r = _defines.Expression(solid_name+"_pRMax",node.attributes['r'].value,self._registry)
        
        _g4.solid.Orb(solid_name,r,self._registry)

    def parseTorus(self, node) : 
        solid_name = node.attributes['name'].value 

        rmin = _defines.Expression(solid_name+"_pRmin",node.attributes['rmin'].value,self._registry)
        rmax = _defines.Expression(solid_name+"_pRmax",node.attributes['rmax'].value,self._registry)
        rtor = _defines.Expression(solid_name+"_pRtor",node.attributes['rtor'].value,self._registry)
        sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self._registry) 
        dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self._registry)

        try :
            lunit = node.attributes['lunit'].value
        except KeyError :
            lunit = "mm"

        try :
            aunit = node.attributes['aunit'].value
        except KeyError :
            aunit = "rad"

        _g4.solid.Torus(solid_name,rmin,rmax,rtor, sphi, dphi, self._registry, lunit, aunit)


    def parsePolycone(self, node) : 
        solid_name = node.attributes['name'].value

        try :
            sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self._registry)
        except KeyError:
            sphi = _defines.Expression(solid_name+"_pSphi", "0",self._registry)

        try:
            dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self._registry)
        except KeyError:
            dphi = _defines.Expression(solid_name+"_pDphi", "2*pi" ,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        Rmin = []
        Rmax = []
        Z    = []

        i = 0
        for chNode in node.childNodes :
            rmin  = _defines.Expression(solid_name+"_zplane_rmin"+str(i),chNode.attributes['rmin'].value,self._registry)
            rmax  = _defines.Expression(solid_name+"_zplane_rmax"+str(i),chNode.attributes['rmax'].value,self._registry)
            z     = _defines.Expression(solid_name+"_zplane_z"+str(i),chNode.attributes['z'].value,self._registry)
            Rmin.append(rmin)
            Rmax.append(rmax)
            Z.append(z)
            i+=1

        _g4.solid.Polycone(solid_name, sphi, dphi, Z, Rmin, Rmax, self._registry, lunit, aunit)

    def parseGenericPolycone(self, node) :
        solid_name = node.attributes['name'].value
        try :
            sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self._registry)
        except KeyError:
            sphi = _defines.Expression(solid_name+"_pSphi", "0",self._registry)

        try:
            dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self._registry)
        except KeyError:
            dphi = _defines.Expression(solid_name+"_pDphi", "2*pi" ,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        R = []
        Z = []

        i = 0
        for chNode in node.childNodes :
            r     = _defines.Expression(solid_name+"_rzpoint_r"+str(i),chNode.attributes['r'].value,self._registry)
            z     = _defines.Expression(solid_name+"_rzpoint_z"+str(i),chNode.attributes['z'].value,self._registry)
            R.append(r)
            Z.append(z)
            i+=1

        _g4.solid.GenericPolycone(solid_name, sphi, dphi, R, Z, self._registry,lunit,aunit)


    def parsePolyhedra(self, node) :
        solid_name = node.attributes['name'].value

        try :
            sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self._registry)
        except KeyError:
            sphi = _defines.Expression(solid_name+"_pSphi", "0",self._registry)

        try:
            dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self._registry)
        except KeyError:
            dphi = _defines.Expression(solid_name+"_pDphi", "2*pi" ,self._registry)

        nside = _defines.Expression("{}_numSide".format(solid_name),
                                    node.attributes['numsides'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        Rmin = []
        Rmax = []
        Z    = []

        i = 0
        for chNode in node.childNodes :
            rmin = _defines.Expression("{}_zplaine_rmin_{}".format(solid_name, i),
                                       chNode.attributes['rmin'].value,
                                       self._registry)

            rmax = _defines.Expression("{}_zplaine_rmax_{}".format(solid_name, i),
                                       chNode.attributes['rmax'].value,
                                       self._registry)

            z = _defines.Expression("{}_zplaine_z_{}".format(solid_name, i),
                                        chNode.attributes['z'].value,
                                        self._registry)

            Rmin.append(rmin)
            Rmax.append(rmax)
            Z.append(z)
            i += 1

        nzplane = _defines.Expression("{}_numZplanes".format(solid_name), len(Z), self._registry)

        _g4.solid.Polyhedra(solid_name, sphi, dphi, nside, nzplane, Z, Rmin, Rmax, registry=self._registry,lunit=lunit,aunit=aunit)

    def parseGenericPolyhedra(self, node) :
        solid_name = node.attributes['name'].value

        try :
            sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self._registry)
        except KeyError:
            sphi = _defines.Expression(solid_name+"_pSphi", "0",self._registry)

        try:
            dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self._registry)
        except KeyError:
            dphi = _defines.Expression(solid_name+"_pDphi", "2*pi" ,self._registry)

        nside = _defines.Expression("{}_numSide".format(solid_name),
                                    node.attributes['numsides'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        R = []
        Z = []
        
        i = 0
        for chNode in node.childNodes :
            r     = _defines.Expression(solid_name+"_rzpoint_r"+str(i),chNode.attributes['r'].value,self._registry)
            z     = _defines.Expression(solid_name+"_rzpoint_z"+str(i),chNode.attributes['z'].value,self._registry)
            R.append(r)
            Z.append(z)
            i+=1

        _g4.solid.GenericPolyhedra(solid_name, sphi, dphi, nside, R, Z, self._registry, lunit, aunit)

    def parseEllipticalTube(self, node) : 
        solid_name = node.attributes['name'].value
        
        dx = _defines.Expression(solid_name+"_dx",node.attributes['dx'].value,self._registry) 
        dy = _defines.Expression(solid_name+"_dy",node.attributes['dy'].value,self._registry) 
        dz = _defines.Expression(solid_name+"_dz",node.attributes['dz'].value,self._registry) 
    
        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        _g4.solid.EllipticalTube(solid_name,dx,dy,dz, self._registry,lunit)

    def parseEllipsoid(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            bcut = _defines.Expression(solid_name+"_zcut1",node.attributes['zcut1'].value,self._registry)
        except KeyError :
            bcut = _defines.Expression(solid_name+"_zcut1","-1E20",self._registry)

        ax   = _defines.Expression(solid_name+"_ax",node.attributes['ax'].value,self._registry)
        by   = _defines.Expression(solid_name+"_by",node.attributes['by'].value,self._registry)
        cz   = _defines.Expression(solid_name+"_cz",node.attributes['cz'].value,self._registry)
        tcut = _defines.Expression(solid_name+"_zcut2",node.attributes['zcut2'].value,self._registry) 
        
        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        _g4.solid.Ellipsoid(solid_name, ax, by, cz, bcut, tcut, self._registry, lunit)

    def parseEllipticalCone(self, node) : 
        solid_name = node.attributes['name'].value 

        pxSemiAxis = _defines.Expression(solid_name+"_pxSemiAxis",node.attributes['dx'].value,self._registry)
        pySemiAxis = _defines.Expression(solid_name+"_pySemiAxis",node.attributes['dy'].value,self._registry)
        zMax       = _defines.Expression(solid_name+"_zMax",node.attributes['zmax'].value,self._registry)
        pzTopCut   = _defines.Expression(solid_name+"_pzTopCut",node.attributes['zcut'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        _g4.solid.EllipticalCone(solid_name,pxSemiAxis,pySemiAxis,zMax,pzTopCut,self._registry,lunit=lunit)

    def parseParaboloid(self, node) : 
        solid_name = node.attributes['name'].value 

        Dz         = _defines.Expression(solid_name+"_Dz",node.attributes['dz'].value,self._registry)
        R1         = _defines.Expression(solid_name+"_R1",node.attributes['rlo'].value,self._registry)
        R2         = _defines.Expression(solid_name+"_R2",node.attributes['rhi'].value,self._registry)
        
        _g4.solid.Paraboloid(solid_name, Dz, R1, R2, self._registry)
        
    def parseHype(self, node) : 
        solid_name = node.attributes['name'].value         
        
        try : 
            innerStereo = _defines.Expression(solid_name+'_innerStereo',node.attributes['inst'].value,self._registry) 
        except KeyError : 
            innerStereo = _defines.Expression(solid_name+'_innerStereo',"0",self._registry)             

        innerRadius = _defines.Expression(solid_name+'_innerRadius',node.attributes['rmin'].value,self._registry) 
        outerRadius = _defines.Expression(solid_name+'_outerRadius',node.attributes['rmax'].value,self._registry)
        outerStereo = _defines.Expression(solid_name+'_outerStereo',node.attributes['outst'].value,self._registry) 
        halfLenZ    = _defines.Expression(solid_name+'_halfLenZ',node.attributes['z'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.Hype(solid_name, innerRadius, outerRadius, innerStereo, outerStereo, halfLenZ, self._registry, lunit, aunit) 

    def parseTet(self, node) : 
        solid_name = node.attributes['name'].value         
        
        anchor = self._registry.defineDict[node.attributes['vertex1'].value]
        p2     = self._registry.defineDict[node.attributes['vertex2'].value]
        p3     = self._registry.defineDict[node.attributes['vertex3'].value]
        p4     = self._registry.defineDict[node.attributes['vertex4'].value]
        
        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        _g4.solid.Tet(solid_name, anchor, p2, p3, p4, self._registry, lunit, False)
        
    def parseExtrudedSolid(self, node) : 
        solid_name = node.attributes['name'].value

        pPolygon = []
        zSection = []
        
        ivec = 1
        isec = 1 
        for chNode in node.childNodes : 
            if chNode.tagName == "twoDimVertex" : 
                x = _defines.Expression(solid_name+'_'+str(ivec)+'_x',chNode.attributes['x'].value,self._registry)
                y = _defines.Expression(solid_name+'_'+str(ivec)+'_y',chNode.attributes['y'].value,self._registry)
                pPolygon.append([x,y])
                ivec = ivec+1
            if chNode.tagName == "section" : 
                scale = _defines.Expression(solid_name+"_"+str(isec)+"_scale",chNode.attributes['scalingFactor'].value,self._registry)
                xoff  = _defines.Expression(solid_name+"_"+str(isec)+"_xoff",chNode.attributes['xOffset'].value,self._registry)
                yoff  = _defines.Expression(solid_name+"_"+str(isec)+"_yoff",chNode.attributes['yOffset'].value,self._registry)
                zpos  = _defines.Expression(solid_name+"_"+str(isec)+"_zpos",chNode.attributes['zPosition'].value,self._registry)
                zSection.append([zpos,[xoff,yoff],scale])
                isec = isec+1

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        _g4.solid.ExtrudedSolid(solid_name, pPolygon, zSection,self._registry,lunit=lunit)
        # print 'extruded solid NOT IMPLEMENTED'

    def parseTwistedBox(self, node) :
        solid_name = node.attributes['name'].value

        twistedAngle = _defines.Expression(solid_name+'_PhiTwist',node.attributes['PhiTwist'].value,self._registry)
        x = _defines.Expression(solid_name+'_x',node.attributes['x'].value,self._registry)
        y = _defines.Expression(solid_name+'_y',node.attributes['y'].value,self._registry)
        z = _defines.Expression(solid_name+'_z',node.attributes['z'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.TwistedBox(solid_name, twistedAngle, x, y, z, self._registry, lunit, aunit)

    def parseTwistedTrap(self, node) : 
        solid_name = node.attributes['name'].value

        twistedAngle = _defines.Expression(solid_name+'_PhiTwist',node.attributes['PhiTwist'].value,self._registry)
        Theta = _defines.Expression(solid_name+'_Theta',node.attributes['Theta'].value,self._registry)
        Phi = _defines.Expression(solid_name+'_Phi',node.attributes['Phi'].value,self._registry)
        Alph = _defines.Expression(solid_name+'_Alph',node.attributes['Alph'].value,self._registry)
        x1 = _defines.Expression(solid_name+'_x1',node.attributes['x1'].value,self._registry)
        x2 = _defines.Expression(solid_name+'_x2',node.attributes['x2'].value,self._registry)
        x3 = _defines.Expression(solid_name+'_x3',node.attributes['x3'].value,self._registry)
        x4 = _defines.Expression(solid_name+'_x4',node.attributes['x4'].value,self._registry)
        y1 = _defines.Expression(solid_name+'_y1',node.attributes['y1'].value,self._registry)
        y2 = _defines.Expression(solid_name+'_y2',node.attributes['y2'].value,self._registry)
        z  = _defines.Expression(solid_name+'_z',node.attributes['z'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.TwistedTrap(solid_name, twistedAngle, z, Theta, Phi, y1,
                              x1, x2, y2, x3, x4, Alph, self._registry, lunit, aunit)


    def parseTwistedTrd(self, node) :
        solid_name = node.attributes['name'].value

        twistedAngle = _defines.Expression(solid_name+'_PhiTwist',node.attributes['PhiTwist'].value,self._registry)
        x1 = _defines.Expression(solid_name+'_x1',node.attributes['x1'].value,self._registry)
        x2 = _defines.Expression(solid_name+'_x2',node.attributes['x2'].value,self._registry)
        y1 = _defines.Expression(solid_name+'_y1',node.attributes['y1'].value,self._registry)
        y2 = _defines.Expression(solid_name+'_y2',node.attributes['y2'].value,self._registry)
        z    = _defines.Expression(solid_name+'_z',node.attributes['z'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.TwistedTrd(solid_name, twistedAngle, x1, x2, y1, y2, z, self._registry, lunit, aunit)

    def parseTwistedTubs(self,node) : 
        solid_name = node.attributes['name'].value

        twist = _defines.Expression(solid_name+'_twistedangle',
                                    node.attributes['twistedangle'].value,
                                    self._registry)

        inner_rad = _defines.Expression(solid_name+'_endinnerrad',
                                        node.attributes['endinnerrad'].value,
                                        self._registry)

        outer_rad = _defines.Expression(solid_name+'_endouterrad',
                                        node.attributes['endouterrad'].value,
                                        self._registry)

        zlen = _defines.Expression(solid_name+'_zlen',node.attributes['zlen'].value,self._registry)
        phi = _defines.Expression(solid_name+'_phi',node.attributes['phi'].value,self._registry)

        try : 
            lunit = node.attributes['lunit'].value
        except KeyError : 
            lunit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.TwistedTubs(solid_name, inner_rad, outer_rad, zlen, phi, twist, self._registry, lunit, aunit)

    def parseGenericTrap(self,node) :
        solid_name = node.attributes['name'].value

        args = [solid_name]
        for i in range(1,9):
            vx = _defines.Expression("{}_v{}x".format(solid_name, i),
                                     node.attributes["v{}x".format(i)].value,
                                     self._registry)
            vy = _defines.Expression("{}_v{}y".format(solid_name, i),
                                     node.attributes["v{}y".format(i)].value,
                                     self._registry)
            args.extend([vx, vy])

        try :
            lunit = node.attributes['lunit'].value
        except KeyError :
            lunit = "mm"

        dz = _defines.Expression(solid_name+"_dz",node.attributes["dz"].value,self._registry)
        args.extend([dz, self._registry, True, lunit])

        _g4.solid.GenericTrap(*args)

    def parseTessellatedSolid(self,node) : 
        solid_name = node.attributes['name'].value

        facet_list = [] 
            
        for chNode in node.childNodes : 
            if chNode.tagName == "triangular" : 
                v1 = chNode.attributes['vertex1'].value
                v2 = chNode.attributes['vertex2'].value
                v3 = chNode.attributes['vertex3'].value
                facet_list.append([v1,v2,v3])
            elif chNode.tagName == 'quadrangular' : 
                v1 = chNode.attributes['vertex1'].value
                v2 = chNode.attributes['vertex2'].value
                v3 = chNode.attributes['vertex3'].value
                v4 = chNode.attributes['vertex4'].value
                facet_list.append([v1,v2,v3,v4])
        
        _g4.solid.TessellatedSolid(solid_name, facet_list, self._registry, _g4.solid.TessellatedSolid.MeshType.Gdml)
        
    def parseUnion(self, node) : 
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError :
            try:
                position = self.parseVector(node.getElementsByTagName("positionref")[0], "positionref", False)
            except IndexError:
                position   = _defines.Position("zero","0","0","0","mm",self._registry,False)
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            try:
                rotation = self.parseVector(node.getElementsByTagName("rotationref")[0], "rotationref", False)
            except IndexError:
                rotation   = _defines.Rotation("identity","0","0","0","rad",self._registry,False)
        
        _g4.solid.Union(solid_name, self._registry.solidDict[first], self._registry.solidDict[second],[rotation,position],self._registry)  

    def parseSubtraction(self, node) : 
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError :
            try:
                position = self.parseVector(node.getElementsByTagName("positionref")[0], "positionref", False)
            except IndexError:
                position   = _defines.Position("zero","0","0","0","mm",self._registry,False)
        try :
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError :
            try:
                rotation = self.parseVector(node.getElementsByTagName("rotationref")[0], "rotationref", False)
            except IndexError:
                rotation   = _defines.Rotation("identity","0","0","0","rad",self._registry,False)

        _g4.solid.Subtraction(solid_name, self._registry.solidDict[first], self._registry.solidDict[second],[rotation,position],self._registry)

    def parseIntersection(self, node) :
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError : 
            try:
                position = self.parseVector(node.getElementsByTagName("positionref")[0], "positionref", False)
            except IndexError:
                position   = _defines.Position("zero","0","0","0","mm",self._registry,False)
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            try:
                rotation = self.parseVector(node.getElementsByTagName("rotationref")[0], "rotationref", False)
            except IndexError:
                rotation   = _defines.Rotation("identity","0","0","0","rad",self._registry,False)

        _g4.solid.Intersection(solid_name, self._registry.solidDict[first], self._registry.solidDict[second],[rotation,position],self._registry)

    def parseMultiUnion(self, node) :
        solid_name = node.attributes['name'].value

        muSolids        = [] 
        transformations = []

        for n in node.getElementsByTagName("multiUnionNode") :
            if n.tagName == "multiUnionNode" : 
                mu_node_name = n.attributes['name']

                # if not defined then need to define defaults
                position = _defines.Position(mu_node_name.value+"_pos","0","0","0","mm",self._registry,False)
                rotation = _defines.Rotation(mu_node_name.value+"_rot","0","0","0","rad",self._registry,False)

                # loop over child nodes 
                for cn in n.childNodes :
                    if cn.tagName == "solid" : 
                        muNodeName = cn.attributes['ref'].value 
                        muNodeSolid = self._registry.solidDict[muNodeName]
                    elif cn.tagName == "position" :
                        position = self.parseVector(cn, "position", False)
                    elif cn.tagName == "positionref" :
                        positionName = cn.attributes['ref'].value
                        position     = self._registry.defineDict[positionName]
                    elif cn.tagName == "rotation" :
                        rotation = self.parseVector(cn, "rotation", False)
                    elif cn.tagName == "rotationref" : 
                        rotationName = cn.attributes['ref'].value
                        rotation     = self._registry.defineDict[rotationName]
                                                                
                muSolids.append(muNodeSolid)
                transformations.append([rotation,position])
        
        _g4.solid.MultiUnion(solid_name, muSolids, transformations,self._registry, True)
        
    def parseOpticalSurface(self, node) : 
        solid_name = node.attributes['name'].value

        finish = node.attributes['finish'].value
        model = node.attributes['model'].value
        surf_type = node.attributes['type'].value
        value = _defines.Expression(solid_name+'_value',node.attributes['value'].value,self._registry)

        surf = _g4.solid.OpticalSurface(solid_name, finish, model, surf_type, value, self._registry, True)

        properties = {}
        for chNode in node.childNodes:
            if chNode.nodeType != chNode.ELEMENT_NODE:
                continue # comment
            if chNode.tagName=="property":
                try :
                    properties[chNode.attributes["name"].value] = chNode.attributes["ref"].value
                except KeyError :
                    pass
        for pname, pref in properties.items():
            if pref not in self._registry.defineDict:
                raise ValueError("Referenced matrix {} not defined for property {} on optical surface {}".format(pref, pname, solid_name))
            surf.addProperty(pname, self._registry.defineDict[pref])

    def parseScaledSolid(self,node):
        scaledSolid_name = node.attributes['name'].value

        solid_name = node.getElementsByTagName("solidref")[0].attributes['ref'].value

        try:
            scale = self.parseVector(node.getElementsByTagName("scale")[0], "scale", False)
        except IndexError:
            try:
                scale = self.parseVector(node.getElementsByTagName("scaleref")[0], "scaleref", False)
            except IndexError:
                scale = _defines.Scale("zero", "0", "0", "0", "mm", self._registry, False)

        solid = self._registry.solidDict[solid_name]
        
        _g4.solid.Scaled(scaledSolid_name, solid, scale.x.expression, scale.y.expression, scale.z.expression, self._registry)

    def parseSolidLoop(self, node):
        pass
        
    def parseStructure(self,xmldoc):
        
        self.xmlstructure = xmldoc.getElementsByTagName("structure")[0]
        
        # loop over child nodes 
        for node in self.xmlstructure.childNodes :
            self.extractStructureNodeData(node)

        # find world logical volume 
        self.xmlsetup = xmldoc.getElementsByTagName("setup")[0]
        worldLvName = self.xmlsetup.childNodes[0].attributes["ref"].value
        self._registry.orderLogicalVolumes(worldLvName)
        self._registry.setWorld(worldLvName)

    def extractStructureNodeData(self, node) : 
        
        if node.nodeType == node.ELEMENT_NODE : 
            node_name = node.tagName 

            if node_name == "volume" :
                name      = node.attributes["name"].value
                material  = node.getElementsByTagName("materialref")[0].attributes["ref"].value
                solid     = node.getElementsByTagName("solidref")[0].attributes["ref"].value
                
                if material in self._registry.materialDict:
                    mat = self._registry.materialDict[material]
                else:
                    try:
                        mat = _g4.MaterialPredefined(material)
                    except ValueError:
                        mat = _g4.MaterialArbitrary(material)

                aux_list = []
                try:
                    for aux_node in node.childNodes:
                        try :
                            if aux_node.tagName == "auxiliary":
                                aux = self._parseAuxiliary(aux_node, register=False)
                                aux_list.append(aux)
                        except AttributeError :
                            pass # probably a comment
                except IndexError:
                    pass

                vol = _g4.LogicalVolume(self._registry.solidDict[solid], mat, name, registry=self._registry,
                auxiliary=aux_list)
                self.parsePhysicalVolumeChildren(node,vol)

                # vol.checkOverlaps()

            elif node_name == "assembly" :
                name = node.attributes["name"].value
                vol  = _g4.AssemblyVolume(name,self._registry, True)
                self.parsePhysicalVolumeChildren(node,vol)
                # vol.checkOverlaps()

            elif node_name == "bordersurface":
                name  = node.attributes["name"].value
                surf_property  = node.attributes["surfaceproperty"].value
                pvol1 = node.getElementsByTagName("physvolref")[0].attributes["ref"].value
                pvol2 = node.getElementsByTagName("physvolref")[1].attributes["ref"].value

                surf  = _g4.BorderSurface(name, pvol1, pvol2, surf_property, self._registry)

            elif node_name == "skinsurface" :
                name  = node.attributes["name"].value
                surf_property  = node.attributes["surfaceproperty"].value
                volref = node.getElementsByTagName("volumeref")[0].attributes["ref"].value

                surf  = _g4.SkinSurface(name, volref, surf_property, self._registry)

            elif node_name == "loop" :
                print("Reader> loop not implemented")
            else:
                print("Unrecognised node: ", node_name)
        
    def parsePhysicalVolumeChildren(self, node, vol) :
        for chNode in node.childNodes :
            if chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "physvol" :
                volref    = chNode.getElementsByTagName("volumeref")[0].attributes["ref"].value

                # Name 
                try : 
                    pvol_name = chNode.attributes["name"].value
                except KeyError:
                    # no name given - in the Geant4 GDML reader it would be <lv name> + _PV
                    # here we do the same but we truly require unique names, so we count them
                    count = self._physVolumeNameCount[volref]
                    suffix = '_'+str(count) if count > 0 else ''
                    pvol_name = volref+suffix+"_PV"
                    self._physVolumeNameCount[volref] += 1
                            
                _log.info('Reader.extractStructureNodeData> %s' % (pvol_name))
                            
                # Position 
                _log.info('Reader.extractStructureNodeData> pv position %s' % (pvol_name))
                try : 
                    position = self._registry.defineDict[chNode.getElementsByTagName("positionref")[0].attributes["ref"].value]
                except IndexError : 
                    try : 
                        position = self.parseVector(chNode.getElementsByTagName("position")[0],"position",False)
                    except IndexError : 
                        position = _defines.Position(pvol_name+"_pos","0","0","0","mm",self._registry,False)

                # Rotation
                _log.info('Reader.extractStructureNodeData> pv rotation %s',pvol_name)
                try : 
                    rotation = self._registry.defineDict[chNode.getElementsByTagName("rotationref")[0].attributes["ref"].value]
                except IndexError : 
                    try : 
                        rotation = self.parseVector(chNode.getElementsByTagName("rotation")[0],"rotation",False)  
                    except IndexError : 
                        rotation = _defines.Rotation(pvol_name+"_rot","0","0","0","rad",self._registry,False)

                # Scale 
                _log.info('Reader.extractStructureNodeData> pv scale %s ' % (pvol_name))
                try :                             
                    scale = self._registry.defineDict[chNode.getElementsByTagName("scaleref")[0].attributes["ref"].value]
                except IndexError : 
                    try : 
                        scale = self.parseVector(chNode.getElementsByTagName("scale")[0],"scale",False)
                    except IndexError : 
                        scale = None

                # Create physical volume
                _log.info('Reader.extractStructureNodeData> construct % s' % (pvol_name))

                try :
                    copyNumber = int(chNode.attributes["copynumber"].value)
                except KeyError :
                    copyNumber = 0

                physvol   = _g4.PhysicalVolume(rotation, position, self._registry.logicalVolumeDict[volref],
                                               pvol_name, vol, registry=self._registry,
                                               copyNumber=copyNumber, scale=scale)
                
            elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "replicavol":
                nreplica  = chNode.attributes['number'].value
                volref    = chNode.getElementsByTagName("volumeref")[0].attributes["ref"].value

                # Name 
                try:
                    pvol_name = chNode.attributes["name"].value
                except KeyError:
                    pvol_name = volref+"_ReplicaPV"
                                
                repNode   = chNode.getElementsByTagName("replicate_along_axis")[0]
                dirNode   = repNode.getElementsByTagName("direction")[0]
                if 'x' in dirNode.attributes:
                    axis = _g4.ReplicaVolume.Axis.kXAxis 
                elif 'y' in dirNode.attributes:
                    axis = _g4.ReplicaVolume.Axis.kYAxis
                elif 'z' in dirNode.attributes:
                    axis = _g4.ReplicaVolume.Axis.kZAxis 
                elif 'rho' in dirNode.attributes:
                    axis = _g4.ReplicaVolume.Axis.kRho 
                elif 'phi' in dirNode.attributes:
                    axis = _g4.ReplicaVolume.Axis.kPhi 

                nreplicas  = _defines.Expression(pvol_name+"_nreplica",
                                                 chNode.attributes['number'].value,
                                                 self._registry, False)

                width_u   = repNode.getElementsByTagName("offset")[0].attributes['unit'].value
                width     =  _defines.Expression(pvol_name+"_width",
                                                 repNode.getElementsByTagName("width")[0].attributes['value'].value,
                                                 self._registry, False)
                
                offset_u  = repNode.getElementsByTagName("offset")[0].attributes['unit'].value
                offset    = _defines.Expression(pvol_name+"offset",
                                                repNode.getElementsByTagName("offset")[0].attributes['value'].value,
                                                self._registry, False)
                
                rv = _g4.ReplicaVolume(pvol_name,
                                       self._registry.logicalVolumeDict[volref],
                                       vol,
                                       axis,
                                       nreplicas, 
                                       width,
                                       offset,
                                       self._registry,
                                       True,
                                       width_u,
                                       offset_u)
                                                       
            elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "paramvol":


                volref  = chNode.getElementsByTagName('volumeref')[0].attributes['ref'].value

                # Name
                try:
                    pvol_name = chNode.attributes["name"].value
                except KeyError:
                    pvol_name = volref+"_ParamPV"


                ncopies= _defines.Expression(pvol_name+"_ncopies",
                                             chNode.attributes['ncopies'].value,
                                             self._registry, False)

                pps     = chNode.getElementsByTagName('parameterised_position_size')[0]


                # transformations
                transforms = []

                # dimensions
                paramData = []

                for ppsChNode in pps.childNodes:

                    # default position
                    position = _defines.Position(pvol_name, "0", "0", "0", "mm", self._registry, False)

                    # default rotation
                    rotation = _defines.Rotation(pvol_name, "0", "0", "0", "rad", self._registry, False)


                    for ppsChNodeTag in ppsChNode.childNodes:
                        if ppsChNodeTag.tagName == "position":
                            position = self.parseVector(ppsChNodeTag, "position", False)
                        elif ppsChNodeTag.tagName == "positionref":
                            position = self._registry.defineDict[ppsChNodeTag.attributes["ref"].value]
                        elif ppsChNodeTag.tagName == "rotation":
                            rotation = self.parseVector(ppsChNodeTag, "rotation", False)
                        elif ppsChNodeTag.tagName == "rotationref":
                            rotation = self._registry.defineDict[ppsChNodeTag.attributes["ref"].value]
                        elif ppsChNodeTag.tagName == "box_dimensions":
                            x = _defines.Expression(pvol_name + '_Box_pX', '{}'.format(ppsChNodeTag.attributes['x'].value),self._registry, False)
                            y = _defines.Expression(pvol_name + '_Box_pY', '{}'.format(ppsChNodeTag.attributes['y'].value),self._registry, False)
                            z = _defines.Expression(pvol_name + '_Box_pZ', '{}'.format(ppsChNodeTag.attributes['z'].value),self._registry, False)
                            if 'lunit' in ppsChNodeTag.attributes:
                                unit = ppsChNodeTag.attributes['lunit'].value
                            else :
                                unit = "mm"

                            dim = _g4.ParameterisedVolume.BoxDimensions(x,y,z)
                        elif ppsChNodeTag.tagName == "tube_dimensions":
                            try :
                                pRMin = _defines.Expression(pvol_name + '_Tubs_rMin', '{}'.format(ppsChNodeTag.attributes['InR'].value),self._registry, False)
                            except KeyError :
                                pRMin = _defines.Expression(pvol_name + '_Tubs_rMin', "0", self._registry, False)

                            pRMax = _defines.Expression(pvol_name + '_Tubs_rMax', '{}'.format(ppsChNodeTag.attributes['OutR'].value),self._registry, False)
                            pDz   = _defines.Expression(pvol_name + '_Tubs_Dz', '{}'.format(ppsChNodeTag.attributes['hz'].value),self._registry, False)
                            try:
                                pSPhi = _defines.Expression(pvol_name + '_Tubs_SPhi', '{}'.format(ppsChNodeTag.attributes['StartPhi'].value),self._registry, False)
                            except KeyError:
                                pSPhi = _defines.Expression(pvol_name + '_Tubs_SPhi', "0", self._registry, False)

                            pDPhi = _defines.Expression(pvol_name + '_Tubs_DPhi', '{}'.format(ppsChNodeTag.attributes['DeltaPhi'].value), self._registry,False)


                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else :
                                lunit = "mm"

                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else :
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.TubeDimensions(pRMin, pRMax, pDz, pSPhi, pDPhi, lunit, aunit)
                        elif ppsChNodeTag.tagName == "cone_dimensions":
                            try :
                                pRMin1 = _defines.Expression(pvol_name + '_Cone_rMin1', '{}'.format(ppsChNodeTag.attributes['rmin1'].value),self._registry, False)
                            except KeyError :
                                pRMin1 = _defines.Expression(pvol_name + '_Cone_rMin1', "0", self._registry, False)
                            pRMax1 = _defines.Expression(pvol_name + '_Cone_rMax1','{}'.format(ppsChNodeTag.attributes['rmax1'].value),self._registry, False)

                            try :
                                pRMin2 = _defines.Expression(pvol_name + '_Cone_rMin2', '{}'.format(ppsChNodeTag.attributes['rmin2'].value),self._registry, False)
                            except KeyError :
                                pRMin2 = _defines.Expression(pvol_name + '_Cone_rMin2', "0", self._registry, False)
                            pRMax2 = _defines.Expression(pvol_name + '_Cone_rMax2','{}'.format(ppsChNodeTag.attributes['rmax2'].value),self._registry, False)
                            pDz   = _defines.Expression(pvol_name + '_Tubs_Dz', '{}'.format(ppsChNodeTag.attributes['z'].value),self._registry, False)

                            try :
                                pSPhi = _defines.Expression(pvol_name + '_Tubs_SPhi', '{}'.format(ppsChNodeTag.attributes['startphi'].value),self._registry, False)
                            except KeyError :
                                pSPhi = _defines.Expression(pvol_name + '_Tubs_SPhi', "0", self._registry, False)
                            pDPhi = _defines.Expression(pvol_name + '_Tubs_DPhi', '{}'.format(ppsChNodeTag.attributes['deltaphi'].value), self._registry,False)


                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else :
                                lunit = "mm"

                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else :
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.ConeDimensions(pRMin1,pRMax1, pRMin2, pRMax2, pDz, pSPhi, pDPhi, lunit, aunit)
                        elif ppsChNodeTag.tagName == "orb_dimensions":
                            pRMax = _defines.Expression(pvol_name + '_Orb_r','{}'.format(ppsChNodeTag.attributes['r'].value),self._registry, False)
                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else :
                                lunit = "mm"

                            dim = _g4.ParameterisedVolume.OrbDimensions(pRMax,lunit)
                        elif ppsChNodeTag.tagName == "sphere_dimensions":
                            try :
                                pRMin = _defines.Expression(pvol_name + '_Sphere_rMin','{}'.format(ppsChNodeTag.attributes['rmin'].value),self._registry, False)
                            except KeyError:
                                pRMin = _defines.Expression(pvol_name + '_Sphere_rMin', "0", self._registry, False)
                            pRMax = _defines.Expression(pvol_name + '_Sphere_rMax','{}'.format(ppsChNodeTag.attributes['rmax'].value),self._registry, False)
                            try :
                                pSPhi = _defines.Expression(pvol_name + '_Sphere_sPhi','{}'.format(ppsChNodeTag.attributes['startphi'].value),self._registry, False)
                            except KeyError:
                                pSPhi = _defines.Expression(pvol_name + '_Sphere_sPhi', "0", self._registry, False)
                            pDPhi = _defines.Expression(pvol_name + '_Sphere_dPhi','{}'.format(ppsChNodeTag.attributes['deltaphi'].value),self._registry, False)
                            try :
                                pSTheta = _defines.Expression(pvol_name + '_Sphere_sTheta','{}'.format(ppsChNodeTag.attributes['starttheta'].value),self._registry, False)
                            except KeyError:
                                pSTheta = _defines.Expression(pvol_name + '_Sphere_sTheta', "0", self._registry, False)
                            pDTheta = _defines.Expression(pvol_name + '_Sphere_sTheta','{}'.format(ppsChNodeTag.attributes['deltatheta'].value),self._registry, False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"

                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.SphereDimensions(pRMin, pRMax,pSPhi,pDPhi, pSTheta, pDTheta, lunit, aunit)
                        elif ppsChNodeTag.tagName == "torus_dimensions":
                            pRMin = _defines.Expression(pvol_name + '_Torus_rMin','{}'.format(ppsChNodeTag.attributes['rmin'].value), self._registry,False)
                            pRMax = _defines.Expression(pvol_name + '_Torus_rMax', '{}'.format(ppsChNodeTag.attributes['rmax'].value),self._registry, False)
                            pRTor = _defines.Expression(pvol_name + '_Torus_rTor', '{}'.format(ppsChNodeTag.attributes['rtor'].value),self._registry, False)
                            try:
                                pSPhi = _defines.Expression(pvol_name + '_Torus_sPhi', '{}'.format(ppsChNodeTag.attributes['startphi'].value),self._registry, False)
                            except KeyError:
                                pSPhi = _defines.Expression(pvol_name + '_Torus_sPhi', "0", self._registry, False)
                            pDPhi = _defines.Expression(pvol_name + '_Torus_dPhi', '{}'.format(ppsChNodeTag.attributes['deltaphi'].value),self._registry, False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"
                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.TorusDimensions(pRMin,pRMax,pRTor,pSPhi, pDPhi, lunit, aunit)
                        elif ppsChNodeTag.tagName == "hype_dimensions":
                            innerRadius = _defines.Expression(pvol_name + '_Hype_rMin','{}'.format(ppsChNodeTag.attributes['rmin'].value), self._registry,False)
                            outerRadius = _defines.Expression(pvol_name + '_Hype_rMax','{}'.format(ppsChNodeTag.attributes['rmax'].value), self._registry,False)
                            innerStereo = _defines.Expression(pvol_name + '_Hype_iHst','{}'.format(ppsChNodeTag.attributes['inst'].value), self._registry,False)
                            outerStereo = _defines.Expression(pvol_name + '_Hype_ouSt','{}'.format(ppsChNodeTag.attributes['outst'].value), self._registry,False)
                            lenZ        = _defines.Expression(pvol_name + '_Hype_z','{}'.format(ppsChNodeTag.attributes['z'].value), self._registry,False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"
                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.HypeDimensions(innerRadius, outerRadius, innerStereo, outerStereo, lenZ, lunit, aunit)
                        elif ppsChNodeTag.tagName == "para_dimensions":
                            pX = _defines.Expression(pvol_name + '_Para_x','{}'.format(ppsChNodeTag.attributes['x'].value), self._registry,False)
                            pY = _defines.Expression(pvol_name + '_Para_y','{}'.format(ppsChNodeTag.attributes['y'].value), self._registry,False)
                            pZ = _defines.Expression(pvol_name + '_Para_z','{}'.format(ppsChNodeTag.attributes['z'].value), self._registry,False)
                            pAlpha = _defines.Expression(pvol_name + '_Para_alpha','{}'.format(ppsChNodeTag.attributes['alpha'].value), self._registry,False)
                            pTheta = _defines.Expression(pvol_name + '_Para_theta', '{}'.format(ppsChNodeTag.attributes['theta'].value),self._registry, False)
                            pPhi = _defines.Expression(pvol_name + '_Para_phi', '{}'.format(ppsChNodeTag.attributes['phi'].value),self._registry, False)
                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"

                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.ParaDimensions(pX, pY, pZ, pAlpha, pTheta, pPhi, lunit, aunit)
                        elif ppsChNodeTag.tagName == "trd_dimensions":
                            pX1 = _defines.Expression(pvol_name + '_Trd_x1','{}'.format(ppsChNodeTag.attributes['x1'].value), self._registry,False)
                            pX2 = _defines.Expression(pvol_name + '_Trd_x2','{}'.format(ppsChNodeTag.attributes['x2'].value), self._registry,False)
                            pY1 = _defines.Expression(pvol_name + '_Trd_y1','{}'.format(ppsChNodeTag.attributes['y1'].value), self._registry,False)
                            pY2 = _defines.Expression(pvol_name + '_Trd_y2','{}'.format(ppsChNodeTag.attributes['y2'].value), self._registry,False)
                            pZ = _defines.Expression(pvol_name + '_Trd_z','{}'.format(ppsChNodeTag.attributes['z'].value), self._registry,False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"

                            dim = _g4.ParameterisedVolume.TrdDimensions(pX1,pX2,pY1,pY2,pZ,lunit)
                        elif ppsChNodeTag.tagName == "trap_dimensions":
                            pDz = _defines.Expression(pvol_name + '_Trap_dz','{}'.format(ppsChNodeTag.attributes['z'].value), self._registry,False)
                            pTheta = _defines.Expression(pvol_name + '_Trap_dTheta','{}'.format(ppsChNodeTag.attributes['theta'].value), self._registry,False)
                            pDPhi = _defines.Expression(pvol_name + '_Trap_dPhi','{}'.format(ppsChNodeTag.attributes['phi'].value), self._registry,False)
                            pDy1 = _defines.Expression(pvol_name + '_Trap_dy1','{}'.format(ppsChNodeTag.attributes['y1'].value), self._registry,False)
                            pDx1 = _defines.Expression(pvol_name + '_Trap_dx1','{}'.format(ppsChNodeTag.attributes['x1'].value), self._registry,False)
                            pDx2 = _defines.Expression(pvol_name + '_Trap_dx2','{}'.format(ppsChNodeTag.attributes['x2'].value), self._registry,False)
                            pAlp1 = _defines.Expression(pvol_name + '_Trap_dAlp1','{}'.format(ppsChNodeTag.attributes['alpha1'].value), self._registry,False)
                            pDy2 = _defines.Expression(pvol_name + '_Trap_dy2','{}'.format(ppsChNodeTag.attributes['y2'].value), self._registry,False)
                            pDx3 = _defines.Expression(pvol_name + '_Trap_dy3','{}'.format(ppsChNodeTag.attributes['x3'].value), self._registry,False)
                            pDx4 = _defines.Expression(pvol_name + '_Trap_dx4','{}'.format(ppsChNodeTag.attributes['x4'].value), self._registry,False)
                            pAlp2 = _defines.Expression(pvol_name + '_Trap_dAlp2','{}'.format(ppsChNodeTag.attributes['alpha2'].value), self._registry,False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"
                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            dim = _g4.ParameterisedVolume.TrapDimensions(pDz, pTheta, pDPhi, pDy1, pDx1, pDx2, pAlp1, pDy2, pDx3, pDx4, pAlp2, lunit, aunit)
                        elif ppsChNodeTag.tagName == "polycone_dimensions":
                            startphi = _defines.Expression(pvol_name + '_Polycone_startphi','{}'.format(ppsChNodeTag.attributes['startPhi'].value), self._registry,False)
                            deltaphi = _defines.Expression(pvol_name + '_Polycone_deltaphi','{}'.format(ppsChNodeTag.attributes['openPhi'].value), self._registry,False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"
                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            # read layers
                            Rmin = []
                            Rmax = []
                            Z = []

                            i = 0
                            for ppsChNodeChildren in ppsChNodeTag.childNodes:
                                rmin = _defines.Expression(pvol_name + "_PolyconeZPlane"+str(i)+"_rmin",ppsChNodeChildren.attributes['rmin'].value, self._registry,False)
                                rmax = _defines.Expression(pvol_name + "_PolyconeZPlane"+str(i)+"_rmax",ppsChNodeChildren.attributes['rmax'].value, self._registry,False)
                                z = _defines.Expression(pvol_name + "_PolyconeZPlane"+str(i)+"_z", ppsChNodeChildren.attributes['z'].value,self._registry,False)
                                Rmin.append(rmin)
                                Rmax.append(rmax)
                                Z.append(z)
                            dim = _g4.ParameterisedVolume.PolyconeDimensions(startphi,deltaphi,Z,Rmin,Rmax,lunit,aunit)

                        elif ppsChNodeTag.tagName == "polyhedra_dimensions":
                            startphi = _defines.Expression(pvol_name + '_Polyhedra_startphi','{}'.format(ppsChNodeTag.attributes['startPhi'].value), self._registry,False)
                            deltaphi = _defines.Expression(pvol_name + '_Polyhedra_deltaphi','{}'.format(ppsChNodeTag.attributes['openPhi'].value), self._registry,False)
                            numsides = _defines.Expression(pvol_name + '_Polyhedra_numsides','{}'.format(ppsChNodeTag.attributes['numSide'].value), self._registry,False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"
                            if 'aunit' in ppsChNodeTag.attributes:
                                aunit = ppsChNodeTag.attributes['aunit'].value
                            else:
                                aunit = "rad"

                            # read layers
                            Rmin = []
                            Rmax = []
                            Z = []

                            i = 0
                            for ppsChNodeChildren in ppsChNodeTag.childNodes:
                                rmin = _defines.Expression(pvol_name + "_PolyhedraZPlane"+str(i)+"_rmin",ppsChNodeChildren.attributes['rmin'].value, self._registry,False)
                                rmax = _defines.Expression(pvol_name + "_PolyhedraZPlane"+str(i)+"_rmax",ppsChNodeChildren.attributes['rmax'].value, self._registry,False)
                                z = _defines.Expression(pvol_name + "_PolyhedraZPlane"+str(i)+"_z", ppsChNodeChildren.attributes['z'].value,self._registry,False)
                                Rmin.append(rmin)
                                Rmax.append(rmax)
                                Z.append(z)

                            dim = _g4.ParameterisedVolume.PolyhedraDimensions(startphi,deltaphi,numsides,Z,Rmin,Rmax,lunit,aunit)

                        elif ppsChNodeTag.tagName == "ellipsoid_dimensions":
                            pxSemiAxis = _defines.Expression(pvol_name + '_Ellipsoid_ax','{}'.format(ppsChNodeTag.attributes['ax'].value), self._registry,False)
                            pySemiAxis = _defines.Expression(pvol_name + '_Ellipsoid_by','{}'.format(ppsChNodeTag.attributes['by'].value), self._registry,False)
                            pzSemiAxis = _defines.Expression(pvol_name + '_Ellipsoid_cz','{}'.format(ppsChNodeTag.attributes['cz'].value), self._registry,False)
                            pzBottomCut = _defines.Expression(pvol_name + '_Ellipsoid_zcut1','{}'.format(ppsChNodeTag.attributes['zcut1'].value), self._registry,False)
                            pzTopCut = _defines.Expression(pvol_name + '_Ellipsoid_zcut2','{}'.format(ppsChNodeTag.attributes['zcut2'].value), self._registry,False)

                            if 'lunit' in ppsChNodeTag.attributes:
                                lunit = ppsChNodeTag.attributes['lunit'].value
                            else:
                                lunit = "mm"

                            dim = _g4.ParameterisedVolume.EllipsoidDimensions(pxSemiAxis,pySemiAxis,pzSemiAxis,pzBottomCut,pzTopCut,lunit)

                    transforms.append([rotation,position])
                    paramData.append(dim)

                # create parameterised volume
                _g4.ParameterisedVolume(pvol_name,
                                        self._registry.logicalVolumeDict[volref],
                                        vol,
                                        ncopies,
                                        paramData,
                                        transforms,
                                        self._registry,
                                        addRegistry=True)


            elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "divisionvol":
                volref    = chNode.getElementsByTagName("volumeref")[0].attributes["ref"].value

                # Name
                try:
                    pvol_name = chNode.attributes["name"].value
                except KeyError:
                    pvol_name = volref+"_DivisionPV"

                ax = chNode.attributes['axis'].value
                axes = {"kXAxis" : 1, "kYAxis" : 2,  "kZAxis" : 3, "kRho" : 4, "kPhi" : 5}
                axis = axes[ax]

                try:
                    offs = chNode.attributes["offset"].value
                except KeyError:
                    offs = 0
                offset = _defines.Expression(pvol_name+"_offset",
                                                offs, self._registry, False)

                try:
                    wdt = chNode.attributes["width"].value
                except KeyError:
                    wdt = -1
                width = _defines.Expression(pvol_name+"_width",
                                                wdt, self._registry, False)

                try:
                    num = chNode.attributes["number"].value
                except KeyError:
                    num = -1
                ndivisions = _defines.Expression(pvol_name+"_ndivisions",
                                                 num, self._registry, False)

                try:
                    unit = chNode.attributes["unit"].value
                except KeyError:
                    unit = "mm"

                rv = _g4.DivisionVolume(pvol_name,
                                       self._registry.logicalVolumeDict[volref],
                                       vol,
                                       axis,
                                       ndivisions,
                                       width,
                                       offset,
                                       self._registry,
                                       True,
                                       unit)
