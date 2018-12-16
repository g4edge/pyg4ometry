import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation   as _vtk
import numpy             as _np
import re as _re
from   xml.dom import minidom as _minidom
import warnings as _warnings
from   math import pi as _pi
from   ..geant4.Registry import registry as _registry

class ReaderNew(object) :

    def __init__(self, fileName, registryOn = True) :
        super(ReaderNew, self).__init__()
        self.filename   = fileName    
        self.registryOn = registryOn    

        if self.registryOn : 
            self.registry = _g4.Registry() 
        else :
            self.registry = _registry
        
        # load file
        self.load()

    def load(self) : 
        
        # open file 
        data  = open(self.filename)

        #remove all newline charecters and whitespaces outside tags
        fs = str()
        for l in data:
            l = l.strip()
            if(l.endswith(">")):
                end=""
            else:
                end=" "
            if(len(l) != 0):
                fs += (l+end)

        # parse xml
        xmldoc = _minidom.parseString(fs)

        # parse xml for defines, materials, solids and structure (#TODO optical surfaces?)
        self.parseDefines(xmldoc)
        self.parseMaterials(xmldoc)
        self.parseSolids(xmldoc)
        self.parseStructure(xmldoc)        
        
        data.close()

    def parseDefines(self, xmldoc) : 
        self.structure = xmldoc.getElementsByTagName("define")[0]

        for df in self.structure.childNodes :
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
                return (x,y,z)

            # parse matricies
            def getMatrix(def_attrs) :
                try : 
                    coldim = def_attrs['coldim']
                except KeyError : 
                    coldim = 0

                try : 
                    values = def_attrs['values'].split()
                except KeyError : 
                    values = []
                
                return (coldim, values)

            if(define_type == "constant"):
                value = def_attrs['value']
                _g4.GdmlDefines.Constant(name,value,self.registry)
            elif(define_type == "quantity"):
                value = def_attrs['value']
                unit  = def_attrs['unit']
                type  = def_attrs['type']
                _g4.GdmlDefines.Quantity(name,value,unit,type, self.registry)
            elif(define_type == "variable"):
                value = def_attrs['value']
                _g4.GdmlDefines.Variable(name,value, self.registry)
            elif(define_type == 'expression'):
                value = def_attrs['value']
                _g4.GdmlDefines.Expression(name,value, self.registry)                 
            elif(define_type == "position"):                
                (x,y,z) = getXYZ(def_attrs)
                _g4.GdmlDefines.Position(name,x,y,z,self.registry)
            elif(define_type == "rotation"):
                (x,y,z) = getXYZ(def_attrs)
                _g4.GdmlDefines.Rotation(name,x,y,z,self.registry)
            elif(define_type == "scale"):
                (x,y,z) = getXYZ(def_attrs)
                _g4.GdmlDefines.Scale(name,x,y,z, self.registry)                
            elif(define_type == "matrix"):
                (coldim, values) = getMatrix(def_attrs)
                _g4.GdmlDefines.Matrix(name,coldim,values, self.registry)
            else:
                print "Urecognised define: ", define_type
        pass

    def parseMaterials(self, xmldoc) : 
        pass

    def parseSolids(self,xmldoc) :
        pass

    def parseStructure(self,xmldoc) :
        pass
    
