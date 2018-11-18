from matplotlib.cbook                  import flatten as _flatten

import pyg4ometry.exceptions
from ..pycsg.geom                      import Vector as _Vector
from ..pycsg.core                      import CSG as _CSG


import solid as _solid
from Registry                          import registry as _registry
from Parameter                         import Parameter as _Parameter
from ParameterVector                   import ParameterVector as _ParameterVector
from Material                          import Material as _Material
from PhysicalVolume import recursize_map_rottrans, tbxyz

import numpy as _np
import sys as _sys

class LogicalVolume(object):
    imeshed = 0
    def __init__(self, solid, material, name, debug=False, register=True, **kwargs):
        super(LogicalVolume, self).__init__()
        self.solid           = solid

        if isinstance(material, _Material):
            self.material = material
        elif isinstance(material, str):
            self.material = _Material.nist(material)
        else:
            raise SystemExit("Unsupported type for material: {}".format(type(material)))

        self.name            = name
        self.daughterVolumes = []
        self.mesh            = None
        self.debug           = debug
        self.alpha           = kwargs.get("alpha", 0.5)
        self.color           = kwargs.get("color", None)

        if register:
            _registry.addLogicalVolume(self)
        self._register = register

    def __repr__(self):
        return 'Logical volume : '+self.name+' '+str(self.solid)+' '+str(self.material)

    def pycsgmesh(self):
        # count the logical volumes meshed
        LogicalVolume.imeshed = LogicalVolume.imeshed + 1
        if self.debug:
            print 'LogicalVolume mesh count',LogicalVolume.imeshed

        #if self.mesh :
        #    return self.mesh

        # see if the volume should be skipped, but only if we registed
        # this volume in the first place.
        if self._register:
            try:
                _registry.logicalVolumeMeshSkip.index(self.name)
                if self.debug:
                    print "Logical volume skipping --------------", self.name
                return []
            except ValueError:
                pass

        if len(self.daughterVolumes) == 0:
            self.mesh = [self.solid.pycsgmesh()]

            self.mesh[0].alpha = self.alpha
            self.mesh[0].wireframe = False
            self.mesh[0].colour    = self.color if self.color is not None else (1,1,1)

        else:
            daughterMeshes = []
            for dv in self.daughterVolumes:
                dvMesh = dv.pycsgmesh()
                daughterMeshes.append(dvMesh)
                self.mesh = [self.solid.pycsgmesh(),daughterMeshes]

            self.mesh[0].alpha     = self.alpha
            self.mesh[0].wireframe = False
            self.mesh[0].colour    = self.color if self.color is not None else (1,0,0)
            self.mesh[0].logical   = True

        if self.debug:
            print 'logical mesh', self.name
        return self.mesh

    def checkOverlaps(self):
        if self._register:
            try:
                _registry.logicalVolumeMeshSkip.index(self.name)
                if self.debug:
                    print "Logical volume skipping --------------", self.name
                    return []
            except ValueError:
                pass

        if len(self.daughterVolumes) == 0:
            # If there are no children, return the mesh itself
            self.mesh = [self.solid.pycsgmesh()]
            overlaps = []
            protrusions = []

        else:
            # If there are children perfom overlap checks between them and
            daughterMeshes = []
            overlaps       = []
            protrusions    = []
            to_check       = []
            for dv in self.daughterVolumes:
                # Override logical volume visual settings
                accumulated = dv.logicalVolume.color = (1,1,1)
                accumulated = dv.logicalVolume.alpha = 0.2

                # Recursive overlap check
                accumulated = dv.logicalVolume.checkOverlaps()
                dvMesh = dv.pycsgmesh()
                to_check.append(dvMesh[0]) # Only check volumes on same level for overlaps

                daughterMeshes.append(dvMesh) # Carry through all full meshes for visualisation

                # Apply the coordinate transforms to the accumulated
                # overlap and protrusion mesh lists
                recursize_map_rottrans(accumulated[1], list(dv.position),tbxyz(list(dv.rotation)),list(dv.scale))
                recursize_map_rottrans(accumulated[2], list(dv.position),tbxyz(list(dv.rotation)),list(dv.scale))

                overlaps.append(accumulated[1]) # Carry through overlaps already accumulated
                protrusions.append(accumulated[2])

            self.mesh = [self.solid.pycsgmesh(), daughterMeshes]

            # Check volumes on the same level for overlaps
            overlaps.append(pycsg_overlap(to_check))
            # Check the container volume and its daugher for portrusions
            protrusions.append(pycsg_protrusion(self.mesh[0], to_check))

            self.mesh[0].logical   = True

        self.mesh[0].alpha     = 0.2 # Full meshes appear as light grey
        self.mesh[0].wireframe = False
        self.mesh[0].colour    = (1,1,1)

        return [self.mesh, overlaps, protrusions]

    def add(self, physicalVolume):
        self.daughterVolumes.append(physicalVolume)

    def getSize(self):
        self.pycsgmesh();
        extent = _np.array(mesh_extent(self.mesh[1:]))

        # size and centre
        self.size = extent[1] - extent[0]
        self.centre = (_Vector(extent[0]) + _Vector(extent[1]))*0.5

        return [self.size, self.centre]

    def setClip(self, centre=True, tolerance=None):
        [size, centre] = self.getSize()
        if tolerance != None:
            size += 2*tolerance
        self.setSize(size)
        if centre:
            print 'Not centering'
            self.setCentre(centre)

    def setSize(self, size):
        # if a box

        sizeParameter = _ParameterVector("GDML_Size",[_Parameter("GDML_Size_position_x",size[0]),
                                                      _Parameter("GDML_Size_position_y",size[1]),
                                                      _Parameter("GDML_Size_position_z",size[2])])


        if isinstance(self.solid,_solid.Box):
            self.solid.pX = sizeParameter[0] / 2.
            self.solid.pY = sizeParameter[1] / 2.
            self.solid.pZ = sizeParameter[2] / 2.
        elif isinstance(self.solid,_solid.Subtraction):
            self.solid.obj1.pX = size[0] / 2.
            self.solid.obj1.pY = size[1] / 2.
            self.solid.obj1.pZ = size[2] / 2.



    def setCentre(self,centre):
        self.centre = centre
        centreParameter = _ParameterVector("GDML_Centre",[_Parameter("GDML_Centre_position_x",centre[0]),
                                                          _Parameter("GDML_Centre_position_y",centre[1]),
                                                          _Parameter("GDML_Centre_position_z",centre[2])])
        for dv in self.daughterVolumes:
            if isinstance(dv.position,_ParameterVector):
                dv.position = _ParameterVector(dv.name+"_position",
                                        [dv.position[0]-centreParameter[0],
                                         dv.position[1]-centreParameter[1],
                                         dv.position[2]-centreParameter[2]],True)
            else:
                dv.position = _ParameterVector(dv.name+"_position",
                                        [_Parameter(dv.name+"_position_x",dv.position[0])-centreParameter[0],
                                         _Parameter(dv.name+"_position_y",dv.position[1])-centreParameter[1],
                                         _Parameter(dv.name+"_position_z",dv.position[2])-centreParameter[2]],True)

        # Move the beam pipe if a subtraction solid
        if isinstance(self.solid, _solid.Subtraction):
            self.solid.tra2[1] = self.solid.tra2[1] - _np.array(self.centre)

    def gdmlWrite(self, gw, prepend):
        we = gw.doc.createElement('volume')
        we.setAttribute('name',prepend + self.name+'_lv')
        mr = gw.doc.createElement('materialref')
        #if self.material.find("G4") != -1 :
        #    mr.setAttribute('ref',self.material)
        #else :
        #    mr.setAttribute('ref',prepend+'_'+self.material)

        mr.setAttribute('ref',self.material.name)
        we.appendChild(mr)

        sr = gw.doc.createElement('solidref')
        sr.setAttribute('ref',prepend + self.solid.name)
        we.appendChild(sr)

        for dv in self.daughterVolumes:
            dve = dv.gdmlWrite(gw,prepend)
            we.appendChild(dve)

        gw.structure.appendChild(we)

