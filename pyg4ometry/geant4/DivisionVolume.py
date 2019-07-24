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
                             " the mother volume. Mother : {}, Division : {}".format(motherVolume.solid.type,
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
             # TODO: What about the starting angles (aka intial offset)?
            sizes = [None, None, float(sd.pDz), float(sd.pRMax), float(sd.pDPhi)]
        elif stype == "Cons":
             # The radius is the outer radius at the -Z face
            sizes = [None, None, float(sd.pDz), float(sd.pRmax1), float(sd.pDPhi)]
        elif stype == "Trd":
            # Can not divide up the sloping sides of the trapezoid
            sizes = [min(float(sd.pDx1),float(sd.pDx2)), # TODO: Check the sizes here
                     min(float(sd.pDy1),float(sd.pDy2)), None, None]
        elif stype == "Para":
            sizes = [float(sd.pDx), float(sd.pDy), float(sd.pDz), None, None]
        elif stype == "Polycone":
            # Z is in increasing order
            sizes = [None, None, float(sd.Zpl[-1]), float(sd.pRMax[0]), float(sd.pDPhi)]
        elif stype == "Polyhedra":
            sizes = [None, None, float(sd.zPlane[-1]), float(sd.rOuter[0]), float(sd.phiTotal)]

        return sizes[self.axis - 1]

    def checkAxis(self, allowed_axes):
        if self.axis not in allowed_axes:
            raise ValueError("Division along axis {}"
                             " not supported for solid {}".format(self.axis, self.logicalVolume.solid.name))

    def divideBox(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kXAxis, self.Axis.kYAxis, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize = self.getMotherSize()
        for i, v in enumerate(_np.arange(-msize/2. + offset + width/2.,  -msize/2. + offset + width*ndiv, width)):
            solid = _copy.deepcopy(self.motherVolume.solid)
            solid.name  = self.name+"_"+solid.name+"_"+str(i)

            if self.axis == self.Axis.kXAxis :
                solid.pX = width
                transforms.append([[0,0,0],[v,0,0]])

            elif self.axis == self.Axis.kYAxis :
                solid.pY = width
                transforms.append([[0,0,0],[0,v,0]])

            elif self.axis == self.Axis.kZAxis :
                solid.pZ = width
                transforms.append([[0,0,0],[0,0,v]])

            meshes.append(_Mesh(solid))
        return meshes, transforms

    def divideTubs(self, offset, width, ndiv):
        raise ValueError("Tubs division not fully implemented!")

        allowed_axes = [self.Axis.kRho, self.Axis.kPhi, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        for i, v in enumerate(_np.arange(offset-width*(ndiv-1)*0.5,  offset+width*(ndiv+1)*0.5, width)):
            if self.axis == self.Axis.kZAxis :
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,0],[0,0,v]])

        for i, v in enumerate(_np.arange(offset, offset+ndivisions*width,width)):
            if self.axis == self.Axis.kRho :
                # Copy solid so we don't change the original
                solid       = _copy.deepcopy(self.logicalVolume.solid)
                # Needs to a good solid name for optimisiation in VtkViewer
                solid.name  = self.name+"_"+solid.name+"_"+str(i)
                # Must be a tubs
                solid.pRMin.expr.expression = str(v)
                solid.pRMax.expr.expression = str(v+width)
                mesh   = _Mesh(solid)

                meshes.append(mesh)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi :
                meshes.append(self.logicalVolume.mesh)
                transforms.append([[0,0,v],[0,0,0]])

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
            meshes, transforms = getattr(self, "divide{}".format(self.logicalVolume.solid.type))(offset,width,ndivisions)
        else:
            raise ValueError("Division with solid {} not supported yet.".format(self.logicalVolume.solid.type))

        return [meshes, transforms]

    def __repr__(self) :
        return 'Division volume : '+self.name+' '+str(self.axis)+' '+str(self.ndivisions)+' '+str(self.offset)+' '+str(self.width)
