import copy as _copy 

from pyg4ometry.transformation import *
from pyg4ometry.pycsg.geom import Vector as _Vector

from pyg4ometry.pycsg.core import CSG as _CSG

import logging as _log

class OverlapType:
    protrusion = 1
    overlap    = 2
    coplanar   = 3

class Mesh(object) : 

    def __init__(self, solid) : 
        parameters = [] 
        values     = {}

        # Solid which contains the mesh
        self.solid = solid 

        # mesh in local coordinates
        self.localmesh  = self.solid.pycsgmesh().clone()

        # bounding mesh in local coordinates
        self.localboundingmesh = self.getBoundingBoxMesh()

        # overlap meshes (protusion, overlap, coplanar)
        self.overlapmeshes = []
        
    def remesh(self) :
        # existing overlaps become invalid
        self.overlapmeshes = []

        # recreate mesh
        self.localmesh = self.solid.pycsgmesh().clone()

        # recreate bounding mesh
        self.localboundingmesh = self.getBoundingBoxMesh()

    def addOverlapMesh(self, mesh) : 
        self.overlapmeshes.append(mesh)

    def getLocalMesh(self) :
        return self.localmesh 

    def getBoundingBox(self) :
        '''Axes aligned bounding box'''

        vAndP = self.localmesh.toVerticesAndPolygons()
        
        vMin = [ 1e99, 1e99,1e99]
        vMax = [-1e99,-1e99,-1e99]
        for v in vAndP[0] : 
             if v[0] < vMin[0] : 
                 vMin[0] = v[0]
             if v[1] < vMin[1] : 
                 vMin[1] = v[1]
             if v[2] < vMin[2] :
                 vMin[2] = v[2]

             if v[0] > vMax[0] :
                 vMax[0] = v[0]
             if v[1] > vMax[1] :
                 vMax[1] = v[1]
             if v[2] > vMax[2] : 
                 vMax[2] = v[2]

        _log.info('visualisation.Mesh.getBoundingBox> %s %s' % (str(vMin), str(vMax)))

        return [vMin, vMax]

    def getBoundingBoxMesh(self):
        bb = self.getBoundingBox()
        x0 = (bb[1][0]+bb[0][0])/2.0
        y0 = (bb[1][1]+bb[0][1])/2.0
        z0 = (bb[1][2]+bb[0][2])/2.0

        dx = bb[1][0]-bb[0][0]
        dy = bb[1][1]-bb[0][1]
        dz = bb[1][2]-bb[0][2]

        pX = dx/2.0
        pY = dy/2.0
        pZ = dz/2.0

        _log.info('box.pycsgmesh> getBoundingBoxMesh')

        mesh = _CSG.cube(center=[x0,y0,z0], radius=[pX,pY,pZ])
        return mesh