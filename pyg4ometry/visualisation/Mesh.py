import copy as _copy 

from pyg4ometry.transformation import *
from pyg4ometry.pycsg.geom import Vector as _Vector

import logging as _log

class Mesh(object) : 

    def __init__(self, solid) : 
        parameters = [] 
        values     = {}

        # Solid which contains the mesh
        self.solid = solid 

        # mesh in global coordinates 
        self.localmesh  = self.solid.pycsgmesh().clone()

        # overlap meshes 
        self.overlapmeshes = []
        
        # coplanar meshes 
        self.coplanarmeshes = []

        # extents 
        self.extent = []
        
    def remesh(self) : 
        self.localmesh = self.solid.pycsgmesh().clone()

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
