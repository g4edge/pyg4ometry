import warnings
from collections import OrderedDict as _OrderedDict
from copy import deepcopy

import pyg4ometry.geant4 as _g4
from .Region import Region

from pyg4ometry.exceptions import IdenticalNameError


WORLD_DIMENSIONS = 10000

class FlukaRegistry(object):
    def __init__(self) :
        self.bodyDict          = _OrderedDict()
        self.bodyTransformDict = _OrderedDict()
        self.regionDict        = _OrderedDict()
        self.materialDict      = _OrderedDict()
        self.latticeDict       = _OrderedDict()
        self.cardDict          = _OrderedDict()

    def addBody(self, body):
        if body.name in self.bodyDict:
            raise IdenticalNameError(body.name)
        self.bodyDict[body.name] = body

    def addBodyTransform(self, trans):
        self.bodyTransformDict[trans.name] = trans

    def addRegion(self, region):
        self.regionDict[region.name] = region

    def addMaterial(self, material):
        self.materialDict.add(material)

    def addLattice(self, lattice):
        self.latticeDict.add(lattice)

    def getBody(self, name):
        return self.bodyDict[name]

    def printDefinitions(self):
        print "bodyDict = {}".format(self.bodyDict)
        print "bodyTransformDict = {}".format(self.bodyTransformDict)
        print "regionDict = {}".format(self.regionDict)
        print "materialDict = {}".format(self.materialDict)
        print "latticeDict = {}".format(self.latticeDict)
        print "cardDict = {}".format(self.cardDict)

    def _make_length_safety_registry(self):
        bigger = FlukaRegistry()
        smaller = FlukaRegistry()
        for name, body in self.bodyDict.iteritems():
            try:
                bigger.addBody(body.safety_expanded())
                smaller.addBody(body.safety_shrunk())
            except AttributeError:
                warnings.warn(
                    "No length safety supported for body type {}.".format(
                        type(body).__name__))
                bigger.addBody(body)
                smaller.addBody(body)

        # return bigger, smaller
        fluka_reg_out = FlukaRegistry()
        for name, region in self.regionDict.iteritems():
            ls_region = region.with_length_safety(bigger, smaller)
            fluka_reg_out.addRegion(ls_region)
            ls_region.allBodiesToRegistry(fluka_reg_out)

        return fluka_reg_out

    def _make_disjoint_unions_registry(self):
        fluka_reg_out = FlukaRegistry()
        for name, region in self.regionDict.iteritems():
            if len(region.zones) == 1: # can't be any disjoint unions if 1 zone.
                fluka_reg_out.addRegion(deepcopy(region))
                continue

            connected_zones = region.get_connected_zones()
            if len(connected_zones) == 1: # then there are no disjoint unions
                fluka_reg_out.addRegion(deepcopy(region))
                continue

            for connection in connected_zones: # loop over the connections

                # make new region with appropriate name
                zones_string = "_".join(map(str, connection))
                new_region_name = "{}_djz{}".format(name, zones_string)
                new_region = Region(new_region_name, material=region.material)

                # get the zones which are connected
                zones = [(i, region.zones[i]) for i in connection]
                for index, zone in zones:
                    # copy teh zone, give it a new name since it now
                    # belongs to a different region.
                    new_zone = deepcopy(zone)
                    new_zone.name = "{}_djz_z{}".format(new_zone.name, index)
                    new_region.addZone(new_zone)
                    new_region.allBodiesToRegistry(fluka_reg_out)
                    fluka_reg_out.addRegion(new_region)

        return fluka_reg_out

    def toG4Registry(self, with_length_safety=True, split_disjoint_unions=True):
        flukareg = self
        if with_length_safety:
            flukareg = flukareg._make_length_safety_registry()

        if split_disjoint_unions:
            flukareg = flukareg._make_disjoint_unions_registry()

        if not flukareg.regionDict:
            raise ValueError("No regions in registry.")

        greg = _g4.Registry()

        wm = _g4.MaterialPredefined("G4_Galactic")

        ws = _g4.solid.Box("ws",
                           WORLD_DIMENSIONS,
                           WORLD_DIMENSIONS,
                           WORLD_DIMENSIONS, greg, "mm")
        wlv = _g4.LogicalVolume(ws, wm, "wl", greg)



        for name, region in flukareg.regionDict.iteritems():
            region_solid = region.geant4_solid(greg)
            region_material = _g4.MaterialPredefined("G4_Fe")
            region_lv = _g4.LogicalVolume(region_solid,
                                          region_material,
                                          "{}_lv".format(name),
                                          greg)
            region_pv = _g4.PhysicalVolume(list(region.tbxyz()),
                                           list(region.centre()),
                                           region_lv,
                                           "{}_pv".format(name),
                                           wlv, greg)

        greg.setWorld(wlv.name)
        return greg
