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
        self.localmesh = self.solid.pycsgmesh()
        self.mesh      = _copy.deepcopy(self.localmesh)


    def transformLocalMesh(self, rot, tra) : 
        self.rot = rot 
        self.tra = tra
        self.rotva = matrix2axisangle(self.rot) # vector angle (va)

        self.localmesh.rotate(self.rotva[0],rad2deg(self.rotva[1]))
        self.localmesh.translate(_Vector(tra))

    def pygcsgmesh(self) :
        return self.mesh 

    def getSize(self) :
        pass

    def getCentre(self) : 
        pass

    def setCentre(self) : 
        pass
