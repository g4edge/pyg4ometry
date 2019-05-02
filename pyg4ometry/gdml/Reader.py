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

class Reader(object) :

    def __init__(self, fileName, registryOn = True) :
        super(Reader, self).__init__()
        self.filename   = fileName    
        self.registryOn = registryOn    

        if self.registryOn : 
            self._registry = _g4.Registry() 
        
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
                u = def_attrs.get("unit","none")
                return (x,y,z,u)

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
                _defines.Constant(name,value,self._registry)
            elif(define_type == "quantity"):
                value = def_attrs['value']
                unit  = def_attrs['unit']
                type  = def_attrs['type']
                _defines.Quantity(name,value,unit,type, self._registry)
            elif(define_type == "variable"):
                value = def_attrs['value']
                _defines.Variable(name,value, self._registry)
            elif(define_type == "expression"):
                value = df.childNodes[0].nodeValue
                _defines.Expression(name,value, self._registry)
            elif(define_type == "position"):                
                (x,y,z,u) = getXYZ(def_attrs)
                _defines.Position(name,x,y,z,u,self._registry)
            elif(define_type == "rotation"):
                (x,y,z,u) = getXYZ(def_attrs)
                _defines.Rotation(name,x,y,z,u,self._registry)
            elif(define_type == "scale"):
                (x,y,z,u) = getXYZ(def_attrs)
                _defines.Scale(name,x,y,z,u,self._registry)                
            elif(define_type == "matrix"):
                (coldim, values) = getMatrix(def_attrs)
                _defines.Matrix(name,coldim,values, self._registry)
            else:
                print "Unrecognised define: ", define_type

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
        try : 
            unit = node.attributes['unit'].value
        except KeyError : 
            unit = None
        
        if type == 'position' : 
            return _defines.Position(name,x,y,z,unit,self._registry,addRegistry) 
        elif type == 'positionref' :
            return self._registry.defineDict[node.attributes['ref'].value]
        elif type == 'rotation' :
            return _defines.Rotation(name,x,y,z,unit,self._registry,addRegistry)
        elif type == 'rotationref' :
            return self._registry.defineDict[node.attributes['ref'].value]
        elif type == 'scale' : 
            return _defines.Scale(name,x,y,z,self._registry,addRegistry)
        
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
        x = _defines.Expression(solid_name+'_pX','{}'.format(node.attributes['x'].value),self._registry)
        y = _defines.Expression(solid_name+'_pY','{}'.format(node.attributes['y'].value),self._registry)
        z = _defines.Expression(solid_name+'_pZ','{}'.format(node.attributes['z'].value),self._registry)
        try : 
            unit = node.attributes['unit'].value
        except KeyError : 
            unit = "mm"
              
        solid = _g4.solid.Box(solid_name,x,y,z,unit,self._registry)

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
        z    = _defines.Expression(solid_name+'_pDz','({})/2'.format(node.attributes['z'].value),self._registry)
        dphi = _defines.Expression(solid_name+'_pDPhi',node.attributes['deltaphi'].value,self._registry)

        try : 
            unit = node.attributes['unit'].value
        except KeyError : 
            unit = "mm"

        try : 
            aunit = node.attributes['aunit'].value
        except KeyError : 
            aunit = "rad"

        _g4.solid.Tubs(solid_name,rmin,rmax,z, sphi, dphi, unit, aunit, self._registry)


    def parseCutTube(self, node) : 
        solid_name = node.attributes['name'].value 

        try : 
            rmin = _defines.Expression(solid_name+'_pRMin',node.attributes['rmin'].value,self._registry)
        except KeyError : 
            rmin = _defines.Expression(solid_name+'_pRMin',"0",self._registry)
            
        rmax = _defines.Expression(solid_name+'_pRMax',node.attributes['rmax'].value,self._registry)
        dz   = _defines.Expression(solid_name+'_pDz','({})/2'.format(node.attributes['z'].value),self._registry)
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
        
        _g4.solid.CutTubs(solid_name, rmin, rmax, dz, sphi, dphi, lNorm, hNorm, self._registry) 
        

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
        dz    = _defines.Expression(solid_name+"_pDz","({})/2.0".format(node.attributes['z'].value),self._registry)
        dphi  = _defines.Expression(solid_name+"_pDPhi",node.attributes['deltaphi'].value,self._registry) 

        _g4.solid.Cons(solid_name, rmin1, rmax1, rmin2, rmax2, dz, sphi, dphi, self._registry)        

    def parsePara(self,node) : 
        solid_name = node.attributes['name'].value         

        x     = _defines.Expression(solid_name+'_pX',node.attributes['x'].value,self._registry) 
        y     = _defines.Expression(solid_name+'_pY',node.attributes['y'].value,self._registry) 
        z     = _defines.Expression(solid_name+'_pZ',node.attributes['z'].value,self._registry) 
        phi   = _defines.Expression(solid_name+'_pPhi',node.attributes['phi'].value,self._registry) 
        alpha = _defines.Expression(solid_name+'_pAlpha',node.attributes['alpha'].value,self._registry) 
        theta = _defines.Expression(solid_name+'_pTheta',node.attributes['theta'].value,self._registry) 

        _g4.solid.Para(solid_name, x, y, z, alpha, theta, phi, self._registry)

    def parseTrd(self, node) : 
        solid_name = node.attributes['name'].value
        
        x1 = _defines.Expression(solid_name+"_px1",node.attributes['x1'].value,self._registry)
        x2 = _defines.Expression(solid_name+"_px2",node.attributes['x2'].value,self._registry)
        y1 = _defines.Expression(solid_name+"_py1",node.attributes['y1'].value,self._registry)
        y2 = _defines.Expression(solid_name+"_py2",node.attributes['y2'].value,self._registry)
        z  = _defines.Expression(solid_name+"_z",node.attributes['z'].value,self._registry) 
        
        _g4.solid.Trd(solid_name, x1, x2, y1, y2, z, self._registry)

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

        _g4.solid.Trap(solid_name,dz,theta,dphi,dy1,dx1,dx2,alp1,dy2,dx3,dx4,alp2,self._registry)

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
            
        rmax       = _defines.Expression(solid_name+"_pRMax",node.attributes['rmax'].value,self._registry)
        deltaphi   = _defines.Expression(solid_name+"_pDPhi",node.attributes['deltaphi'].value,self._registry)
        deltatheta = _defines.Expression(solid_name+"_pDTheta",node.attributes['deltatheta'].value,self._registry)

        _g4.solid.Sphere(solid_name, rmin, rmax, startphi, deltaphi, starttheta, deltatheta, self._registry)

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

        _g4.solid.Torus(solid_name,rmin,rmax,rtor, sphi, dphi, self._registry) 


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

        _g4.solid.Polycone(solid_name, sphi, dphi, Z, Rmin, Rmax, self._registry)

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

        R = []
        Z = []

        i = 0
        for chNode in node.childNodes :
            r     = _defines.Expression(solid_name+"_rzpoint_r"+str(i),chNode.attributes['r'].value,self._registry)
            z     = _defines.Expression(solid_name+"_rzpoint_z"+str(i),chNode.attributes['z'].value,self._registry)
            R.append(r)
            Z.append(z)
            i+=1

        _g4.solid.GenericPolycone(solid_name, sphi, dphi, R, Z, self._registry)


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

        _g4.solid.Polyhedra(solid_name, sphi, dphi, nside, nzplane, Z, Rmin, Rmax, registry=self._registry)

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

        R = []
        Z = []
        
        i = 0
        for chNode in node.childNodes :
            r     = _defines.Expression(solid_name+"_rzpoint_r"+str(i),chNode.attributes['r'].value,self._registry)
            z     = _defines.Expression(solid_name+"_rzpoint_z"+str(i),chNode.attributes['z'].value,self._registry)
            R.append(r)
            Z.append(z)
            i+=1

        _g4.solid.GenericPolyhedra(solid_name, sphi, dphi, nside, R, Z, self._registry)

    def parseEllipticalTube(self, node) : 
        solid_name = node.attributes['name'].value
        
        dx = _defines.Expression(solid_name+"_dx",node.attributes['dx'].value,self._registry) 
        dy = _defines.Expression(solid_name+"_dy",node.attributes['dy'].value,self._registry) 
        dz = _defines.Expression(solid_name+"_dz",node.attributes['dz'].value,self._registry) 
    
        _g4.solid.EllipticalTube(solid_name,dx,dy,dz, self._registry)

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
        
        _g4.solid.Ellipsoid(solid_name, ax, by, cz, bcut, tcut, self._registry)

    def parseEllipticalCone(self, node) : 
        solid_name = node.attributes['name'].value 

        pxSemiAxis = _defines.Expression(solid_name+"_pxSemiAxis",node.attributes['dx'].value,self._registry)
        pySemiAxis = _defines.Expression(solid_name+"_pySemiAxis",node.attributes['dy'].value,self._registry)
        zMax       = _defines.Expression(solid_name+"_zMax",node.attributes['zmax'].value,self._registry)
        pzTopCut   = _defines.Expression(solid_name+"_pzTopCut",node.attributes['zcut'].value,self._registry)

        _g4.solid.EllipticalCone(solid_name,pxSemiAxis,pySemiAxis,zMax,pzTopCut,self._registry)

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
        halfLenZ    = _defines.Expression(solid_name+'_halfLenZ','({})/2'.format(node.attributes['z'].value),self._registry)

        _g4.solid.Hype(solid_name, innerRadius, outerRadius, innerStereo, outerStereo, halfLenZ, self._registry) 

    def parseTet(self, node) : 
        solid_name = node.attributes['name'].value         
        
        anchor = _defines.Expression(solid_name+'_anchor',node.attributes['vertex1'].value,self._registry)
        p2     = _defines.Expression(solid_name+'_p2',node.attributes['vertex2'].value,self._registry)
        p3     = _defines.Expression(solid_name+'_p3',node.attributes['vertex3'].value,self._registry)
        p4     = _defines.Expression(solid_name+'_p4',node.attributes['vertex4'].value,self._registry)

        _g4.solid.Tet(solid_name, anchor, p2, p3, p4, self._registry, False)
        
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

        _g4.solid.ExtrudedSolid(solid_name, pPolygon, zSection,self._registry)
        # print 'extruded solid NOT IMPLEMENTED'

    def parseTwistedBox(self, node) :
        solid_name = node.attributes['name'].value

        twistedAngle = _defines.Expression(solid_name+'_PhiTwist',node.attributes['PhiTwist'].value,self._registry)
        x = _defines.Expression(solid_name+'_x',node.attributes['x'].value,self._registry)
        y = _defines.Expression(solid_name+'_y',node.attributes['y'].value,self._registry)
        z    = _defines.Expression(solid_name+'_z',node.attributes['z'].value,self._registry)

        _g4.solid.TwistedBox(solid_name, twistedAngle, x, y, z, self._registry)

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

        _g4.solid.TwistedTrap(solid_name, twistedAngle, z, Theta, Phi, y1,
                              x1, x2, y2, x3, x4, Alph, self._registry)


    def parseTwistedTrd(self, node) :
        solid_name = node.attributes['name'].value

        twistedAngle = _defines.Expression(solid_name+'_PhiTwist',node.attributes['PhiTwist'].value,self._registry)
        x1 = _defines.Expression(solid_name+'_x1',node.attributes['x1'].value,self._registry)
        x2 = _defines.Expression(solid_name+'_x2',node.attributes['x2'].value,self._registry)
        y1 = _defines.Expression(solid_name+'_y1',node.attributes['y1'].value,self._registry)
        y2 = _defines.Expression(solid_name+'_y2',node.attributes['y2'].value,self._registry)
        z    = _defines.Expression(solid_name+'_z',node.attributes['z'].value,self._registry)

        _g4.solid.TwistedTrd(solid_name, twistedAngle, x1, x2, y1, y2, z, self._registry)

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

        _g4.solid.TwistedTubs(solid_name, inner_rad, outer_rad, zlen, phi, twist, self._registry)

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

        dz = _defines.Expression(solid_name+"_dz",node.attributes["dz"].value,self._registry)
        args.extend([dz, self._registry])

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
        
        _g4.solid.TessellatedSolid(solid_name, facet_list, self._registry)        
        
    def parseUnion(self, node) : 
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError : 
            position   = _defines.Position("zero","0","0","0","mm",self._registry,False)            
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            rotation   = _defines.Rotation("indentity","0","0","0","rad",self._registry,False)
        
        _g4.solid.Union(solid_name, first, second,[rotation,position],self._registry)  

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
                rotation = self.parseVector(node.getElementsByTagName("rotation")[0], "rotation", False)
            except IndexError:
                rotation   = _defines.Rotation("identity","0","0","0","rad",self._registry,False)

        _g4.solid.Subtraction(solid_name, first, second,[rotation,position],self._registry)

    def parseIntersection(self, node) :
        solid_name = node.attributes['name'].value
        first      = node.getElementsByTagName("first")[0].attributes['ref'].value
        second     = node.getElementsByTagName("second")[0].attributes['ref'].value
        try : 
            position   = self.parseVector(node.getElementsByTagName("position")[0],"position",False)
        except IndexError : 
            position   = _defines.Position("zero","0","0","0","mm",self._registry,False)            
        try : 
            rotation   = self.parseVector(node.getElementsByTagName("rotation")[0],"rotation",False)
        except IndexError : 
            rotation   = _defines.Rotation("indentity","0","0","0","rad",self._registry,False)

        _g4.solid.Intersection(solid_name, first, second,[rotation,position],self._registry)

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
        self._registry.orderLogicalVolumes(worldLvName)
        self._registry.setWorld(worldLvName)

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
        

                vol = _g4.LogicalVolume(self._registry.solidDict[solid], 'G4_Galactic', name, registry=self._registry)
                
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
                            position = self._registry.defineDict[chNode.getElementsByTagName("positionref")[0].attributes["ref"].value]
                        except IndexError : 
                            try : 
                                position = self.parseVector(chNode.getElementsByTagName("position")[0],"position",False)
                            except IndexError : 
                                position = _defines.Position(pvol_name,"0","0","0","mm",self._registry,False)

                        # Rotation
                        _log.info('Reader.extractStructureNodeData> pv rotation %s',pvol_name)
                        try : 
                            rotation = self._registry.defineDict[chNode.getElementsByTagName("rotationref")[0].attributes["ref"].value]
                        except IndexError : 
                            try : 
                                rotation = self.parseVector(chNode.getElementsByTagName("rotation")[0],"rotation",False)  
                            except IndexError : 
                                rotation = _defines.Rotation(pvol_name,"0","0","0","rad",self._registry,False)

                        # Scale 
                        _log.info('Reader.extractStructureNodeData> pv scale %s ' % (pvol_name))
                        try :                             
                            scale = self._registry.defineDict[chNode.getElementsByTagName("scaleref")[0].attributes["ref"].value]
                        except IndexError : 
                            try : 
                                scale = self.parseVector(chNode.getElementsByTagName("scale")[0],"scale",False)
                            except IndexError : 
                                scale = _defines.Scale("","1","1","1","none",self._registry,False)    

                        # Create physical volume
                        _log.info('Reader.extractStructureNodeData> construct % s' % (pvol_name))

                        physvol   = _g4.PhysicalVolume(rotation, position, self._registry.logicalVolumeDict[volref],
                                                       pvol_name, vol, registry=self._registry)

                    elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "replicavol" : 
                        print 'Reader> replica not implemented'                                        
                    elif chNode.nodeType == node.ELEMENT_NODE and chNode.tagName == "paramvol":
                        print 'Reader> param not implemented'                                        

                # now logical is complete, check for overlaps
                vol.checkOverlaps()

            elif node_name == "loop" : 
                print 'Reader> loop not implemented'                
            elif node_name == "assembly" :
                print 'Reader> assembly not implemented'
            elif node_name == "bordersurface":
                print 'Reader> bordersurface not implemented'
            elif node_name == "skinsurface" : 
                print 'Reader> skinsurface not implemented'

            else:
                print "Unrecognised node: ", node_name

    def parseUserAuxInformation(self,xmldoc) :
        pass

    
    def extractUserAuxInformationNodeData(self,xmldoc) : 
        pass
