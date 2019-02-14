import numpy                             as _np
import re                                as _re
from   xml.dom import minidom            as _minidom
import xml.parsers.expat                 as _expat
import warnings                          as _warnings
from   math import pi                    as _pi
import Defines                           as _defines
import logging                           as _log

import pyg4ometry.geant4                          as _g4
import pyg4ometry.visualisation                   as _vtk
from   pyg4ometry.geant4.Registry import registry as _registry
from   pyg4ometry.geant4 import Expression        as _Expression

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

        _log.info('Reader.load>')
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
        _log.info('Reader.load> minidom parse')
        try :
            xmldoc = _minidom.parseString(fs)
        except _expat.ExpatError as ee : 
            print ee.args
            print ee.args[0]
            column = int(ee.args[0].split()[-1])
            print column,fs[column-10:min(len(fs),column+100)]
            print "        ^^^^ "
        _log.info('Reader.load> parse')
        # parse xml for defines, materials, solids and structure (#TODO optical surfaces?)
        self.parseDefines(xmldoc)
        self.parseMaterials(xmldoc)
        self.parseSolids(xmldoc)
        self.parseStructure(xmldoc)
        self.parseUserAuxInformation(xmldoc)
        
        
        data.close()

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
                _defines.Constant(name,value,self.registry)
            elif(define_type == "quantity"):
                value = def_attrs['value']
                unit  = def_attrs['unit']
                type  = def_attrs['type']
                _defines.Quantity(name,value,unit,type, self.registry)
            elif(define_type == "variable"):
                value = def_attrs['value']
                _defines.Variable(name,value, self.registry)
            elif(define_type == "expression"):
                value = df.childNodes[0].nodeValue
                _defines.Expression(name,value, self.registry)
            elif(define_type == "position"):                
                (x,y,z) = getXYZ(def_attrs)
                _defines.Position(name,x,y,z,self.registry)
            elif(define_type == "rotation"):
                (x,y,z) = getXYZ(def_attrs)
                _defines.Rotation(name,x,y,z,self.registry)
            elif(define_type == "scale"):
                (x,y,z) = getXYZ(def_attrs)
                _defines.Scale(name,x,y,z, self.registry)                
            elif(define_type == "matrix"):
                (coldim, values) = getMatrix(def_attrs)
                _defines.Matrix(name,coldim,values, self.registry)
            else:
                print "Urecognised define: ", define_type

        pass

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
        
        if type == 'position' : 
            return _defines.Position(name,x,y,z,self.registry,addRegistry) 
        elif type == 'rotation' : 
            return _defines.Rotation(name,x,y,z,self.registry,addRegistry)
        elif type == 'scale' : 
            return _defines.Scale(name,x,y,z,self.registry,addRegistry)
        
    def parseMatrix(self, node) : 
        pass

    def parseMaterials(self, xmldoc) : 
        pass

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
            else : 
                print solid_type, node.attributes['name'].value

    def parseBox(self, node) : 
        solid_name = node.attributes['name'].value 
        x = _defines.Expression(solid_name+'_pX','({})/2'.format(node.attributes['x'].value),self.registry)
        y = _defines.Expression(solid_name+'_pY','({})/2'.format(node.attributes['y'].value),self.registry)
        z = _defines.Expression(solid_name+'_pZ','({})/2'.format(node.attributes['z'].value),self.registry)
                
        solid = _g4.solid.Box(solid_name,x,y,z,self.registry)

    def parseTube(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            rmin = _defines.Expression(solid_name+'_pRMin',node.attributes['rmin'].value,self.registry)
        except KeyError :
            rmin = _defines.Expression(solid_name+'_pRMin',"0",self.registry)
        try : 
            sphi = _defines.Expression(solid_name+'_pSPhi',node.attributes['startphi'].value,self.registry)
        except KeyError : 
            sphi = _defines.Expression(solid_name+'_pSPhi',"0",self.registry)

        rmax = _defines.Expression(solid_name+'_pRMax',node.attributes['rmax'].value,self.registry)
        z    = _defines.Expression(solid_name+'_pDz','({})/2'.format(node.attributes['z'].value),self.registry)
        dphi = _defines.Expression(solid_name+'_pDPhi',node.attributes['deltaphi'].value,self.registry)

        _g4.solid.Tubs(solid_name,rmin,rmax,z, sphi, dphi, self.registry)


    def parseCutTube(self, node) : 
        solid_name = node.attributes['name'].value 
        
        try : 
            rmin = _defines.Expression(solid_name+'_pRMin',node.attributes['rmin'].value,self.registry)
        except KeyError : 
            rmin = _defines.Expression(solid_name+'_pRMin',"0",self.registry)
            
        rmax = _defines.Expression(solid_name+'_pRMax',node.attributes['rmax'].value,self.registry)
        dz   = _defines.Expression(solid_name+'_pDz','({})/2'.format(node.attributes['z'].value),self.registry)
        try : 
            sphi = _defines.Expression(solid_name+'_pSPhi',node.attributes['startphi'].value,self.registry)
        except KeyError :
            sphi = _defines.Expression(solid_name+'_pSPhi',"0",self.registry)
        
        dphi = _defines.Expression(solid_name+'_pDPhi',node.attributes['deltaphi'].value,self.registry)
        lx   = _defines.Expression(solid_name+'_plNorm_x',node.attributes['lowX'].value,self.registry)
        ly   = _defines.Expression(solid_name+'_plNorm_y',node.attributes['lowY'].value,self.registry)
        lz   = _defines.Expression(solid_name+'_plNorm_z',node.attributes['lowZ'].value,self.registry)
        hx   = _defines.Expression(solid_name+'_phNorm_x',node.attributes['highX'].value,self.registry)
        hy   = _defines.Expression(solid_name+'_phNorm_y',node.attributes['highY'].value,self.registry)
        hz   = _defines.Expression(solid_name+'_phNorm_z',node.attributes['highZ'].value,self.registry)

        lNorm = [lx, ly, lz] 
        hNorm = [hx, hy, hz]
        
        _g4.solid.CutTubs(solid_name, rmin, rmax, dz, sphi, dphi, lNorm, hNorm, self.registry) 
        

    def parseCone(self,node) : 
        solid_name = node.attributes['name'].value         

        try : 
            rmin1 = _defines.Expression(solid_name+"_pRMin1",node.attributes['rmin1'].value,self.registry) 
        except KeyError : 
            rmin1 = _defines.Expression(solid_name+"_pRMin1","0",self.registry) 
        try :
            rmin2 = _defines.Expression(solid_name+"_pRMin2",node.attributes['rmin2'].value,self.registry) 
        except KeyError : 
            rmin2 = _defines.Expression(solid_name+"_pRMin2","0",self.registry) 
        try :
            sphi  = _defines.Expression(solid_name+"_pSPhi",node.attributes['startphi'].value,self.registry) 
        except KeyError : 
            sphi  = _defines.Expression(solid_name+"_pSPhi","0",self.registry) 

        rmax1 = _defines.Expression(solid_name+"_pRMax1",node.attributes['rmax1'].value,self.registry) 
        rmax2 = _defines.Expression(solid_name+"_pRMax2",node.attributes['rmax2'].value,self.registry) 
        dz    = _defines.Expression(solid_name+"_pDz","({})/2.0".format(node.attributes['z'].value),self.registry)
        dphi  = _defines.Expression(solid_name+"_pDPhi",node.attributes['deltaphi'].value,self.registry) 

        _g4.solid.Cons(solid_name, rmin1, rmax1, rmin2, rmax2, dz, sphi, dphi, self.registry)        

    def parsePara(self,node) : 
        solid_name = node.attributes['name'].value         

        x     = _defines.Expression(solid_name+'_pX',node.attributes['x'].value,self.registry) 
        y     = _defines.Expression(solid_name+'_pY',node.attributes['y'].value,self.registry) 
        z     = _defines.Expression(solid_name+'_pZ',node.attributes['z'].value,self.registry) 
        phi   = _defines.Expression(solid_name+'_pPhi',node.attributes['phi'].value,self.registry) 
        alpha = _defines.Expression(solid_name+'_pAlpha',node.attributes['alpha'].value,self.registry) 
        theta = _defines.Expression(solid_name+'_pTheta',node.attributes['theta'].value,self.registry) 

        solid = _g4.solid.Para(solid_name, x, y, z, alpha, theta, phi, self.registry)

    def parseTrd(self, node) : 
        solid_name = node.attributes['name'].value
        
        x1 = _defines.Expression(solid_name+"_px1",node.attributes['x1'].value,self.registry)
        x2 = _defines.Expression(solid_name+"_px2",node.attributes['x2'].value,self.registry)
        y1 = _defines.Expression(solid_name+"_py1",node.attributes['y1'].value,self.registry)
        y2 = _defines.Expression(solid_name+"_py2",node.attributes['y2'].value,self.registry)
        z  = _defines.Expression(solid_name+"_z",node.attributes['z'].value,self.registry) 
        
        _g4.solid.Trd(solid_name, x1, x2, y1, y2, z, self.registry)

    def parseTrap(self, node) : 
        solid_name = node.attributes['name'].value
        
        dz    = _defines.Expression(solid_name+"_pDz",node.attributes['z'].value,self.registry)
        theta = _defines.Expression(solid_name+"_pTheta",node.attributes['theta'].value,self.registry) 
        dphi  = _defines.Expression(solid_name+"_pDphi",node.attributes['phi'].value,self.registry)
        dx1   = _defines.Expression(solid_name+"_pDx1",node.attributes['x1'].value,self.registry)
        dx2   = _defines.Expression(solid_name+"_pDx2",node.attributes['x2'].value,self.registry)
        dx3   = _defines.Expression(solid_name+"_pDx3",node.attributes['x3'].value,self.registry)
        dx4   = _defines.Expression(solid_name+"_pDx4",node.attributes['x4'].value,self.registry)
        dy1   = _defines.Expression(solid_name+"_pDy1",node.attributes['y1'].value,self.registry)
        dy2   = _defines.Expression(solid_name+"_pDy2",node.attributes['y2'].value,self.registry)
        alp1  = _defines.Expression(solid_name+"_pAlp1",node.attributes['alpha1'].value,self.registry)
        alp2  = _defines.Expression(solid_name+"_pAlp2",node.attributes['alpha2'].value,self.registry)

        _g4.solid.Trap(solid_name,dz,theta,dphi,dy1,dx1,dx2,alp1,dy2,dx3,dx4,alp2,self.registry)

    def parseSphere(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            rmin = _defines.Expression(solid_name+"_pRMin",node.attributes['rmin'].value,self.registry) 
        except KeyError : 
            rmin = _defines.Expression(solid_name+"_pRMin","0",self.registry)
        try : 
            startphi = _defines.Expression(solid_name+"_pSPhi",node.attributes['startphi'].value,self.registry) 
        except KeyError : 
            startphi = _defines.Expression(solid_name+"_pSPhi","0",self.registry) 
        try : 
            starttheta = _defines.Expression(solid_name+"_pSTheta",node.attributes['starttheta'].value,self.registry)
        except KeyError : 
            starttheta = _defines.Expression(solid_name+"_pSTheta","0",self.registry)
            
        rmax       = _defines.Expression(solid_name+"_pRMax",node.attributes['rmax'].value,self.registry)
        deltaphi   = _defines.Expression(solid_name+"_pDPhi",node.attributes['deltaphi'].value,self.registry)
        deltatheta = _defines.Expression(solid_name+"_pDTheta",node.attributes['deltatheta'].value,self.registry)

        _g4.solid.Sphere(solid_name, rmin, rmax, startphi, deltaphi, starttheta, deltatheta, self.registry)

    def parseOrb(self, node) : 
        solid_name = node.attributes['name'].value 
        
        r = _defines.Expression(solid_name+"_pRMax",node.attributes['r'].value,self.registry)
        
        _g4.solid.Orb(solid_name,r,self.registry)

    def parseTorus(self, node) : 
        solid_name = node.attributes['name'].value 

        rmin = _defines.Expression(solid_name+"_pRmin",node.attributes['rmin'].value,self.registry)
        rmax = _defines.Expression(solid_name+"_pRmax",node.attributes['rmax'].value,self.registry)
        rtor = _defines.Expression(solid_name+"_pRtor",node.attributes['rtor'].value,self.registry)
        sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self.registry) 
        dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self.registry)

        _g4.solid.Torus(solid_name,rmin,rmax,rtor, sphi, dphi, self.registry) 


    def parsePolycone(self, node) : 
        solid_name = node.attributes['name'].value         

        sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self.registry)
        dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self.registry)
        try : 
            nzpl = _defines.Expression(solid_name+"_pZpl",node.attributes['nzplanes'].value,self.registry)
        except KeyError :
            nzpl = _defines.Expression(solid_name+"_pZpl","0",self.registry)            

        Rmin = [] 
        Rmax = []
        Z    = [] 
        
        i = 0
        for chNode in node.childNodes : 
            rmin  = _defines.Expression(solid_name+"_zplane_rmin"+str(i),chNode.attributes['rmin'].value,self.registry)
            rmax  = _defines.Expression(solid_name+"_zplane_rmax"+str(i),chNode.attributes['rmax'].value,self.registry)
            z     = _defines.Expression(solid_name+"_zplane_z"+str(i),chNode.attributes['z'].value,self.registry)
            Rmin.append(rmin)
            Rmax.append(rmax)
            Z.append(z)
            i=i+1

        _g4.solid.Polycone(solid_name, sphi,dphi,Z, Rmin, Rmax, self.registry)

    def parseGenericPolycone(self, node) : 
        solid_name = node.attributes['name'].value
        
        sphi = _defines.Expression(solid_name+"_pSphi",node.attributes['startphi'].value,self.registry)
        dphi = _defines.Expression(solid_name+"_pDphi",node.attributes['deltaphi'].value,self.registry)

        R = []
        Z = []
        
        i = 0
        for chNode in node.childNodes : 
            r     = _defines.Expression(solid_name+"_rzpoint_r"+str(i),chNode.attributes['r'].value,self.registry)
            z     = _defines.Expression(solid_name+"_rzpoint_z"+str(i),chNode.attributes['z'].value,self.registry)
            R.append(r)
            Z.append(z)
            i=i+1
        
        print 'generic polycone NOT IMPLEMENTED'

    def parsePolyhedra(self, node) :
        solid_name = node.attributes['name'].value        

        print 'polyhedra NOT IMPLEMENTED'        

    def parseGenericPolyhedra(self, node) :
        solid_name = node.attributes['name'].value        

        print 'generic polyhedra NOT IMPLEMENTED'        

    def parseEllipticalTube(self, node) : 
        solid_name = node.attributes['name'].value
        
        dx = _defines.Expression(solid_name+"_dx",node.attributes['dx'].value,self.registry) 
        dy = _defines.Expression(solid_name+"_dy",node.attributes['dy'].value,self.registry) 
        dz = _defines.Expression(solid_name+"_dz",node.attributes['dz'].value,self.registry) 
    
        _g4.solid.EllipticalTube(solid_name,dx,dy,dz, self.registry)

    def parseEllipsoid(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            bcut = _defines.Expression(solid_name+"_zcut1",node.attributes['zcut1'].value,self.registry)
        except KeyError :
            bcut = _defines.Expression(solid_name+"_zcut1","-1E20",self.registry)

        ax   = _defines.Expression(solid_name+"_ax",node.attributes['ax'].value,self.registry)
        by   = _defines.Expression(solid_name+"_by",node.attributes['by'].value,self.registry)
        cz   = _defines.Expression(solid_name+"_cz",node.attributes['cz'].value,self.registry)
        tcut = _defines.Expression(solid_name+"_zcut2",node.attributes['zcut2'].value,self.registry) 
        
        _g4.solid.Ellipsoid(solid_name, ax, by, cz, bcut, tcut, self.registry)

    def parseEllipticalCone(self, node) : 
        solid_name = node.attributes['name'].value 

        pxSemiAxis = _defines.Expression(solid_name+"_pxSemiAxis",node.attributes['dx'].value,self.registry)
        pySemiAxis = _defines.Expression(solid_name+"_pySemiAxis",node.attributes['dy'].value,self.registry)
        zMax       = _defines.Expression(solid_name+"_zMax",node.attributes['zmax'].value,self.registry)
        pzTopCut   = _defines.Expression(solid_name+"_pzTopCut",node.attributes['zcut'].value,self.registry)

        _g4.solid.EllipticalCone(solid_name,pxSemiAxis,pySemiAxis,zMax,pzTopCut,self.registry)

    def parseParaboloid(self, node) : 
        solid_name = node.attributes['name'].value 

        Dz         = _defines.Expression(solid_name+"_Dz",'({})/2'.format(node.attributes['dz'].value),self.registry)
        R1         = _defines.Expression(solid_name+"_R1",node.attributes['rlo'].value,self.registry)
        R2         = _defines.Expression(solid_name+"_R2",node.attributes['rhi'].value,self.registry)
        
        _g4.solid.Paraboloid(solid_name, Dz, R1, R2, self.registry)
        
    def parseHype(self, node) : 
        solid_name = node.attributes['name'].value         
        
        try : 
            innerStereo = _defines.Expression(solid_name+'_innerStereo',node.attributes['ihst'].value,self.registry) 
        except KeyError : 
            innerStereo = _defines.Expression(solid_name+'_innerStereo',"0",self.registry)             

        innerRadius = _defines.Expression(solid_name+'_innerRadius',node.attributes['rmin'].value,self.registry) 
        outerRadius = _defines.Expression(solid_name+'_outerRadius',node.attributes['rmax'].value,self.registry)
        outerStereo = _defines.Expression(solid_name+'_outerStereo',node.attributes['outst'].value,self.registry) 
        halfLenZ    = _defines.Expression(solid_name+'_halfLenZ','({})/2'.format(node.attributes['z'].value),self.registry)

        _g4.solid.Hype(solid_name, innerRadius, outerRadius, innerStereo, outerStereo, halfLenZ, self.registry) 

    def parseTet(self, node) : 
        solid_name = node.attributes['name'].value         
        
        anchor = _defines.Expression(solid_name+'_anchor',node.attributes['vertex1'],self.registry)
        p2     = _defines.Expression(solid_name+'_p2',node.attributes['vertex2'],self.registry)
        p3     = _defines.Expression(solid_name+'_p3',node.attributes['vertex3'],self.registry)
        p4     = _defines.Expression(solid_name+'_p4',node.attributes['vertex4'],self.registry)

        _g4.solid.Tet(solid_name, anchor, p2, p3, p4, False, self.registry)
        
    def parseExtrudedSolid(self, node) : 
        solid_name = node.attributes['name'].value
                               
        print 'extruded solid NOT IMPLEMENTED'

    def parseTwistedBox(self, node) : 
        solid_name = node.attributes['name'].value 

        print 'twisted box NOT IMPLEMENTED'        

    def parseTwistedTrap(self, node) : 
        solid_name = node.attributes['name'].value 

        print 'twisted trap NOT IMPLEMENTED'        

    def parseTwistedTrd(self, node) : 
        solid_name = node.attributes['name'].value 
    
        print 'twisted trd NOT IMPLEMENTED'        

    def parseTwistedTubs(self,node) : 
        solid_name = node.attributes['name'].value         

        print 'twisted tubs NOT IMPLEMENTED'        

    def parseGenericTrap(self,node) : 
        solid_name = node.attributes['name'].value         

        print 'generic trap NOT IMPLEMENTED'        

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
        
        _g4.solid.TessellatedSolid(solid_name, facet_list, self.registry)        
        
    def parseUnion(self, node) : 
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError : 
            position   = _defines.Position("zero","0","0","0",self.registry,False)            
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            rotation   = _defines.Rotation("indentity","0","0","0",self.registry,False)
        
        _g4.solid.Union(solid_name, first, second,[rotation,position],self.registry)  

    def parseSubtraction(self, node) : 
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError : 
            position   = _defines.Position("zero","0","0","0",self.registry,False)            
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            rotation   = _defines.Rotation("indentity","0","0","0",self.registry,False)

        _g4.solid.Subtraction(solid_name, first, second,[rotation,position],self.registry)

    def parseIntersection(self, node) :
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError : 
            position   = _defines.Position("zero","0","0","0",self.registry,False)            
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            rotation   = _defines.Rotation("indentity","0","0","0",self.registry,False)

        _g4.solid.Intersection(solid_name, first, second,[rotation,position],self.registry)

    def parseMultiUnion(self, node) :
        solid_name = node.attributes['name'].value

        print 'multiunion NOT IMPLEMENTED'

    def parseStructure(self,xmldoc) :
        
        self.xmlstructure = xmldoc.getElementsByTagName("structure")[0]
        
        # loop over child nodes 
        for node in self.xmlstructure.childNodes :
            self.extractStructureNodeData(node)

        # find world logical volume 
        self.xmlsetup = xmldoc.getElementsByTagName("setup")[0]
        worldLvName = self.xmlsetup.childNodes[0].attributes["ref"].value
        self.registry.orderLogicalVolumes(worldLvName)
        self.registry.setWorld(worldLvName)

    def extractStructureNodeData(self, node) : 
        node_name = node.tagName 
        
        if node.nodeType == node.ELEMENT_NODE : 
            if node_name == "volume" :
                name      = node.attributes["name"].value
                material  = node.getElementsByTagName("materialref")[0].attributes["ref"].value
                solid     = node.getElementsByTagName("solidref")[0].attributes["ref"].value
                
#               determine material                               
#                if material in _g4.registry.materialDict:
#                    mat = _g4.registry.materialDict[material]
#                else:
#                    mat = str(material)
        
                vol = _g4.LogicalVolume(self.registry.solidDict[solid], 'G4_Galactic', name, registry=self.registry)

                for chNode in node.childNodes :
                    if chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "physvol" :
                        volref    = chNode.getElementsByTagName("volumeref")[0].attributes["ref"].value

                        # Name 
                        try : 
                            pvol_name = chNode.attributes["name"].value
                        except KeyError : 
                            pvol_name = volref+"_PV"
                            
                        _log.info('Reader.extractStructureNodeData> %s' % (pvol_name))
                            
                        # Position 
                        _log.info('Reader.extractStructureNodeData> pv position %s' % (pvol_name))

                        try : 
                            position = self.registry.defineDict[chNode.getElementsByTagName("positionref")[0].attributes["ref"].value]
                        except IndexError : 
                            try : 
                                position = self.parseVector(chNode.getElementsByTagName("position")[0],"position",False)
                            except IndexError : 
                                position = _defines.Position(pvol_name,"0","0","0",self.registry,False)

                        # Rotation
                        _log.info('Reader.extractStructureNodeData> pv rotation %s',pvol_name)
                        try : 
                            rotation = self.registry.defineDict[chNode.getElementsByTagName("rotationref")[0].attributes["ref"].value]
                        except IndexError : 
                            try : 
                                rotation = self.parseVector(chNode.getElementsByTagName("rotation")[0],"rotation",False)  
                            except IndexError : 
                                rotation = _defines.Rotation(pvol_name,"0","0","0",self.registry,False)

                        # Scale 
                        _log.info('Reader.extractStructureNodeData> pv scale %s ' % (pvol_name))
                        try :                             
                            scale = self.registry.defineDict[chNode.getElementsByTagName("scaleref")[0].attributes["ref"].value]                            
                        except IndexError : 
                            try : 
                                scale = self.parseVector(chNode.getElementsByTagName("scale")[0],"scale",False)
                            except IndexError : 
                                scale = _defines.Scale("","1","1","1",self.registry,False)    

                        # Create physical volume
                        _log.info('Reader.extractStructureNodeData> construct % s' % (pvol_name))
                        physvol   = _g4.PhysicalVolume(rotation, position, self.registry.logicalVolumeDict[volref],
                                                       pvol_name, vol, scale, registry=self.registry)

                    elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "replicavol" : 
                        print 'ReaderNew> replica not implemented'                                        
                    elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "paramvol":
                        print 'ReaderNew> param not implemented'                                        
            elif node_name == "loop" : 
                print 'ReaderNew> loop not implemented'                
            elif node_name == "assembly" :
                print 'ReaderNew> assembly not implemented'
            elif node_name == "bordersurface":
                print 'ReaderNew> bordersurface not implemented'
            elif node_name == "skinsurface" : 
                print 'ReaderNew> skinsurface not implemented'

            else:
                print "Unrecognised node: ", node_name

    def parseUserAuxInformation(self,xmldoc) :
        pass

    
    def extractUserAuxInformationNodeData(self,xmldoc) : 
        pass
