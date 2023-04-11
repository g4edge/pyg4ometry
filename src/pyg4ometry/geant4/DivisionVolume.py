from .PhysicalVolume import PhysicalVolume as _PhysicalVolume
import pyg4ometry.geant4.solid as _solid
from   pyg4ometry.visualisation  import Mesh as _Mesh
from   pyg4ometry.visualisation import VisualisationOptions as _VisOptions
import pyg4ometry.transformation as _trans

import numpy as _np
import copy as _copy
import logging as _log


class DivisionVolume(_PhysicalVolume) :
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
        self.unit                = unit

        self.visOptions          = _VisOptions()

        # NOT PART OF NORMAL DIVISION VOLUME BUT USEFUL FOR CONVERSION TO FLUKA
        # need to determine type or rotation and position, as should be Position or Rotation type
        from pyg4ometry.gdml import Defines as _Defines

        self.position = _Defines.Position(name + "_pos", 0, 0, 0, "mm", registry, False)
        self.rotation = _Defines.Rotation(name + "_rot", 0, 0, 0, "rad", registry, False)
        self.scale    = _Defines.Scale(name + "_sca", 1, 1, 1, "none", registry, False)

        if motherVolume.solid.type != logicalVolume.solid.type:
            raise ValueError("Can not have divisions with a different solid type than"
                             " the mother volume. Mother"
                             " : {}, Division : {}".format(motherVolume.solid.type,
                                                           logicalVolume.solid.type))
        if addRegistry :
            registry.addPhysicalVolume(self)

        # physical visualisation options
        self.visOptions    = _VisOptions()

        # Create division meshes
        [self.meshes, self.transforms] = self.createDivisionMeshes()

    def getMotherSize(self):
        sd = self.motherVolume.solid
        stype = sd.type

        # The sizes along the 5 axis for all supported solids
        if stype == "Box":
            sizes = [float(sd.pX), float(sd.pY), float(sd.pZ), -1, -1]

        elif stype == "Tubs":
            sizes = [-1, -1, float(sd.pDz), float(sd.pRMax) - float(sd.pRMin), float(sd.pDPhi)]

        elif stype == "Cons":
             # The radius is the outer radius at the -Z face
            sizes = [-1, -1, float(sd.pDz), float(sd.pRmax1)-float(sd.pRmin1), float(sd.pDPhi)]

        elif stype == "Trd":
            # Can not divide up the sloping sides of the trapezoid
            sizes = [min(float(sd.pX1),float(sd.pX2)),
                     min(float(sd.pY1),float(sd.pY2)), float(sd.pZ), -1, -1]

        elif stype == "Para":
            sizes = [2*float(sd.pX), 2*float(sd.pY), 2*float(sd.pZ), -1, -1]

        elif stype == "Polycone":
            # Z is in increasing order
            sizes = [-1, -1, float(sd.pZpl[-1])-float(sd.pZpl[0]),
                     float(sd.pRMax[0])-float(sd.pRMin[0]), float(sd.pDPhi)]

        elif stype == "Polyhedra":
            sizes = [-1, -1, float(sd.zPlane[-1])-float(sd.zPlane[0]),
                     float(sd.rOuter[0])-float(sd.rInner[0]), float(sd.pDPhi)]

        return sizes[self.axis - 1]

    def checkAxis(self, allowed_axes):
        if self.axis not in allowed_axes:
            raise ValueError("Division along axis {}"
                             " not supported for solid {}".format(self.axis,
                                                                  self.logicalVolume.solid.type))

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
            solid = _solid.Box(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                               self.motherVolume.solid.pX,
                               self.motherVolume.solid.pY,
                               self.motherVolume.solid.pZ,
                               self.logicalVolume.registry,
                               self.motherVolume.solid.lunit,
                               False)

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
            solid = _solid.Tubs(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                                self.motherVolume.solid.pRMin,
                                self.motherVolume.solid.pRMax,
                                self.motherVolume.solid.pDz,
                                self.motherVolume.solid.pSPhi,
                                self.motherVolume.solid.pDPhi,
                                self.motherVolume.registry,
                                self.motherVolume.solid.lunit,
                                self.motherVolume.solid.aunit,
                                self.logicalVolume.solid.nslice,
                                False)

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
            solid = _solid.Cons(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                                self.motherVolume.solid.pRmin1,
                                self.motherVolume.solid.pRmax1,
                                self.motherVolume.solid.pRmin2,
                                self.motherVolume.solid.pRmax2,
                                self.motherVolume.solid.pDz,
                                self.motherVolume.solid.pSPhi,
                                self.motherVolume.solid.pDPhi,
                                self.motherVolume.registry,
                                self.motherVolume.solid.lunit,
                                self.motherVolume.solid.aunit,
                                self.motherVolume.solid.nslice,
                                False)

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
            solid = _solid.Para(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                                self.motherVolume.solid.pX,
                                self.motherVolume.solid.pY,
                                self.motherVolume.solid.pZ,
                                self.motherVolume.solid.pAlpha,
                                self.motherVolume.solid.pTheta,
                                self.motherVolume.solid.pPhi,
                                self.motherVolume.registry,
                                self.motherVolume.solid.lunit,
                                self.motherVolume.solid.aunit,
                                False)

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

    def divideTrd(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kXAxis, self.Axis.kYAxis, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize =  self.getMotherSize()
        placements = _np.arange(-msize/2. + offset + width/2.,
                                -msize/2. + offset + width*ndiv,
                                width)

        x1 = float(self.motherVolume.solid.pX1)
        x2 = float(self.motherVolume.solid.pX2)
        y1 = float(self.motherVolume.solid.pY1)
        y2 = float(self.motherVolume.solid.pY2)

        dX = x2 - x1
        dY = y2 - y1
        x_i = x1  # For linear interpolation in Z
        y_i = y1
        h_i  = 0.

        for i, v in enumerate(placements):
            solid = _solid.Trd(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                               self.motherVolume.solid.pX1,
                               self.motherVolume.solid.pX2,
                               self.motherVolume.solid.pY1,
                               self.motherVolume.solid.pY2,
                               self.motherVolume.solid.pZ,
                               self.motherVolume.registry,
                               self.motherVolume.solid.lunit,
                               False)
            if self.axis == self.Axis.kXAxis :
                solid.pX1.expr.expression = str(width)
                solid.pX2.expr.expression = str(width)
                transforms.append([[0,0,0],[v,0,0]])

            elif self.axis == self.Axis.kYAxis:
                solid.pY1.expr.expression = str(width)
                solid.pY2.expr.expression = str(width)
                transforms.append([[0,0,0],[0,v,0]])

            elif self.axis == self.Axis.kZAxis :
                solid.pX1.expr.expression = str(x_i)
                solid.pY1.expr.expression = str(y_i)
                h_i += width
                x_i = x1 + h_i*dX/msize
                y_i = y1 + h_i*dY/msize
                solid.pX2.expr.expression = str(x_i)
                solid.pY2.expr.expression = str(y_i)
                solid.pZ.expr.expression = str(width)
                transforms.append([[0,0,0], [0,0,v]])

            meshes.append(_Mesh(solid))

        return meshes, transforms

    def dividePolycone(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kRho, self.Axis.kPhi, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize =  self.getMotherSize()
        if not msize: # Possible if inner and outer radii at -Z are the same
            raise ValueError("Cannot construct polycone division with degenerate radii at -Z")

        if self.axis ==  self.Axis.kPhi:
            # Always take into account the inner sizes of the solids
            placements =_np.arange(float(self.motherVolume.solid.pSPhi) + offset,
                                   float(self.motherVolume.solid.pSPhi) + offset+ndiv*width, width)
        elif self.axis == self.Axis.kRho:
            placements =_np.arange(float(self.motherVolume.solid.pRMin[0]) + offset,
                                   float(self.motherVolume.solid.pRMin[0]) + offset+ndiv*width, width)
        else:
            # If width is not specified, divide along the Z planes
            # If the width is specified, can only divide between 2 Z planes
            if ndiv*width == msize: # this means default width
                placements = _np.array([float(t) for t in self.motherVolume.solid.pZpl])
            else:
                zpl_sizes = _np.diff([float(t) for t in self.motherVolume.solid.pZpl])
                zsl_index = 0
                zsl_size  = 0
                offs = offset
                for i, zs in enumerate(zpl_sizes):
                    offs -= zs
                    if offs < 0:
                        if ndiv*width > abs(offs):
                            raise ValueError("Division with user-specified width is only possible"
                                             " between 2 z-planes.")
                        zsl_index = i
                        zsl_size = zs
                        break

                placements = _np.arange(float(self.motherVolume.solid.pZpl[0]) + offset,
                                        float(self.motherVolume.solid.pZpl[0]) + offset + width*ndiv,
                                        width)

                z_1 = float(self.motherVolume.solid.pZpl[zsl_index])
                z_2 = float(self.motherVolume.solid.pZpl[zsl_index+1])
                r_1 = float(self.motherVolume.solid.pRMin[zsl_index])
                r_2 = float(self.motherVolume.solid.pRMin[zsl_index+1])
                R_1 = float(self.motherVolume.solid.pRMax[zsl_index])
                R_2 = float(self.motherVolume.solid.pRMax[zsl_index+1])

                dr = r_2 - r_1
                dR = R_2 - R_1
                dz = z_2 - z_1
                h_i = offset - sum(zpl_sizes[:zsl_index])

        for i, v in enumerate(placements):
            solid = _solid.Polycone(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                                    self.motherVolume.solid.pSPhi,
                                    self.motherVolume.solid.pDPhi,
                                    self.motherVolume.solid.pZpl,
                                    self.motherVolume.solid.pRMin,
                                    self.motherVolume.solid.pRMax,
                                    self.motherVolume.registry,
                                    self.motherVolume.solid.lunit,
                                    self.motherVolume.solid.aunit,
                                    self.motherVolume.solid.nslice,
                                    False)

            if self.axis == self.Axis.kRho :
                r_0 = float(self.motherVolume.solid.pRMin[0])
                w_0 = float(self.motherVolume.solid.pRMax[0]) - r_0
                for i in range(len(solid.pRMin)):
                    r_i = float(self.motherVolume.solid.pRMin[i])
                    w_i = float(self.motherVolume.solid.pRMax[i]) - r_i
                    w_ratio_i = w_i / w_0
                    v_2 = w_ratio_i*(v - (r_0+offset)) + (r_i+w_ratio_i*offset) # Proprtional increase
                    solid.pRMin[i].expr.expression = str(v_2)
                    solid.pRMax[i].expr.expression = str(v_2 + w_ratio_i*width)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi:
                solid.pSPhi.expr.expression = str(v)
                solid.pDPhi.expr.expression = str(width)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kZAxis :
                if ndiv*width == msize:
                    # This is the default case and we don't actually need the calculated
                    # placements, only the indices
                    if i == len(solid.pRMin) -1:
                        continue # As we split into (nzplanes - 1) polycones
                    solid.pRMin = solid.pRMin[i:i+2]
                    solid.pRMax = solid.pRMax[i:i+2]
                    solid.pZpl  = solid.pZpl[i:i+2]
                else:
                    r_min = []
                    r_max = []
                    r_min.append(r_1 + h_i*dr/dz)
                    r_max.append(R_1 + h_i*dR/dz)
                    h_i += width
                    r_min.append(r_1 + h_i*dr/dz)
                    r_max.append(R_1 + h_i*dR/dz)
                    solid.pRMin = r_min
                    solid.pRMax = r_max
                    solid.pZpl  = [v, v + width]
                    transforms.append([[0,0,0], [0,0,0]])

            meshes.append(_Mesh(solid))

        return meshes, transforms

    def dividePolyhedra(self, offset, width, ndiv):
        allowed_axes = [self.Axis.kRho, self.Axis.kPhi, self.Axis.kZAxis]
        self.checkAxis(allowed_axes)

        meshes = []
        transforms = []

        msize =  self.getMotherSize()
        if not msize: # Possible if inner and outer radii at -Z are the same
            raise ValueError("Cannot construct polyhedra division with degenerate radii at -Z")

        if self.axis ==  self.Axis.kPhi:
            # Always take into account the inner sizes of the solids
            sphi = float(self.motherVolume.solid.pSPhi)
            dphi = float(self.motherVolume.solid.pDPhi)
            nsides = int(float(self.motherVolume.solid.numSide))
            placements =_np.arange(sphi, sphi+dphi, dphi/nsides)

        elif self.axis == self.Axis.kRho:
            placements =_np.arange(float(self.motherVolume.solid.rInner[0]) + offset,
                                   float(self.motherVolume.solid.rInner[0]) + offset+ndiv*width, width)
        else:
            # If width is not specified, divide along the Z planes
            # If the width is specified, can only divide between 2 Z planes
            if ndiv*width == msize: # this means default width
                placements = _np.array([float(t) for t in self.motherVolume.solid.zPlane])
            else:
                zpl_sizes = _np.diff([float(t) for t in self.motherVolume.solid.zPlane])
                zsl_index = 0
                zsl_size  = 0
                offs = offset
                for i, zs in enumerate(zpl_sizes):
                    offs -= zs
                    if offs < 0:
                        if ndiv*width > abs(offs):
                            raise ValueError("Division with user-specified width is only possible"
                                             " between 2 z-planes.")
                        zsl_index = i
                        zsl_size = zs
                        break

                placements = _np.arange(float(self.motherVolume.solid.zPlane[0]) + offset,
                                        float(self.motherVolume.solid.zPlane[0]) + offset + width*ndiv,
                                        width)

                z_1 = float(self.motherVolume.solid.zPlane[zsl_index])
                z_2 = float(self.motherVolume.solid.zPlane[zsl_index+1])
                r_1 = float(self.motherVolume.solid.rInner[zsl_index])
                r_2 = float(self.motherVolume.solid.rInner[zsl_index+1])
                R_1 = float(self.motherVolume.solid.rOuter[zsl_index])
                R_2 = float(self.motherVolume.solid.rOuter[zsl_index+1])

                dr = r_2 - r_1
                dR = R_2 - R_1
                dz = z_2 - z_1
                h_i = offset - sum(zpl_sizes[:zsl_index])

        for i, v in enumerate(placements):
            solid = _solid.Polyhedra(self.name + "_" + self.motherVolume.solid.name + "_" + str(i),
                                     self.motherVolume.solid.pSPhi,
                                     self.motherVolume.solid.pDPhi,
                                     self.motherVolume.solid.numSide,
                                     self.motherVolume.solid.numZPlanes,
                                     self.motherVolume.solid.zPlane,
                                     self.motherVolume.solid.rInner,
                                     self.motherVolume.solid.rOuter,
                                     self.motherVolume.registry,
                                     self.motherVolume.solid.lunit,
                                     self.motherVolume.solid.aunit,
                                     False)

            if self.axis == self.Axis.kRho :
                r_0 = float(self.motherVolume.solid.rInner[0])
                w_0 = float(self.motherVolume.solid.rOuter[0]) - r_0
                for i in range(len(solid.rInner)):
                    r_i = float(self.motherVolume.solid.rInner[i])
                    w_i = float(self.motherVolume.solid.rOuter[i]) - r_i
                    w_ratio_i = w_i / w_0
                    v_2 = w_ratio_i*(v - (r_0+offset)) + (r_i+w_ratio_i*offset) # Proprtional increase
                    solid.rInner[i].expr.expression = str(v_2)
                    solid.rOuter[i].expr.expression = str(v_2 + w_ratio_i*width)
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kPhi:
                solid.pSPhi.expr.expression = str(v)
                solid.pDPhi.expr.expression = str(dphi / nsides)
                solid.numSide.expr.expression = "1"
                transforms.append([[0,0,0],[0,0,0]])

            elif self.axis == self.Axis.kZAxis :
                if ndiv*width == msize:
                    # This is the default case and we don't actually need the calculated
                    # placements, only the indices
                    if i == len(solid.rInner) -1:
                        continue # As we split into (nzplanes - 1) polycones
                    solid.rInner = solid.rInner[i:i+2]
                    solid.rOuter = solid.rOuter[i:i+2]
                    solid.zPlane  = solid.zPlane[i:i+2]
                else:
                    r_min = []
                    r_max = []
                    r_min.append(r_1 + h_i*dr/dz)
                    r_max.append(R_1 + h_i*dR/dz)
                    h_i += width
                    r_min.append(r_1 + h_i*dr/dz)
                    r_max.append(R_1 + h_i*dR/dz)
                    solid.rInner = r_min
                    solid.rOuter = r_max
                    solid.zPlane  = [v, v + width]
                    transforms.append([[0,0,0], [0,0,0]])

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

    def extent(self, includeBoundingSolid = True) :
        _log.info('ReplicaVolume.extent> %s' %(self.name))

        vMin = [1e99, 1e99, 1e99]
        vMax = [-1e99, -1e99, -1e99]

        for trans, mesh in zip(self.transforms, self.meshes) :
            # transform daughter meshes to parent coordinates
            dvmrot = _trans.tbxyz2matrix(trans[0])
            dvtra = _np.array(trans[1])

            [vMinDaughter, vMaxDaughter] = mesh.getBoundingBox()

            vMinDaughter = _np.array((dvmrot.dot(vMinDaughter) + dvtra)).flatten()
            vMaxDaughter = _np.array((dvmrot.dot(vMaxDaughter) + dvtra)).flatten()


            if vMaxDaughter[0] > vMax[0] :
                vMax[0] = vMaxDaughter[0]
            if vMaxDaughter[1] > vMax[1] :
                vMax[1] = vMaxDaughter[1]
            if vMaxDaughter[2] > vMax[2] :
                vMax[2] = vMaxDaughter[2]

            if vMinDaughter[0] < vMin[0] :
                vMin[0] = vMinDaughter[0]
            if vMinDaughter[1] < vMin[1] :
                vMin[1] = vMinDaughter[1]
            if vMinDaughter[2] < vMin[2] :
                vMin[2] = vMinDaughter[2]

        return [vMin,vMax]

