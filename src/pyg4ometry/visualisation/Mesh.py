import copy as _copy 

from .. import config as _config
import pyg4ometry.exceptions

if _config.meshing == _config.meshingType.pycsg :
    from pyg4ometry.pycsg.core import CSG as _CSG
elif _config.meshing == _config.meshingType.cgal_sm :
    from pyg4ometry.pycgal.core import CSG as _CSG



import logging as _log
import numpy as _np

class OverlapType:
    protrusion = 1
    overlap    = 2
    coplanar   = 3

class Mesh(object):
    def __init__(self, solid) : 
        parameters = [] 
        values     = {}

        # solid which contains the mesh
        self.solid = solid 

        # mesh in local coordinates
        self.localmesh = self.solid.mesh()

        # bounding mesh in local coordinates
        self.localboundingmesh = self.getBoundingBoxMesh()

        # overlap meshes (protrusion, overlap, coplanar)
        self.overlapmeshes = []
        
    def remesh(self):
        # existing overlaps become invalid
        self.overlapmeshes = []

        # recreate mesh
        self.localmesh = self.solid.mesh().clone()

        # recreate bounding mesh
        self.localboundingmesh = self.getBoundingBoxMesh()

    def addOverlapMesh(self, mesh):
        self.overlapmeshes.append(mesh)

    def getLocalMesh(self):
        return self.localmesh

    def getBoundingBox(self, rotationMatrix=None, translation=None) :
        """
        Axes aligned bounding box. Can also provide a rotation and
        a translation (applied in that order) to the vertices.
        """
        return _getBoundingBox(self.localmesh, rotationMatrix, translation, self.solid)

    def getBoundingBoxMesh(self):
        bb = self.getBoundingBox()
        return _getBoundingBoxMesh(bb)


def _getBoundingBox(aMesh, rotationMatrix=None, translation=None, nameForError=""):
    """
    Axes aligned bounding box. Can also provide a rotation and
    a translation (applied in that order) to the vertices.
    """
    vertices, _, _ = aMesh.toVerticesAndPolygons()
    if not vertices:
        print("Warning> getBoundingBox null mesh error : ", nameForError)
        if _config.meshingNullException :
            raise pyg4ometry.exceptions.NullMeshError(nameForError)
        else :
            return [[-1e-9,-1e-9,-1e-9],[1e9,1e9,1e9]]
    vertices = _np.vstack(vertices)

    if rotationMatrix is not None:
        vertices = rotationMatrix.dot(vertices.T).T
    if translation is not None:
        vertices[...,0] += translation[0]
        vertices[...,1] += translation[1]
        vertices[...,2] += translation[2]

    vMin = [min(vertices[...,0]),
            min(vertices[...,1]),
            min(vertices[...,2])]
    vMax = [max(vertices[...,0]),
            max(vertices[...,1]),
            max(vertices[...,2])]

    _log.info('visualisation.Mesh.getBoundingBox> %s %s', vMin, vMax)

    return [vMin, vMax]

def _getBoundingBoxMesh(boundingBox):
    bb = boundingBox
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