def mesh_extent(nlist):
    '''Function to determine extent of an tree of meshes'''

    vMin = _Vector([1e50,1e50,1e50])
    vMax = _Vector([-1e50,-1e50,-1e50])

    for m in _flatten(nlist):
        polys = m.toPolygons()
        for p in polys:
            for vert in p.vertices:
                v = vert.pos
                if v[0] < vMin[0]:
                    vMin[0] = v[0]
                if v[1] < vMin[1]:
                    vMin[1] = v[1]
                if v[2] < vMin[2]:
                    vMin[2] = v[2]
                if v[0] > vMax[0]:
                    vMax[0] = v[0]
                if v[1] > vMax[1]:
                    vMax[1] = v[1]
                if v[2] > vMax[2]:
                    vMax[2] = v[2]

    return [vMin,vMax]

def pycsg_protrusion(containerMesh, daughterMeshes):
    msl = [] # mesh subtraction list

    # count number of meshes and make flat list
    imesh = 0
    mfl   = [] # mesh flat list
    for m in _flatten(daughterMeshes):
        mfl.append(m)
        imesh += 1

    # loop over daughter meshes and subtract the container volume from them
    # if the resulting mesh is not null, a protrusion has occurred

    # Bounding box for container volume doesn't change - do it outside of loop
    m1 = containerMesh
    ex1  = mesh_extent([m1]) #Get the extents of the mesh
    c1 = (ex1[0]+ex1[1])/2.
    bbox1 = _CSG.cube(center=[c1[0],c1[1],c1[2]], radius=[float(ex1[1][0]-ex1[0][0])/2,
                                                              float(ex1[1][1]-ex1[0][1])/2,
                                                              float(ex1[1][2]-ex1[0][2])/2])
    for i in range(0, imesh):
        m2 = mfl[i]

        ex2  = mesh_extent([m2])
        c2 = (ex2[0]+ex2[1])/2.
        #l = x_max - x_min; w = y_max - y_min; h = z_max - z_min
        bbox2 = _CSG.cube(center=[c2[0],c2[1],c2[2]], radius=[float(ex2[1][0]-ex2[0][0])/2,
                                                              float(ex2[1][1]-ex2[0][1])/2,
                                                              float(ex2[1][2]-ex2[0][2])/2])

        if bbox2.subtract(bbox1).toPolygons(): #Possible protrusion, proceed to subtract
            ms = m2.subtract(m1) # mesh subtraction
            ms.colour = (1, 0, 1) # mesh prortrusions are purple/pink
            msl.append(ms)

    return msl

