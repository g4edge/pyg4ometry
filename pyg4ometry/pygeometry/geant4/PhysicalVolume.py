from pygeometry.geant4.Registry import registry as _registry
import copy as _copy
from pygeometry.transformation import *
from pygeometry.geant4.Parameter import Parameter as _Parameter
from pygeometry.geant4.ParameterVector import ParameterVector as _ParameterVector

import sys as _sys

class PhysicalVolume(object):
    imeshed = 0
    def __init__(self, rotation, position, logicalVolume, name, motherVolume, scale = [1,1,1], debug= False):
        super(PhysicalVolume, self).__init__()
        self.rotation      = rotation
        self.position      = position
        self.logicalVolume = logicalVolume
        self.name          = name 
        self.motherVolume  = motherVolume
        self.motherVolume.add(self)
        self.mesh          = None
        self.scale         = scale
        self.debug         = debug
        _registry.addPhysicalVolume(self)

    def __repr__(self) : 
        return 'Physical Volume : '+self.name+' '+str(self.rotation)+' '+str(self.position)
        
    def pycsgmesh(self) :

        PhysicalVolume.imeshed = PhysicalVolume.imeshed + 1
        if self.debug :
            print 'PhysicalVolume mesh count',PhysicalVolume.imeshed

        #if self.mesh :
        #    return self.mesh

        # see if the volume should be skipped
        try :
            _registry.logicalVolumeMeshSkip.index(self.logicalVolume.name)
            if self.debug:
                print "Physical volume skipping ---------------------------------------- ",self.name
            return []
        except ValueError :
            if list(self.position) == [0,0,0] and list(self.rotation) == [0,0,0] :
                self.mesh = self.logicalVolume.pycsgmesh()
            else :
                lvmesh = self.logicalVolume.pycsgmesh()
                self.mesh = _copy.deepcopy(lvmesh)

                # Mesh is only placed once remove the logical mesh as it will not be used again
                if _registry.logicalVolumeUsageCountDict[self.logicalVolume.name] == 1 :
                    self.logicalVolume.mesh = None

        # loop over daughter meshes
        recursize_map_rottrans(self.mesh,list(self.position),tbxyz(list(self.rotation)),list(self.scale))

        if self.debug :
            print 'physical mesh', self.name
            recursive_map_size(self.mesh)
        
        return self.mesh

    def gdmlWrite(self, gw, prepend) : 
        # physical volume
        pv = gw.doc.createElement('physvol')
        pv.setAttribute('name',prepend+'_'+self.name+'_pv')
        vr = gw.doc.createElement('volumeref')
        vr.setAttribute('ref',prepend+'_'+self.logicalVolume.name+'_lv')
        pv.appendChild(vr)

        # phys vol translation
        if isinstance(self.position,_ParameterVector) :
            tlatee = gw.doc.createElement('positionref')
            tlatee.setAttribute('ref',str(self.position))
            pv.appendChild(tlatee)
        else :
            tlatee = gw.doc.createElement('position')
            tlatee.setAttribute('name',prepend+'_'+self.name+'_pos')
            tlatee.setAttribute('x',str(self.position[0]))
            tlatee.setAttribute('y',str(self.position[1]))
            tlatee.setAttribute('z',str(self.position[2]))
            pv.appendChild(tlatee)



        # phys vol rotation
        rote   = gw.doc.createElement('rotation')
        rote.setAttribute('name',prepend+'_'+self.name+'_rot')
        rote.setAttribute('x',str(self.rotation[0]))
        rote.setAttribute('y',str(self.rotation[1]))
        rote.setAttribute('z',str(self.rotation[2]))
        pv.appendChild(rote)

        # phys vol scale
        tscae = gw.doc.createElement('scale')
        tscae.setAttribute('name',prepend+'_'+self.name+'_sca')
        tscae.setAttribute('x',str(self.scale[0]))
        tscae.setAttribute('y',str(self.scale[1]))
        tscae.setAttribute('z',str(self.scale[2]))
        pv.appendChild(tscae)    

        return pv
                           
def recursize_map_rottrans(nlist,trans,rot,scale = [1,1,1]):
    '''Function to apply transformation (rot then trans) to nested list of meshes (nlist)'''
    for i in range(len(nlist)) :
        if isinstance(nlist[i],list) :
            recursize_map_rottrans(nlist[i],trans,rot,scale)
        else :
            nlist[i].scale(scale)
            nlist[i].rotate(rot[0],rad2deg(rot[1]))
            nlist[i].translate(trans)

def recursive_map_size(nlist) :
    '''Recursive application of .polygonCount() and .vertexCount() to meshlist
    :argument nlist
    '''
    for i in range(len(nlist)) :
        if isinstance(nlist[i],list) :
            recursive_map_size(nlist[i])
        else :
            print 'PhysicalVolume.recursize_map_size : polygons, vertices', nlist[i].polygonCount(), nlist[i].vertexCount()
