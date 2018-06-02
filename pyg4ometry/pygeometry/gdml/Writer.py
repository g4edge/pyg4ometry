from xml.dom import minidom as _minidom
from xml.dom import getDOMImplementation
from pygeometry.geant4.Parameter import Parameter as _Parameter
from pygeometry.geant4.ParameterVector import ParameterVector as _ParameterVector

class Writer(object):
    def __init__(self, prepend = 'PREPEND'):
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
        
        self.defineList        = []
        self.materialList      = []
        self.solidList         = []
        self.logicalVolumeList = []
        self.physicalVolumeList= []

    def addDetector(self, registry) :
        registry = self.extractDefinesFromTesselatedSolids(registry)

        # loop over defines 
        for define in registry.defineDict :
            pass

        # loop over parameters
        for paramId in registry.parameterDict.keys() :
            param = registry.parameterDict[paramId]
            self.writeParameter(param)

        # loop over materials 

        # loop over solids 
        for solidId in registry.solidDict.keys():
            solid = registry.solidDict[solidId]
            self.writeSolid(solid)

        # loop over logical volumes 
        for logicalName in registry.logicalVolumeList  :
            logical = registry.logicalVolumeDict[logicalName]
            logical.gdmlWrite(self,self.prepend)

        self.setup.setAttribute("name","Default")
        self.setup.setAttribute("version","1.0")
        we = self.doc.createElement("world")
        we.setAttribute("ref",self.prepend+'_'+registry.worldName+"_lv")
        self.setup.appendChild(we)

    def write(self, filename) : 
        self.filename = filename

        f = open(filename,'w')
        xmlString = self.doc.toprettyxml()
        f.write(xmlString)
        f.close()

    def extractDefinesFromTesselatedSolids(self, registry):
        #Tesselated solids require their veritces to be declared in the defines.
        #Loop over all tesselated solids and populate the defines dictionary.
        for solidId in registry.solidDict.keys():
            solid = registry.solidDict[solidId]
            if solid.type == "TesselatedSolid":
                name = solid.name
                for i in range(len(solid.facet_list)):
                    facet = solid.facet_list[i][0]
                    for j in range(len(facet)):
                        vertex = facet[j]
                        defname   = "{}_F{}_V{}".format(name, i, j)
                        defvertex = _ParameterVector(defname, list(vertex))
                        registry.defineDict[defname] = defvertex

        return registry

    def writeGmadTester(self, filenameGmad, writeDefaultLattice=False, zLength=100):
        self.filenameGmad = filenameGmad

        if writeDefaultLattice:
            self.writeDefaultLattice()

        s = 'e1: element, geometry="gdml:'
        s += str(self.filename)
        s += '", l=' + str(zLength) + '*cm;\n'
        s += 'l1: line = (e1);\n'
        s += 'use,period=l1;\n'
        s += 'sample,all;\n'
        s += 'beam, particle="e-",\n'
        s += 'energy=250.0*GeV;\n'        
        f = open(self.filenameGmad, 'w')
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

    def writeParameter(self, param):
        if isinstance(param,_Parameter) :
            oe = self.doc.createElement('variable')
            oe.setAttribute('name', param.name)
            if param.name != param.expr :
                oe.setAttribute('value',param.expr)
            else :
                oe.setAttribute('value',str(float(param)))
            self.defines.appendChild(oe)
        elif isinstance(param,_ParameterVector) :
            oe = self.doc.createElement('position')
            oe.setAttribute('name', param.name)
            oe.setAttribute('unit','mm')
            oe.setAttribute('x',str(param[0]))
            oe.setAttribute('y',str(param[1]))
            oe.setAttribute('z',str(param[2]))
            self.defines.appendChild(oe)

    def writeSolid(self, solid):
        """
        Dispatch to correct member function based on type string in SolidBase.
        """

        try:
            func = getattr(self, 'write'+solid.type) # get the member function
            func(solid) # call it with the solid instance as an argument            
        except AttributeError:
            raise ValueError("No such solid "+solid.type)

    def writeBox(self, instance):
        oe = self.doc.createElement('box')
        oe.setAttribute('name', self.prepend+'_'+instance.name)
        oe.setAttribute('lunit','mm')
        oe.setAttribute('x','2*'+str(instance.pX))
        oe.setAttribute('y','2*'+str(instance.pY))
        oe.setAttribute('z','2*'+str(instance.pZ))
        self.solids.appendChild(oe)

    def writeCons(self, instance):
        oe = self.doc.createElement('cone')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('rmin1', str(instance.pRmin1))
        oe.setAttribute('rmax1', str(instance.pRmax1))
        oe.setAttribute('rmin2', str(instance.pRmin2))
        oe.setAttribute('rmax2', str(instance.pRmax2))
        oe.setAttribute('z', str(instance.pDz))
        oe.setAttribute('startphi', str(instance.pSPhi))
        oe.setAttribute('deltaphi', str(instance.pDPhi))        
        self.solids.appendChild(oe)

    def writeCutTubs(self, instance):
        oe = self.doc.createElement('cutTube')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('z', '2*'+str(instance.pDz))
        oe.setAttribute('rmin', str(instance.pRMin))
        oe.setAttribute('rmax', str(instance.pRMax))
        oe.setAttribute('startphi', str(instance.pSPhi))
        oe.setAttribute('deltaphi', str(instance.pDPhi))
        oe.setAttribute('lowX', str(instance.pLowNorm[0]))
        oe.setAttribute('lowY', str(instance.pLowNorm[1]))
        oe.setAttribute('lowZ', str(instance.pLowNorm[2]))
        oe.setAttribute('highX', str(instance.pHighNorm[0]))
        oe.setAttribute('highY', str(instance.pHighNorm[1]))
        oe.setAttribute('highZ', str(instance.pHighNorm[2]))
        self.solids.appendChild(oe)
        
        
    def writeEllipsoid(self, instance):
        oe = self.doc.createElement('ellipsoid')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('ax', str(instance.pxSemiAxis))
        oe.setAttribute('by', str(instance.pySemiAxis))
        oe.setAttribute('cz', str(instance.pzSemiAxis))
        oe.setAttribute('zcut1', str(instance.pzBottomCut))
        oe.setAttribute('zcut2', str(instance.pzTopCut))
        self.solids.appendChild(oe)

    def writeEllipticalCone(self, instance):
        oe = self.doc.createElement('elcone')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('dx', str(instance.pxSemiAxis))
        oe.setAttribute('dy', str(instance.pySemiAxis))
        oe.setAttribute('zmax', str(instance.zMax))
        oe.setAttribute('zcut', str(instance.pzTopCut))
        self.solids.appendChild(oe)

    def writeEllipticalTube(self, instance):
        oe = self.doc.createElement('eltube')
        oe.setAttribute('name', self.prepend+'_'+instance.name)
        oe.setAttribute('dx', '2*'+str(instance.pDx))
        oe.setAttribute('dy', '2*'+str(instance.pDy))
        oe.setAttribute('dz', '2*'+str(instance.pDz))
        self.solids.appendChild(oe)

    def createTwoDimVertex(self, x, y):
        td = self.doc.createElement('twoDimVertex')
        td.setAttribute('x', str(x))
        td.setAttribute('y', str(y))
        return td

    def createSection(self, zOrder, zPosition, xOffset, yOffset, scalingFactor):
        s = self.doc.createElement('section')
        s.setAttribute('zOrder', str(zOrder))
        s.setAttribute('zPosition', str(zPosition))
        s.setAttribute('xOffset', str(xOffset))
        s.setAttribute('yOffset', str(yOffset))
        s.setAttribute('scalingFactor', str(scalingFactor))
        return s

    def writeExtrudedSolid(self, instance):
        oe = self.doc.createElement('xtru')
        oe.setAttribute('name', self.prepend + '_' + instance.name)

        for vertex in instance.vertices:
            v = self.createTwoDimVertex(vertex[0], vertex[1])
            oe.appendChild(v)

        i = instance
        n = 1
        for z,x,y,s in zip(i.zpos,i.x_offs, i.y_offs, i.scale):
            s = self.createSection(n, z, x, y, s)
            n += 1
            oe.appendChild(s)

        self.solids.appendChild(oe)
        
    def createrzPoint(self, r, z):
        rz = self.doc.createElement('rzpoint')
        rz.setAttribute('r', str(r))
        rz.setAttribute('z', str(z))
        return rz

    def writeGenericPolycone(self, instance):
        oe = self.doc.createElement('genericPolycone')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('startphi', str(instance.pSPhi))
        oe.setAttribute('deltaphi', str(instance.pDPhi))

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
        oe.setAttribute('name', self.prepend + '_' + name)

        for i in range(len(instance.facet_list)):
            vertices = []
            for j in range(len(instance.facet_list[i][0])): #Always 3 elements in a facet
                vertices.append("{}_F{}_V{}".format(name, i, j))
            oe.appendChild(self.createTriangularFacet(*vertices))
        self.solids.appendChild(oe)

    def writeHype(self, instance):
        oe = self.doc.createElement('hype')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('rmin', str(instance.innerRadius))
        oe.setAttribute('rmax', str(instance.outerRadius))
        oe.setAttribute('z', '2*'+str(instance.halfLenZ))
        oe.setAttribute('inst', str(instance.innerStereo))
        oe.setAttribute('outst', str(instance.outerStereo))
        self.solids.appendChild(oe)         

    def writeIntersection(self, instance):
        oe  = self.doc.createElement('intersection')
        oe.setAttribute('name',self.prepend + '_' + instance.name)
        
        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + '_' + instance.obj1.name)
        oe.appendChild(cfe)
        
        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + '_' + instance.obj2.name)
        oe.appendChild(cse)
        
        p = self.doc.createElement('position')
        p.setAttribute('name',self.prepend + '_' + instance.name+'_'+'position') 
        p.setAttribute('x',str(instance.tra2[1][0]))
        p.setAttribute('y',str(instance.tra2[1][1]))
        p.setAttribute('z',str(instance.tra2[1][2]))
        self.defines.appendChild(p)

        r = self.doc.createElement('rotation')
        r.setAttribute('name',self.prepend + '_' + instance.name+'_'+'rotation') 
        r.setAttribute('x', str(instance.tra2[0][0]))
        r.setAttribute('y', str(instance.tra2[0][1]))
        r.setAttribute('z', str(instance.tra2[0][2]))
        self.defines.appendChild(r)
        

        csce = self.doc.createElement('positionref')
        csce.setAttribute('ref',self.prepend + '_' + instance.name+'_'+'position')
        oe.appendChild(csce)
        
        csce1 = self.doc.createElement('rotationref')
        csce1.setAttribute('ref',self.prepend + '_' + instance.name+'_'+'rotation')
        oe.appendChild(csce1)
        

        self.solids.appendChild(oe)

    def writeOpticalSurface(self, instance):
        pass

    def writeOrb(self, instance):
        oe = self.doc.createElement('orb')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('r', str(instance.pRMax))
        self.solids.appendChild(oe)

    def writePara(self, instance):      
        oe = self.doc.createElement('para')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('x', str(instance.pX))
        oe.setAttribute('y', str(instance.pY))
        oe.setAttribute('z', str(instance.pZ))
        oe.setAttribute('alpha', str(instance.pAlpha))
        oe.setAttribute('theta', str(instance.pTheta))
        oe.setAttribute('phi', str(instance.pPhi))
        self.solids.appendChild(oe)

    def writeParaboloid(self, instance):
        oe = self.doc.createElement('paraboloid')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('rlo', str(instance.pR1))
        oe.setAttribute('rhi', str(instance.pR2))
        oe.setAttribute('dz', str(instance.pDz))        
        self.solids.appendChild(oe)

    def createzPlane(self, rInner, rOuter, zplane):
        d = self.doc.createElement('zplane')
        d.setAttribute('rmin',str(rInner))
        d.setAttribute('rmax', str(rOuter))
        d.setAttribute('z', str(zplane))
        return d
    
    def writePolycone(self, instance):
        oe = self.doc.createElement('polycone')        
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('startphi',str(instance.pSPhi))
        oe.setAttribute('deltaphi',str(instance.pDPhi))

        i = instance
        for w,x,y in zip(i.pRMin, i.pRMax, i.pZpl):
            d = self.createzPlane(w,x,y)
            oe.appendChild(d)

        self.solids.appendChild(oe)
        
    def writePolyhedra(self, instance):
        oe = self.doc.createElement('polyhedra')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('startphi',str(instance.phiStart))
        oe.setAttribute('deltaphi',str(instance.phiTotal))
        oe.setAttribute('numsides',str(instance.numSide))
        
        i = instance
        for w,x,y in zip(i.rInner, i.rOuter, i.zPlane):
            d = self.createzPlane(w,x,y)
            oe.appendChild(d)

        self.solids.appendChild(oe)             

    def writeSphere(self, instance):
        oe = self.doc.createElement('sphere')
        oe.setAttribute('name',self.prepend+'_'+instance.name)
        oe.setAttribute('rmin',str(instance.pRmin))
        oe.setAttribute('rmax',str(instance.pRmax))
        oe.setAttribute('deltaphi',str(instance.pDPhi))
        oe.setAttribute('startphi',str(instance.pSPhi))
        oe.setAttribute('starttheta',str(instance.pSTheta))
        oe.setAttribute('deltatheta',str(instance.pDTheta))
        oe.setAttribute('aunit', 'rad')
        self.solids.appendChild(oe)


    def writeSubtraction(self, instance):    
        oe  = self.doc.createElement('subtraction')
        oe.setAttribute('name',self.prepend + '_' + instance.name)
        
        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + '_' + instance.obj1.name)
        oe.appendChild(cfe)
        
        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + '_' + instance.obj2.name)
        oe.appendChild(cse)
        
        p = self.doc.createElement('position')
        p.setAttribute('name',self.prepend + '_' + instance.name+'_'+'position') 
        p.setAttribute('x',str(instance.tra2[1][0]))
        p.setAttribute('y',str(instance.tra2[1][1]))
        p.setAttribute('z',str(instance.tra2[1][2]))
        self.defines.appendChild(p)

        r = self.doc.createElement('rotation')
        r.setAttribute('name',self.prepend + '_' + instance.name+'_'+'rotation') 
        r.setAttribute('x', str(instance.tra2[0][0]))
        r.setAttribute('y', str(instance.tra2[0][1]))
        r.setAttribute('z', str(instance.tra2[0][2]))
        self.defines.appendChild(r)
        

        csce = self.doc.createElement('positionref')
        csce.setAttribute('ref',self.prepend + '_' + instance.name+'_'+'position')
        oe.appendChild(csce)
        
        csce1 = self.doc.createElement('rotationref')
        csce1.setAttribute('ref',self.prepend + '_' + instance.name+'_'+'rotation')
        oe.appendChild(csce1)
        

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
        uniqueName = self.prepend+'_'+instance.name
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
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('rmin',str(instance.pRmin))
        oe.setAttribute('rmax',str(instance.pRmax))
        oe.setAttribute('rtor',str(instance.pRtor))
        oe.setAttribute('deltaphi',str(instance.pDPhi))
        oe.setAttribute('startphi',str(instance.pSPhi))
        self.solids.appendChild(oe)

    def writeTrap(self, instance):
        oe = self.doc.createElement('trap')
        oe.setAttribute('name', self.prepend + '_' + instance.name)
        oe.setAttribute('z','2*'+str(instance.pDz))
        oe.setAttribute('theta',str(instance.pTheta))
        oe.setAttribute('phi',str(instance.pDPhi))
        oe.setAttribute('y1','2*'+str(instance.pDy1))
        oe.setAttribute('x1','2*'+str(instance.pDx1))
        oe.setAttribute('x2','2*'+str(instance.pDx2))
        oe.setAttribute('alpha1',str(instance.pAlp1))
        oe.setAttribute('y2','2*'+str(instance.pDy2))
        oe.setAttribute('x3','2*'+str(instance.pDx3))
        oe.setAttribute('x4','2*'+str(instance.pDx4))
        oe.setAttribute('alpha2',str(instance.pAlp2))
        self.solids.appendChild(oe)        

    def writeTrd(self, instance):
        oe = self.doc.createElement("trd")
        oe.setAttribute('name',self.prepend + '_' + instance.name)
        oe.setAttribute('x1',str(2*instance.pX1))
        oe.setAttribute('x2',str(2*instance.pX2))
        oe.setAttribute('y1',str(2*instance.pY1))
        oe.setAttribute('y2',str(2*instance.pY2))
        oe.setAttribute('z',str(2*instance.pZ))
        self.solids.appendChild(oe)

    def writeTubs(self, instance):
        oe = self.doc.createElement("tube")
        oe.setAttribute('name',self.prepend+'_'+instance.name)
        oe.setAttribute('rmin',str(instance.pRMin))
        oe.setAttribute('rmax',str(instance.pRMax))
        oe.setAttribute('z',   str(2*instance.pDz))
        oe.setAttribute('startphi',str(instance.pSPhi))
        oe.setAttribute('deltaphi',str(instance.pDPhi))
        self.solids.appendChild(oe)

    def writeTwistedBox(self, instance):
        oe = self.doc.createElement("twistedbox")
        oe.setAttribute('name',self.prepend+'_'+instance.name)
        oe.setAttribute('PhiTwist',str(instance.twistedAngle))
        oe.setAttribute('x','2*'+ str(instance.pDx))
        oe.setAttribute('y','2*'+ str(instance.pDy))
        oe.setAttribute('z','2*'+ str(instance.pDz))
        self.solids.appendChild(oe)        

    def writeTwistedTrd(self, instance):
        oe = self.doc.createElement("twistedtrd")
        oe.setAttribute('name',self.prepend+'_'+instance.name)
        oe.setAttribute('PhiTwist',str(instance.twistedAngle))
        oe.setAttribute('x1','2*'+ str(instance.pDx1))
        oe.setAttribute('x2','2*'+ str(instance.pDx2))
        oe.setAttribute('y1','2*'+ str(instance.pDy1))
        oe.setAttribute('y2','2*'+ str(instance.pDy2))
        oe.setAttribute('z','2*'+ str(instance.pDz))
        self.solids.appendChild(oe)

    def writeTwistedTrap(self, instance):
        oe = self.doc.createElement("twistedtrap")
        oe.setAttribute('name',self.prepend+'_'+instance.name)
        oe.setAttribute('PhiTwist',str(instance.twistedangle))
        oe.setAttribute('z','2*'+ str(instance.pDz))
        oe.setAttribute('Theta',str(instance.pTheta))
        oe.setAttribute('Phi',str(instance.pDPhi))
        oe.setAttribute('y1','2*'+ str(instance.pDy1))        
        oe.setAttribute('x1','2*'+ str(instance.pDx1))
        oe.setAttribute('x2','2*'+ str(instance.pDx2))
        oe.setAttribute('y2','2*'+ str(instance.pDy2))
        oe.setAttribute('x3','2*'+ str(instance.pDx3))
        oe.setAttribute('x4','2*'+ str(instance.pDx4))
        oe.setAttribute('Alph',str(instance.pAlp))
        self.solids.appendChild(oe)       

    def writeUnion(self, instance):
        oe  = self.doc.createElement('union')
        oe.setAttribute('name',self.prepend + '_' + instance.name)
        
        cfe = self.doc.createElement('first')
        cfe.setAttribute('ref',self.prepend + '_' + instance.obj1.name)
        oe.appendChild(cfe)
        
        cse = self.doc.createElement('second')
        cse.setAttribute('ref',self.prepend + '_' + instance.obj2.name)
        oe.appendChild(cse)
        
        p = self.doc.createElement('position')
        p.setAttribute('name',self.prepend + '_' + instance.name+'_'+'position') 
        p.setAttribute('x',str(instance.tra2[1][0]))
        p.setAttribute('y',str(instance.tra2[1][1]))
        p.setAttribute('z',str(instance.tra2[1][2]))
        self.defines.appendChild(p)

        r = self.doc.createElement('rotation')
        r.setAttribute('name',self.prepend + '_' + instance.name+'_'+'rotation') 
        r.setAttribute('x', str(instance.tra2[0][0]))
        r.setAttribute('y', str(instance.tra2[0][1]))
        r.setAttribute('z', str(instance.tra2[0][2]))
        self.defines.appendChild(r)
        

        csce = self.doc.createElement('positionref')
        csce.setAttribute('ref',self.prepend + '_' + instance.name+'_'+'position')
        oe.appendChild(csce)
        
        csce1 = self.doc.createElement('rotationref')
        csce1.setAttribute('ref',self.prepend + '_' + instance.name+'_'+'rotation')
        oe.appendChild(csce1)
        

        self.solids.appendChild(oe)