def pycsg_overlap(meshTree):
    '''Function to determine if there overlaps of meshes.
       If the mesh list is generated by recursively meshing the world volume,
       the first mesh in the list (the world box) is ignored as it overlaps with
       everything.
    '''
    mil = [] # mesh intersection list

    # count number of meshes and make flat list
    imesh = 0
    mfl   = [] # mesh flat list
    for m in _flatten(meshTree):
        mfl.append(m)
        imesh += 1

    # loop over meshes and determine intersection, if intersect append to intersecting mesh list
    for i in range(0, imesh):
        for j in range(i+1,imesh):
            m1 = mfl[i]
            m2 = mfl[j]

            ex1  = mesh_extent([m1]) #Get the extents of the meshes
            ex2  = mesh_extent([m2])

            c1 = (ex1[0]+ex1[1])/2.
            c2 = (ex2[0]+ex2[1])/2.

            #l = x_max - x_min; w = y_max - y_min; h = z_max - z_min
            bbox1 = _CSG.cube(center=[c1[0],c1[1],c1[2]], radius=[float(ex1[1][0]-ex1[0][0])/2,
                                                                  float(ex1[1][1]-ex1[0][1])/2,
                                                                  float(ex1[1][2]-ex1[0][2])/2])

            bbox2 = _CSG.cube(center=[c2[0],c2[1],c2[2]], radius=[float(ex2[1][0]-ex2[0][0])/2,
                                                                  float(ex2[1][1]-ex2[0][1])/2,
                                                                  float(ex2[1][2]-ex2[0][2])/2])

            if bbox2.intersect(bbox1).toPolygons(): #The solids may overlap - proceed to intersect
                mi = m1.intersect(m2) # mesh intersection
                mi.colour = (0, 0, 1) # mesh overlaps are blue
                mil.append(mi)

            """
            #Add bounding boxes for visual validation of the algorithm
            bbox1.alpha = 0.05
            bbox2.alpha = 0.05
            mil.append(bbox1)
            mil.append(bbox2)
            """
    return mil
