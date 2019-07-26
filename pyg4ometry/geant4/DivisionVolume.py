import PhysicalVolume as _PhysicalVolume
from   pyg4ometry.visualisation  import Mesh     as _Mesh

import numpy as _np
import copy as _copy

class DivisionVolume(_PhysicalVolume.PhysicalVolume) : 
    '''
    DivisionVolume: G4PVDivision

    :param name: of physical volume 
    :param logical: volume to be placed
    :param mother: logical volume, 
    :param axis: kXAxis,kYAxis,kZAxis,kRho,kPhi
    :param ncopies: number of replicas
    :param width: spacing between replicas along axis
    :param offset: of grid
    '''

    class Axis:
        kXAxis = 1
        kYAxis = 2
        kZAxis = 3
        kRho   = 4
        kPhi   = 5

    def __init__(self, name, logicalVolume, motherVolume, axis, ndivisions=-1,
                 width=-1, offset=0, registry=None, addRegistry=True, unit="mm") :

        self.type = "division"
        self.name = name
        self.logicalVolume       = logicalVolume
        self.motherVolume        = motherVolume
        self.motherVolume.add(self)
        self.axis                = axis
        self.ndivisions          = ndivisions
        self.width               = width
        self.offset              = offset

        if motherVolume.solid.type != logicalVolume.solid.type:
            raise ValueError("Can not have divisions with a different solid type than"
                             " the mother volume. Mother"
                             " : {}, Division : {}".format(motherVolume.solid.type,
                                                           logicalVolume.solid.type))
        if addRegistry :
            registry.addPhysicalVolume(self)

        # Create division meshes
        [self.meshes, self.transforms] = self.createDivisionMeshes()

    def getMotherSize(self):
        sd = self.motherVolume.solid
        stype = sd.type

        # The sizes along the 5 axis for all supported solids
        if stype == "Box":
            sizes = [float(sd.pX), float(sd.pY), float(sd.pZ), None, None]

        elif stype == "Tubs":
            sizes = [None, None, float(sd.pDz), float(sd.pRMax) - float(sd.pRMin), float(sd.pDPhi)]

        elif stype == "Cons":
             # The radius is the outer radius at the -Z face
            sizes = [None, None, float(sd.pDz), float(sd.pRmax1)-float(sd.pRmin1), float(sd.pDPhi)]

        elif stype == "Trd":
            # Can not divide up the sloping sides of the trapezoid
            sizes = [min(float(sd.pX1),float(sd.pX2)),
                     min(float(sd.pY1),float(sd.pY2)), float(sd.pZ), None, None]

        elif stype == "Para":
            sizes = [2*float(sd.pX), 2*float(sd.pY), 2*float(sd.pZ), None, None]

        elif stype == "Polycone":
            # Z is in increasing order
            sizes = [None, None, float(sd.Zpl[-1]), float(sd.pRMax[0])-float(sd.pRMin[0]),
                     float(sd.pDPhi)]

        elif stype == "Polyhedra":
            sizes = [None, None, float(sd.zPlane[-1]), float(sd.rOuter[0])-float(sd.rInner[0]),
                     float(sd.phiTotal)]

        return sizes[self.axis - 1]

    def checkAxis(self, allowed_axes):
        if self.axis not in allowed_axes:
            raise ValueError("Division along axis {}"
                             " not supported for solid {}".format(self.axis,
                                                                  self.logicalVolume.solid.name))

    def divideBox(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kXAxis, self.Axis.kYAxis, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize = self.getMotherSize()
        placements = _np.arange(-msize/2. + offset + width/2.,
                                -msize/2. + offset + width*ndiv,
                                width)

        for i, v in enumerate(placements):
            solid = _copy.deepcopy(self.motherVolume.solid)
            solid.name  = self.name+"_"+solid.name+"_"+str(i)

            if self.axis == self.Axis.kXAxis :
                solid.pX.expr.expression = str(width)
                transforms.append([[0,0,0],[v,0,0]])

            elif self.axis == self.Axis.kYAxis :
                solid.pY.expr.expression = str(width)
                transforms.append([[0,0,0],[0,v,0]])

            elif self.axis == self.Axis.kZAxis :
                solid.pZ.expr.expression = str(width)
                transforms.append([[0,0,0],[0,0,v]])

            meshes.append(_Mesh(solid))
        return meshes, transforms

    def divideTubs(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kRho, self.Axis.kPhi, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        if self.axis ==  self.Axis.kPhi:
            # Always take into account the inner sizes of the solids
            placements =_np.arange(float(self.motherVolume.solid.pSPhi) + offset,
                                   float(self.motherVolume.solid.pSPhi) + offset+ndiv*width, width)
        elif self.axis == self.Axis.kRho:
            placements =_np.arange(float(self.motherVolume.solid.pRMin) + offset,
                                   float(self.motherVolume.solid.pRMin) + offset+ndiv*width, width)
        else: # Position axes
            msize =  self.getMotherSize()
            placements = _np.arange(-msize/2. + offset + width/2.,
                                    -msize/2. + offset + width*ndiv,
                                    width)

        for i, v in enumerate(placements):
            solid       = _copy.deepcopy(self.motherVolume.solid)
            solid.name  = self.name+"_"+solid.name+"_"+str(i)
            if self.axis == self.Axis.kZAxis :
                solid.pDz.expr.expression = str(width)
                transforms.append([[0,0,0],[0,0,v]])

            elif self.axis == self.Axis.kRho:
                solid.pRMin.expr.expression = str(v)
                solid.pRMax.expr.expression = str(v+width)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi :
                solid.pSPhi.expr.expression = str(v)
                solid.pDPhi.expr.expression = str(width)
                transforms.append([[0,0,0],[0,0,0]])

            meshes.append(_Mesh(solid))

        return meshes, transforms

    def divideCons(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kRho, self.Axis.kPhi, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize =  self.getMotherSize()
        if self.axis ==  self.Axis.kPhi:
            # Always take into account the inner sizes of the solids
            placements =_np.arange(float(self.motherVolume.solid.pSPhi) + offset,
                                   float(self.motherVolume.solid.pSPhi) + offset+ndiv*width, width)
        elif self.axis == self.Axis.kRho:
            placements =_np.arange(float(self.motherVolume.solid.pRmin1) + offset,
                                   float(self.motherVolume.solid.pRmin1) + offset+ndiv*width, width)
        else: # Position axes
            placements = _np.arange(-msize/2. + offset + width/2.,
                                    -msize/2. + offset + width*ndiv,
                                    width)

        r1 = float(self.motherVolume.solid.pRmin1)
        r2 = float(self.motherVolume.solid.pRmin2)
        R1 = float(self.motherVolume.solid.pRmax1)
        R2 = float(self.motherVolume.solid.pRmax2)
        dr = r2 - r1
        dR = R2 - R1
        w_ratio = (R2-r2)/msize # Ratio of the bottom and top thickness

        h_i = 0. # For linear interpolation of the Z-divisions
        r_i = r1
        R_i = R1
        for i, v in enumerate(placements):
            solid       = _copy.deepcopy(self.motherVolume.solid)
            solid.name  = self.name+"_"+solid.name+"_"+str(i)
            if self.axis == self.Axis.kZAxis :
                solid.pRmin1.expr.expression = str(r_i) # Set the radii
                solid.pRmax1.expr.expression = str(R_i)
                h_i += width
                r_i = r1 + h_i*dr/msize
                R_i = R1 + h_i*dR/msize
                solid.pRmin2.expr.expression = str(r_i)
                solid.pRmax2.expr.expression = str(R_i)
                solid.pDz.expr.expression = str(width) # Set the slice size
                transforms.append([[0,0,0],[0,0,v]])

            elif self.axis == self.Axis.kRho:
                solid.pRmin1.expr.expression = str(v)
                solid.pRmax1.expr.expression = str(v + width)
                v_2 = v - (r1+offset) + (r2+w_ratio*offset) # Transfrom to top starting offset
                solid.pRmin2.expr.expression = str(v_2)
                solid.pRmax2.expr.expression = str(v_2 + w_ratio*width)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi :
                solid.pSPhi.expr.expression = str(v)
                solid.pDPhi.expr.expression = str(width)
                transforms.append([[0,0,0],[0,0,0]])

            meshes.append(_Mesh(solid))

        return meshes, transforms

    def dividePara(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kXAxis, self.Axis.kYAxis, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize =  self.getMotherSize()

        placements = _np.arange(-msize/2. + offset + width/2.,
                                -msize/2. + offset + width*ndiv,
                                width)

        for i, v in enumerate(placements):
            solid       = _copy.deepcopy(self.motherVolume.solid)
            solid.name  = self.name+"_"+solid.name+"_"+str(i)
            if self.axis == self.Axis.kXAxis :
                solid.pX.expr.expression = str(width/2.)
                transforms.append([[0,0,0],[v,0,0]])

            elif self.axis == self.Axis.kYAxis:
                solid.pY.expr.expression = str(width/2.)
                transforms.append([[0,0,0],[v*_np.sin(float(solid.pAlpha)),v,0]])

            elif self.axis == self.Axis.kZAxis :
                theta = float(solid.pTheta)
                phi = float(solid.pPhi)
                solid.pZ.expr.expression = str(width/2.)
                transforms.append([[0,0,0],
                                   [v*_np.sin(theta), v*_np.sin(phi), v*_np.cos(phi)]])

            meshes.append(_Mesh(solid))

        return meshes, transforms

    def createDivisionMeshes(self) :
        ndivisions = int(float(self.ndivisions)) # Do float() instead of .eval() because .eval() doesnt
        offset    = float(self.offset)           # work with the default numerical values
        width     = float(self.width)

        transforms = []
        meshes     = []


        # Poor man's overloading of the 3 possible constructors.
        if width <= 0  and ndivisions > 0:
            #raise ValueError("Option not implemented yet")
            width = (self.getMotherSize() - offset) / ndivisions
        elif ndivisions <= 0 and width > 0:
            #raise ValueError("Option not implemented yet")
            width = int((self.getMotherSize() - offset) / width)
        elif ndivisions > 0 and width > 0:
            pass # Can work with this directly

        if hasattr(self, "divide{}".format(self.logicalVolume.solid.type)):
            stype = self.logicalVolume.solid.type
            meshes, transforms = getattr(self, "divide{}".format(stype))(offset,width,ndivisions)
        else:
            raise ValueError("Division with solid {}"
                             " is not supported yet.".format(self.logicalVolume.solid.type))

        return [meshes, transforms]

    def __repr__(self) :
        return 'Division volume : {} {} {} {} {}'.format(self.name, self.axis, self.ndivisions,
                                                         self.offset, self.width)
