from ... import config as _config

from .SolidBase import SolidBase as _SolidBase

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
    from pyg4ometry.pycsg.geom import Vector as _Vector
    from pyg4ometry.pycsg.geom import Vertex as _Vertex
    from pyg4ometry.pycsg.geom import Polygon as _Polygon
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG
    from pyg4ometry.pycgal.geom import Vector as _Vector
    from pyg4ometry.pycgal.geom import Vertex as _Vertex
    from pyg4ometry.pycgal.geom import Polygon as _Polygon

from .TwistedSolid import TwistedSolid as _TwistedSolid
from .TwoVector import TwoVector as _TwoVector
from .Layer import Layer as _Layer

import numpy as _np
import logging as _log

class TwistedBox(_SolidBase, _TwistedSolid):
    """
    Constructs a box that is twisted though angle twisted angle

    :param name:         of the solid
    :type name:          str
    :param twistedangle: twist angle, must be less than pi/2
    :type twistedangle:  float, Constant, Quantity, Variable, Expression
    :param pDx:          length in x
    :type pDx:           float, Constant, Quantity, Variable, Expression
    :param pDy:          length in y
    :type pDy:           float, Constant, Quantity, Variable, Expression
    :param pDz:          length in z
    :type pDz:           float, Constant, Quantity, Variable, Expression
    :param refine:       number of steps to iteratively smoothen the mesh by doubling the number of vertices at every step
    :type refine:        int
    :param registry:     for storing solid
    :type registry:      Registry
    :param lunit:        length unit (nm,um,mm,m,km) for solid
    :type lunit:         str    
    :param aunit:        angle unit (rad,deg) for solid
    :type aunit:         str
    :param nstack:       Not written
    :type nstack:        int
    """
    def __init__(self, name, twistedangle, pDx, pDy, pDz, registry,
                 lunit = "mm", aunit = "rad",
                 nstack=None, refine=0, addRegistry=True):
        super(TwistedBox, self).__init__(name, 'TwistedBox', registry)

        self.twistedAngle = twistedangle
        self.pDx          = pDx
        self.pDy          = pDy
        self.pDz          = pDz
        self.lunit        = lunit
        self.aunit        = aunit
        self.nstack       = nstack if nstack else _config.SolidDefaults.TwistedBox.nstack
        self.refine       = refine

        self.dependents = []

        self.varNames = ["twistedAngle", "pDx", "pDy", "pDz"]
        self.varUnits = ["aunit", "lunit", "lunit", "lunit"]

        self.checkParameters()

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return "Twisted Box : {} {} {} {} {}".format(self.name, self.twistedAngle,
                                                     self.pDx, self.pDy, self.pDz)
    def checkParameters(self):
        if self.evaluateParameterWithUnits('twistedAngle') > _np.pi:
            raise ValueError("Twisted Angle must be less than 0.5*pi")


    def makeLayers(self, p1, p2, p3, p4, pDz, theta, nstack):
        dz = 2*pDz/nstack
        dtheta = theta/nstack
        z = -pDz

        layers = []

        bottom = _Layer(p1,p2,p3,p4, z)
        bottom = bottom.Rotated(-theta*0.5) #overwrite
        layers.append(bottom)

        for i in range(nstack):
            l = layers[-1].Rotated(dtheta) # returns rotated copy
            z += dz # increment z
            l.z = z # fix z
            layers.append(l)

        return layers

    def mesh_old(self):
        _log.info('twistedbox.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit)

        twistedAngle = self.evaluateParameter(self.twistedAngle) * auval
        pDx = self.evaluateParameter(self.pDx) / 2. * luval
        pDy = self.evaluateParameter(self.pDy) / 2. * luval
        pDz = self.evaluateParameter(self.pDz) / 2. * luval
        refine = self.evaluateParameter(self.refine)

        p1 = _TwoVector(-pDx, -pDy)  # , pDz]
        p2 = _TwoVector(pDx, -pDy)  # pDz]
        p3 = _TwoVector(pDx, pDy)  # pDz]
        p4 = _TwoVector(-pDx, pDy)  # pDz]
        m = self.makeLayers(p1, p2, p3, p4, pDz, -twistedAngle, self.nstack)

        return self.meshFromLayers(m, self.nstack)

    def makeLayerEdge(self, pDx, pDy, pTwistedAngle = 0, nx = 20, ny = 20):
        x = []
        y = []

        dX = 2*pDx/nx
        dY = 2*pDy/ny

        # +y
        for i in range(0,ny+1) :
            x.append(-pDx)
            y.append(-pDy+i*dY)

        # +x
        for i in range(1,nx+1) :
            x.append(-pDx+i*dX)
            y.append(pDy)

        # -y
        for i in range(1,ny+1) :
            x.append(pDx)
            y.append(pDy-i*dY)

        # -x
        for i in range(1,nx) :
            x.append(pDx-i*dX)
            y.append(-pDy)

        x = _np.array(x)
        y = _np.array(y)

        nx = x*_np.cos(pTwistedAngle) - y*_np.sin(pTwistedAngle)
        ny = x*_np.sin(pTwistedAngle) + y*_np.cos(pTwistedAngle)

        x = list(nx)
        y = list(ny)

        #import matplotlib.pyplot as _plt
        #_plt.plot(x,y,"+")

        return [x,y]

    def mesh(self):
        _log.info('twistedbox.pycsgmesh> antlr')

        import pyg4ometry.gdml.Units as _Units #TODO move circular import 
        luval = _Units.unit(self.lunit)
        auval = _Units.unit(self.aunit) 

        twistedAngle = self.evaluateParameter(self.twistedAngle)*auval
        pDx = self.evaluateParameter(self.pDx)/2.*luval
        pDy = self.evaluateParameter(self.pDy)/2.*luval
        pDz = self.evaluateParameter(self.pDz)/2.*luval
        refine  = self.evaluateParameter(self.refine)

        _log.info('twistedbox.mesh> mesh')

        dTwist = twistedAngle/self.nstack
        dZ     = 2*pDz/self.nstack

        polygons = []

        for i in range(0,self.nstack,1) :

            i1 = i
            i2 = i+1

            twist1 = -twistedAngle/2.0 + i1*dTwist
            z1     = -pDz+i1*dZ

            twist2 = -twistedAngle/2.0 + i2*dTwist
            z2     = -pDz+i2*dZ

            edge1 = self.makeLayerEdge(pDx, pDy, twist1, 20, 20)
            edge2 = self.makeLayerEdge(pDx, pDy, twist2, 20, 20)

            # add bottom layer
            if i1 == 0 :
                vBottom = []
                for j in range(0,len(edge1[0]),1) :
                    vBottom.append(_Vertex(_Vector([edge1[0][j],edge1[1][j], z1])))
                polygons.append(_Polygon(vBottom))

            # add top layer
            if i2 == self.nstack :
                vTop = []
                for j in range(0, len(edge1[0]), 1):
                    vTop.append(_Vertex(_Vector([edge2[0][j], edge2[1][j], z2])))
                vTop.reverse()
                polygons.append(_Polygon(vTop))

            # edges
            for j in range(0,len(edge1[0]),1) :
                j1 = j
                j2 = (j+1) % len(edge1[0])
                vSide = []
                vSide.append(_Vertex(_Vector([edge1[0][j1],edge1[1][j1], z1])))
                vSide.append(_Vertex(_Vector([edge2[0][j1],edge2[1][j1], z2])))
                vSide.append(_Vertex(_Vector([edge2[0][j2],edge2[1][j2], z2])))
                vSide.append(_Vertex(_Vector([edge1[0][j2],edge1[1][j2], z1])))
                polygons.append(_Polygon(vSide))

            # print(i1,twist1,z1,i2,twist2,z2)


        return _CSG.fromPolygons(polygons)
