import pyg4ometry.transformation as _trans
from pyg4ometry.visualisation import VisualisationOptions as _VisOptions
import pyg4ometry.geant4.solid as _solid
from   pyg4ometry.visualisation  import Mesh as _Mesh

import numpy as _np
import logging as _log

class PhysicalVolume(object):
    """
    PhysicalVolume : G4VPhysicalVolume, G4PVPlacement
    
    :param rotation: [float,float,float] - rotations about x,y,z axes of mother volume
    :param position: [float,float,float] - translation with respect to mother volume
    :param logicalVolume: :class:`pyg4ometry.geant4.LogicalVolume` - instance to place 
    :param name: str - name of this placement
    :param motherVolume: :class:`pyg4ometry.geant4.LogicalVolume` - mother volume to place into
    :param registry: :class:`pyg4ometry.geant4.Registry` - registry to register to
    :param copyNumber: int - copy number of the placement that can be used for sensitivity
    :param addRegistry: bool - whether to add to the registry or not
    """
    def __init__(self, rotation, position, logicalVolume, name,
                 motherVolume, registry=None, copyNumber=0, addRegistry=True, scale=None):
        super(PhysicalVolume, self).__init__()

        if logicalVolume == motherVolume:
            raise ValueError("Cannot place a volume inside itself -> recursive")

        # type 
        self.type = "placement"
    
        # need to determine type or rotation and position, as should be Position or Rotation type
        from pyg4ometry.gdml import Defines as _Defines

        if isinstance(position,list) or isinstance(position,_np.ndarray):
            if len(position) == 3:
                unit = "mm"
            elif len(position) == 4:
                unit = position[3]
            else:
                raise ValueError("Position array must be in the format"
                                 " [px, py, pz] or [px, py, pz, unit]")

            position = _Defines.Position(name+"_pos",position[0],position[1],position[2],unit,registry,False)
        if isinstance(rotation,list) or isinstance(position,_np.ndarray):
            if len(rotation) == 3:
                unit = "rad"
            elif len(rotation) == 4:
                unit = rotation[3]
            else:
                raise ValueError("Rotation array must be in the format"
                                 "[rx, ry, rz] or [rx, ry, rz, unit]")

            rotation = _Defines.Rotation(name+"_rot",rotation[0],rotation[1],rotation[2],unit,registry,False)
        if isinstance(scale,list) :
            if not len(scale) == 3:
                raise ValueError("Scale array must be in the format"
                                 "[sx, sy, sz]")

            scale    = _Defines.Scale(name+"_sca",scale[0],scale[1],scale[2],"none",registry,False)


        # geant4 required objects
        self.rotation      = rotation
        self.position      = position
        self.scale         = scale
        self.logicalVolume = logicalVolume
        self.name          = name
        self.motherVolume  = motherVolume
        if self.motherVolume :
            self.motherVolume.add(self)
        self.copyNumber    = copyNumber
        
        # physical visualisation options 
        self.visOptions    = _VisOptions()

        # registry logic
        if registry and addRegistry :
            registry.addPhysicalVolume(self)
        self.registry = registry

    def __repr__(self):
        return 'Physical Volume : '+self.name+' '+str(self.rotation)+' '+str(self.position)

    def extent(self, includeBoundingSolid = True) :
        _log.info('PhysicalVolume.extent> %s' % (self.name))

        # transform daughter meshes to parent coordinates
        dvmrot = _trans.tbxyz2matrix(self.rotation.eval())
        dvtra = _np.array(self.position.eval())

        [vMin,vMax] = self.logicalVolume.extent(includeBoundingSolid)

        # TODO do we need scale here?
        vMinPrime = _np.array((dvmrot.dot(vMin) + dvtra)).flatten()
        vMaxPrime = _np.array((dvmrot.dot(vMax) + dvtra)).flatten()

        vmin = [min(a, b) for a, b in zip(vMinPrime, vMaxPrime)]
        vmax = [max(a, b) for a, b in zip(vMinPrime, vMaxPrime)]

        return [vmin, vmax]

    def getAABBMesh(self):
        '''return CSG.core (symmetric around the origin) axis aligned bounding box mesh'''

        extent = self.extent()

        x = max(abs(extent[0][0]),extent[1][0])
        y = max(abs(extent[0][1]),extent[1][1])
        z = max(abs(extent[0][2]),extent[1][2])

        bs = _solid.Box(self.name+"_aabb",x,y,z,self.registry,"mm",False)

        bm = _Mesh(bs)

        return bm.localmesh