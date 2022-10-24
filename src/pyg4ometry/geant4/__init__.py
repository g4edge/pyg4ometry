"""
Geant4 classes. The classes mainly match those of Geant4
"""

def IsAReplica(logicalVolume):
    """
    Utility function to test if an LV is really a replica volume. A replica is a special case
    where we have an in-effect dummy mother and is detectable by there only being 1 daughter
    and it being a ReplicaVolume instance.
    """
    replicaCondition1 = len(logicalVolume.daughterVolumes) == 1
    replicaCondition2 = False
    if replicaCondition1:  # can only do this if len > 0
        replicaCondition2 = type(logicalVolume.daughterVolumes[0]) is ReplicaVolume
    itsAReplica = replicaCondition1 and replicaCondition2
    return itsAReplica

from .LogicalVolume import *
from .PhysicalVolume import *
from .AssemblyVolume import *
from .ReplicaVolume import *
from .ParameterisedVolume import *
from .DivisionVolume import *
from .SkinSurface import *
from .BorderSurface import *
from .Registry import *
from ._Material import *
from .Expression import *
from . import solid
