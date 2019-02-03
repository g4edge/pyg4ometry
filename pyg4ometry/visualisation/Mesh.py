import copy as _copy 

from pyg4ometry.transformation import *
from pyg4ometry.pycsg.geom import Vector as _Vector

class Mesh(object) : 

    def __init__(self, solid) : 
        parameters = [] 
        values     = {}

        # Solid which contains the mesh
        self.solid = solid 

        # Visualisation attributes 
        self.wireframe = False

        # mesh in global coordinates 
        self.localmesh  = self.solid.pycsgmesh()

        # overlap meshes 
        self.overlapmeshes = []
        
        # coplanar meshes 
        self.coplanarmeshes = []

        # extents 
        self.extent = []
        
    def addOverlapMesh(self, mesh) : 
        self.overlapmeshes.append(mesh)

    def getLocalMesh(self) :
        return self.localmesh 

    def getBoundingBox(self) : 
        pass

    def getSize(self) :
        pass

    def getCentre(self) : 
        pass

    def setCentre(self) : 
        pass
