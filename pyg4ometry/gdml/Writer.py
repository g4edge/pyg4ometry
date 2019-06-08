from xml.dom import minidom as _minidom
from xml.dom import getDOMImplementation
from ..geant4.Material import Material as _Material
from ..geant4.Material import Element as _Element
from ..geant4.Material import Isotope as _Isotope
from ..gdml import Defines as _Defines
import Expression as _Expression
import pyg4ometry.geant4 as _g4
import logging as _log

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
        self.setup     = self.top.appendChild(self.doc.createElement('setup'))

        self.materials_written = []

        self.defineList        = []
        self.materialList      = []
        self.solidList         = []
        self.logicalVolumeList = []
        self.physicalVolumeList= []

    def addDetector(self, registry) :
        self.registry = registry

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
        for logicalName in registry.logicalVolumeList  :
            _log.info('gdml.Writer.addDetector> logical '+logicalName)
            logical = registry.logicalVolumeDict[logicalName]
            if logical.type == "placement" : 
                self.writeLogicalVolume(logical)
                self.writeMaterial(logical.material)
            elif logical.type == "assembly" : 
                self.writeAssemblyVolume(logical)


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

    def writeGmadTester(self, filenameGmad, filenameGDML, writeDefaultLattice=False, zLength=None, preprocessGDML=True):
        if writeDefaultLattice:
            self.writeDefaultLattice()

        s = 'e1: element, geometry="gdml:'
        s += str(filenameGDML)
        if self.registry.parameterDict.has_key("GDML_Size_position_z"):
            s += '", l=' + str(self.registry.parameterDict['GDML_Size_position_z'].value) + '*mm;\n'
        else:
            # be super tolerant incase the meshing fails - still write out
            try:
                ext = self.registry.worldVolume.mesh.extent
                dz = ext[1][2] - ext[0][2]
                s += '", l=' + str(dz) + '*mm;\n'
            except IndexError:
                s += '", l=20*m;\n'
        s += 'l1: line = (e1);\n'
        s += 'use,period=l1;\n'
        s += 'sample,all;\n'
        s += 'beam, particle="e-",\n'
        s += 'energy=250.0*GeV;\n'
        if not preprocessGDML:
            s += "option, preprocessGDML=0;"
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
            oe.setAttribute('unit',define.unit)
            oe.setAttribute('type',define.type)
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Variable):
            oe = self.doc.createElement('variable')
            oe.setAttribute('name',define.name)
            oe.setAttribute('value',str(define.expr.expression))
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Position):
            oe = self.doc.createElement('position')
            oe.setAttribute('name',define.name)
            oe.setAttribute('x',str(define.x.expression))
            oe.setAttribute('y',str(define.y.expression))
            oe.setAttribute('z',str(define.z.expression))
            #oe.setAttribute('unit', str(define.unit)) #TODO: Units not handled by position right now
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Rotation):
            oe = self.doc.createElement('rotation')
            oe.setAttribute('name',define.name)
            oe.setAttribute('x',str(define.x.expression))
            oe.setAttribute('y',str(define.y.expression))
            oe.setAttribute('z',str(define.z.expression))
            # oe.setAttribute('unit','rad')
            #oe.setAttribute('unit', str(define.unit)) #TODO: Units not handled by position right now
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Scale):
            oe = self.doc.createElement('scale')
            oe.setAttribute('name',define.name)
            oe.setAttribute('x',str(define.x.expression))
            oe.setAttribute('y',str(define.y.expression))
            oe.setAttribute('z',str(define.z.expression))
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Matrix):
            oe = self.doc.createElement('matrix')
            oe.setAttribute('name',define.name)
            oe.setAttribute('coldim',str(define.coldim))
            oe.setAttribute('values', " ".join([val.expression for val in define.values]))
            self.defines.appendChild(oe)
        elif isinstance(define, _Defines.Expression):
            return # Only write out named defines
        else:
            raise Exception("Unrecognised define type: {}".format(type(define)))

    def writeMaterial(self, material):
        if material.name in self.materials_written:
            return

        if isinstance(material, _Material) :
            oe = self.doc.createElement('material')
            oe.setAttribute('name', material.name)
            de = self.doc.createElement('D')
            de.setAttribute('value', str(material.density))
            oe.appendChild(de)

            if material.type == 'simple':
                oe.setAttribute('Z', str(material.atomic_number))
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
                        se.setAttribute('n', str(comp_info[1]))
                        oe.appendChild(se)
                    if frac_type == "natoms":
                        se = self.doc.createElement('composite')
                        se.setAttribute('ref', name)
                        se.setAttribute('n', str(comp_info[1]))
                        oe.appendChild(se)
                self.materials.appendChild(oe)
            elif material.type == 'nist' or material.type == 'arbitrary':
                # No need to add defines for NIST compounds or
                # materials which are simply names, so do not append child.
                pass

        elif isinstance(material, _Element):
            oe = self.doc.createElement('element')
            oe.setAttribute('name', material.name)
            oe.setAttribute('formula', material.symbol)
            if material.type == 'simple':
                oe.setAttribute('Z', str(material.Z))
                se = self.doc.createElement('atom')
                se.setAttribute('value', str(material.A))
                oe.appendChild(se)
            elif material.type == 'composite':
                for comp_info in material.components:
                    name = comp_info[0].name
                    self.writeMaterial(comp_info[0])
                    se = self.doc.createElement('fraction')
                    se.setAttribute('ref', name)
                    se.setAttribute('n', str(comp_info[1]))
                    oe.appendChild(se)
            self.materials.appendChild(oe)

        elif isinstance(material, _Isotope) :
            oe = self.doc.createElement('isotope')
            oe.setAttribute('name', material.name)
            oe.setAttribute('Z', str(material.Z))
            oe.setAttribute('N', str(material.N))
            se = self.doc.createElement('atom')
            se.setAttribute('type', 'A')
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

        for dv in lv.daughterVolumes :
            dve = self.writePhysicalVolume(dv)
            we.appendChild(dve)

        self.structure.appendChild(we)

    def writeAssemblyVolume(self, lv) :
        we = self.doc.createElement('assembly')
        # we.setAttribute('name', "{}{}_lv".format(self.prepend, lv.name, '_lv'))
        we.setAttribute('name',"{}{}".format(self.prepend,lv.name))

        for dv in lv.daughterVolumes :
            dve = self.writePhysicalVolume(dv)
            we.appendChild(dve)

        self.structure.appendChild(we)

    def GetDefinesFromPV(self, instance, variable):
        if not hasattr(instance, variable):
            raise AttributeError("") #TODO: Add error message
        # name = instance.name + "_" + getattr(instance,variable).name
        name = instance.name+"_"+variable
        try:
            self.registry.defineDict[name]
            # will have been written before if already in define dict
        except KeyError:
            # otherwise write define
            getattr(instance, variable).name = name
            self.writeDefine(getattr(instance, variable))
        return name

    def writePhysicalVolume(self, pv):
        pvol = self.doc.createElement('physvol')
        # pvol.setAttribute('name',"{}{}_pv".format(self.prepend, pv.name))
        pvol.setAttribute('name',"{}{}".format(self.prepend, pv.name))
        vr = self.doc.createElement('volumeref')
        # vr.setAttribute('ref',"{}{}_lv".format(self.prepend, pv.logicalVolume.name))
        vr.setAttribute('ref',"{}{}".format(self.prepend, pv.logicalVolume.name))
        pvol.appendChild(vr)

        # check if variable are in defines registry, else write define.
        posName = self.GetDefinesFromPV(pv,'position')
        rotName = self.GetDefinesFromPV(pv,'rotation')

        # phys vol translation
        tlatee = self.doc.createElement('positionref')
        tlatee.setAttribute('ref', str(posName))
        pvol.appendChild(tlatee)

        # phys vol rotation
        rote = self.doc.createElement('rotationref')
        rote.setAttribute('ref', str(rotName))
        pvol.appendChild(rote)

        # phys vol scale
        # TODO: Scale information
        #tscae = self.doc.createElement('scaleref')
        #tscae.setAttribute('ref', str(pv.rotation.name))
        #pvol.appendChild(tscae)

        return pvol

    def writeSolid(self, solid):
        """
        Dispatch to correct member function based on type string in SolidBase.
        """

        try:
            func = getattr(self, 'write'+solid.type) # get the member function
            func(solid) # call it with the solid instance as an argument
        except AttributeError:
            raise ValueError("No such solid "+solid.type)

    def getValueOrExpr(self, expr) : 
        if self.registry.defineDict.has_key(expr.name) :
            return expr.name
        else :
            return expr.expr.expression


    def getValueOrExprFromInstance(self, instance, variable, index=None):

        if not hasattr(instance, variable):
            raise AttributeError("") #TODO: Add error message
        var = getattr(instance, variable)
        
        # Indexed variable 
        if index is not None:
            try:
                var = getattr(instance,variable)[index]
            except IndexError:
                raise IndexError("") #TODO: Add error message

        # check if variable is in registry #TODO indexed variables
            if self.registry.defineDict.has_key(var.name) :
                return var.name
            else :
                return var.expr.expression

        # Expression, Constant, Quantity or Variable
        if isinstance(var, _Defines.Expression) or isinstance(var, _Defines.Constant) or isinstance(var, _Defines.Quantity) or isinstance(var, _Defines.Variable):
            return str(var.expr.expression)
        else:
            return str(var)

    def writeBox(self, instance):
        oe = self.doc.createElement('box')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('x',self.getValueOrExprFromInstance(instance,'pX'))
        oe.setAttribute('y',self.getValueOrExprFromInstance(instance,'pY'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pZ'))
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
        self.solids.appendChild(oe)

    def writeEllipsoid(self, instance):
        oe = self.doc.createElement('ellipsoid')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('ax', self.getValueOrExprFromInstance(instance,'pxSemiAxis'))
        oe.setAttribute('by', self.getValueOrExprFromInstance(instance,'pySemiAxis'))
        oe.setAttribute('cz', self.getValueOrExprFromInstance(instance,'pzSemiAxis'))
        oe.setAttribute('zcut1', self.getValueOrExprFromInstance(instance,'pzBottomCut'))
        oe.setAttribute('zcut2', self.getValueOrExprFromInstance(instance,'pzTopCut'))
        self.solids.appendChild(oe)

    def writeEllipticalCone(self, instance):
        oe = self.doc.createElement('elcone')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('dx', self.getValueOrExprFromInstance(instance,'pxSemiAxis'))
        oe.setAttribute('dy', self.getValueOrExprFromInstance(instance,'pySemiAxis'))
        oe.setAttribute('zmax', self.getValueOrExprFromInstance(instance,'zMax'))
        oe.setAttribute('zcut', self.getValueOrExprFromInstance(instance,'pzTopCut'))
        self.solids.appendChild(oe)

    def writeEllipticalTube(self, instance):
        oe = self.doc.createElement('eltube')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('dx', self.getValueOrExprFromInstance(instance,'pDx'))
        oe.setAttribute('dy', self.getValueOrExprFromInstance(instance,'pDy'))
        oe.setAttribute('dz', self.getValueOrExprFromInstance(instance,'pDz'))
        self.solids.appendChild(oe)

    def createTwoDimVertex(self, x, y):
        td = self.doc.createElement('twoDimVertex')
        td.setAttribute('x', str(x.expr.expression))
        td.setAttribute('y', str(y.expr.expression))
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

        self.solids.appendChild(oe)


    def createTriangularFacet(self, vertex1, vertex2, vertex3):
        tf = self.doc.createElement('triangular')
        tf.setAttribute('vertex1', str(vertex1))
        tf.setAttribute('vertex2', str(vertex2))
        tf.setAttribute('vertex3', str(vertex3))
        tf.setAttribute('type', 'ABSOLUTE')
        return tf

    def writeTesselatedSolid(self, instance):
        oe = self.doc.createElement('tessellated')
        name     = instance.name
        oe.setAttribute('name', self.prepend + name)

        verts = instance.mesh[0]
        facet = instance.mesh[1]

        vert_names = [] 
        
        vertex_id = 0 
        for v in verts : 
            defname = "{}_{}".format(name, vertex_id)
            vert_names.append(defname)
            vertex_id = vertex_id + 1
            self.writeDefine(_Defines.Position(defname, v[0],v[1],v[2]))
            
        for f in facet :
            oe.appendChild(self.createTriangularFacet(vert_names[f[0]], vert_names[f[1]], vert_names[f[2]]))
        
        self.solids.appendChild(oe)

    def writeHype(self, instance):
        oe = self.doc.createElement('hype')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rmin', self.getValueOrExprFromInstance(instance,'innerRadius'))
        oe.setAttribute('rmax', self.getValueOrExprFromInstance(instance,'outerRadius'))
        oe.setAttribute('z',    self.getValueOrExprFromInstance(instance,'lenZ'))
        oe.setAttribute('inst', self.getValueOrExprFromInstance(instance,'innerStereo'))
        oe.setAttribute('outst', self.getValueOrExprFromInstance(instance,'outerStereo'))
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
        pass

    def writeOrb(self, instance):
        oe = self.doc.createElement('orb')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('r', self.getValueOrExprFromInstance(instance,'pRMax'))
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
        self.solids.appendChild(oe)

    def writeParaboloid(self, instance):
        oe = self.doc.createElement('paraboloid')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rlo', self.getValueOrExprFromInstance(instance,'pR1'))
        oe.setAttribute('rhi', self.getValueOrExprFromInstance(instance,'pR2'))
        oe.setAttribute('dz', self.getValueOrExprFromInstance(instance,'pDz'))
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

        self.solids.appendChild(oe)

    def writePolyhedra(self, instance):
        oe = self.doc.createElement('polyhedra')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'phiStart'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'phiTotal'))
        oe.setAttribute('numsides',self.getValueOrExprFromInstance(instance,'numSide'))

        i = instance
        for w,x,y in zip(i.rInner, i.rOuter, i.zPlane):
            d = self.createzPlane(w,x,y)
            oe.appendChild(d)

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
        self.solids.appendChild(oe)

    def writeGenericTrap(self, instance):
        oe = self.doc.createElement('arb8')
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
        self.solids.appendChild(oe)
        
    def createPosition(self,name, x, y, z):
        p = self.doc.createElement('position')
        p.setAttribute('name',str(name))
        p.setAttribute('x', str(x))
        p.setAttribute('y', str(y))
        p.setAttribute('z', str(z))
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
        self.solids.appendChild(oe)

    def writeTorus(self, instance):
        oe = self.doc.createElement('torus')
        oe.setAttribute('name', self.prepend + instance.name)
        oe.setAttribute('rmin',self.getValueOrExprFromInstance(instance,'pRmin'))
        oe.setAttribute('rmax',self.getValueOrExprFromInstance(instance,'pRmax'))
        oe.setAttribute('rtor',self.getValueOrExprFromInstance(instance,'pRtor'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))
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
        self.solids.appendChild(oe)

    def writeTrd(self, instance):
        oe = self.doc.createElement("trd")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('x1',self.getValueOrExprFromInstance(instance,'pX1'))
        oe.setAttribute('x2',self.getValueOrExprFromInstance(instance,'pX2'))
        oe.setAttribute('y1',self.getValueOrExprFromInstance(instance,'pY1'))
        oe.setAttribute('y2',self.getValueOrExprFromInstance(instance,'pY2'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pZ'))
        self.solids.appendChild(oe)

    def writeTubs(self, instance):
        oe = self.doc.createElement("tube")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('rmin',self.getValueOrExprFromInstance(instance,'pRMin'))
        oe.setAttribute('rmax',self.getValueOrExprFromInstance(instance,'pRMax'))
        oe.setAttribute('z',   self.getValueOrExprFromInstance(instance,'pDz'))
        oe.setAttribute('startphi',self.getValueOrExprFromInstance(instance,'pSPhi'))
        oe.setAttribute('deltaphi',self.getValueOrExprFromInstance(instance,'pDPhi'))
        self.solids.appendChild(oe)

    def writeTwistedBox(self, instance):
        oe = self.doc.createElement("twistedbox")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('PhiTwist', self.getValueOrExprFromInstance(instance,'twistedAngle'))
        oe.setAttribute('x',self.getValueOrExprFromInstance(instance,'pDx'))
        oe.setAttribute('y',self.getValueOrExprFromInstance(instance,'pDy'))
        oe.setAttribute('z',self.getValueOrExprFromInstance(instance,'pDz'))
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
        self.solids.appendChild(oe)

    def writeTwistedTrap(self, instance):
        oe = self.doc.createElement("twistedtrap")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('PhiTwist',self.getValueOrExprFromInstance(instance,'twistedangle'))
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
        self.solids.appendChild(oe)
        
    def writeTwistedTubs(self, instance):
        oe = self.doc.createElement("twistedtube")
        oe.setAttribute('name',self.prepend + instance.name)
        oe.setAttribute('endinnerrad',self.getValueOrExprFromInstance(instance,'endinnerrad'))
        oe.setAttribute('endouterrad',self.getValueOrExprFromInstance(instance,'endouterrad'))
        oe.setAttribute('zlen',self.getValueOrExprFromInstance(instance,'zlen'))
        oe.setAttribute('phi',self.getValueOrExprFromInstance(instance,'phi'))
        oe.setAttribute('twistedangle',self.getValueOrExprFromInstance(instance,'twistedangle'))
        self.solids.appendChild(oe)    

    def writeUnion(self, instance):
        oe  = self.doc.createElement('union')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1.name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2.name)
        oe.appendChild(cse)

        if self.registry.defineDict.has_key(instance.tra2[1].name) :
            csce = self.doc.createElement('positionref')
            csce.setAttribute('ref',instance.tra2[1].name)
            oe.appendChild(csce)      
        else : 
            p = self.doc.createElement('position')
            p.setAttribute('x',str(instance.tra2[1].x.expression))
            p.setAttribute('y',str(instance.tra2[1].y.expression))
            p.setAttribute('z',str(instance.tra2[1].z.expression))
            oe.appendChild(p)

        if self.registry.defineDict.has_key(instance.tra2[0].name) : 
            csce1 = self.doc.createElement('rotationref')
            csce1.setAttribute(instance.tra2[0].name)
            oe.appendChild(csce1)
        else : 
            r = self.doc.createElement('rotation')
            r.setAttribute('x', str(instance.tra2[0].x.expression))
            r.setAttribute('y', str(instance.tra2[0].y.expression))
            r.setAttribute('z', str(instance.tra2[0].z.expression))
            oe.appendChild(r)

        self.solids.appendChild(oe)

    def writeSubtraction(self, instance):
        oe  = self.doc.createElement('subtraction')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1.name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2.name)
        oe.appendChild(cse)
    
        if self.registry.defineDict.has_key(instance.tra2[1].name) :
            csce = self.doc.createElement('positionref')        
            csce.setAttribute('ref',instance.tra2[1].name)
            oe.appendChild(csce)
        else :
            p = self.doc.createElement('position')
            p.setAttribute('x',str(instance.tra2[1].x.expression))
            p.setAttribute('y',str(instance.tra2[1].y.expression))
            p.setAttribute('z',str(instance.tra2[1].z.expression))
            oe.appendChild(p)

        if self.registry.defineDict.has_key(instance.tra2[0].name) : 
            csce1 = self.doc.createElement('rotationref')
            csce1.setAttribute('ref',instance.tra2[0].name)
            oe.appendChild(csce1)
        else : 
            r = self.doc.createElement('rotation')
            r.setAttribute('x', str(instance.tra2[0].x.expression))
            r.setAttribute('y', str(instance.tra2[0].y.expression))
            r.setAttribute('z', str(instance.tra2[0].z.expression))
            oe.appendChild(r)

        self.solids.appendChild(oe)

    def writeIntersection(self, instance):
        oe  = self.doc.createElement('intersection')
        oe.setAttribute('name',self.prepend + instance.name)

        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + instance.obj1.name)
        oe.appendChild(cfe)

        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + instance.obj2.name)
        oe.appendChild(cse)

        if self.registry.defineDict.has_key(instance.tra2[1].name) :
            csce = self.doc.createElement('positionref')
            csce.setAttribute('ref',instance.tra2[1].name)
            oe.appendChild(csce)
        else :
            p = self.doc.createElement('position')
            p.setAttribute('x',str(instance.tra2[1].x.expression))
            p.setAttribute('y',str(instance.tra2[1].y.expression))
            p.setAttribute('z',str(instance.tra2[1].z.expression))
            oe.appendChild(p)

        if self.registry.defineDict.has_key(instance.tra2[0].name) : 
            csce1 = self.doc.createElement('rotationref')
            csce1.setAttribute('ref',instance.tra2[0].name)
            oe.appendChild(csce1)
        else : 
            r = self.doc.createElement('rotation')
            r.setAttribute('x', str(instance.tra2[0].x.expression))
            r.setAttribute('y', str(instance.tra2[0].y.expression))
            r.setAttribute('z', str(instance.tra2[0].z.expression))
            oe.appendChild(r)

        self.solids.appendChild(oe)

    def writeMultiUnion(self, instance) : 
        oe  = self.doc.createElement('multiUnion')
        oe.setAttribute('name',self.prepend + instance.name)        
        
        # loop over objects
        for solid, trans, i in zip(instance.objects, instance.transformations , range(0,len(instance.objects))) : 
            ce = self.doc.createElement('multiUnionNode')
            ce.setAttribute('name',self.prepend + 'node-' +str(i)) 
            cse = self.doc.createElement('solid')
            cse.setAttribute('ref',solid.name)
            cpe = self.doc.createElement('positionref')
            cpe.setAttribute('ref',trans[1].name)
            cre = self.doc.createElement('rotationref')
            cre.setAttribute('ref',trans[0].name)
            ce.appendChild(cse)
        
            if self.registry.defineDict.has_key(trans[1].name) :
                ce.appendChild(cpe)
            if self.registry.defineDict.has_key(trans[0].name) : 
                ce.appendChild(cre)
                
            oe.appendChild(ce)

        self.solids.appendChild(oe)
