from .SolidBase import SolidBase as _SolidBase
from .._Material import WithPropertiesBase
import warnings

class OpticalSurface(_SolidBase, WithPropertiesBase):
    # from G4OpticalSurface.hh and G4SurfaceProperty.hh of Geant4 11.0
    allowed_models    = ['glisur', 'unified', 'LUT', 'DAVIS', 'dichroic']
    allowed_types     = ['dielectric_metal', 'dielectric_dielectric', 'dielectric_LUT', 'dielectric_LUTDAVIS', 'dielectric_dichroic', 'firsov', 'x_ray']
    allowed_finishes  = ['polished', 'polishedfrontpainted', 'polishedbackpainted', 'ground', 'groundfrontpainted', 'groundbackpainted', 'polishedlumirrorair', 'polishedlumirrorglue', 'polishedair', 'polishedteflonair', 'polishedtioair', 'polishedtyvekair', 'polishedvm2000air', 'polishedvm2000glue', 'etchedlumirrorair', 'etchedlumirrorglue', 'etchedair', 'etchedteflonair', 'etchedtioair', 'etchedtyvekair', 'etchedvm2000air', 'etchedvm2000glue', 'groundlumirrorair', 'groundlumirrorglue', 'groundair', 'groundteflonair', 'groundtioair', 'groundtyvekair', 'groundvm2000air', 'groundvm2000glue', 'Rough_LUT', 'RoughTeflon_LUT', 'RoughESR_LUT', 'RoughESRGrease_LUT', 'Polished_LUT', 'PolishedTeflon_LUT', 'PolishedESR_LUT', 'PolishedESRGrease_LUT', 'Detector_LUT']

    def __init__(self, name, finish, model, surf_type, value, registry, addRegistry=True):
        """
        Construct an optical surface.

        :param name:    of this optical surface
        :type name:     str,int
        :param finish:  One of the allowed surface finishes
        :type finish:   str,int
        :param model:   One of the allowed surface models
        :type model:    str,int
        :param surf_type: One of the allowed surface types
        :type surf_type: str,int
        :param value:   numeric parameter, depending on the model
        :type value:    str,float,int
        """
        super(OpticalSurface, self).__init__(name, 'OpticalSurface', registry)
        self.finish = finish
        self.model  = model
        self.osType = surf_type
        self.value  = value
        self.properties = {}

        # numeric values are also allowed: G4GDMLReadSolids.cc
        if not self.model in self.allowed_models and (not self.model.isdigit() or not int(self.model) in range(0,5)):
            warnings.warn(f'OpticalSurface {self.name} has unkown surface model {self.model}')
        if not self.osType in self.allowed_types and (not self.osType.isdigit() or not int(self.osType) in range(0,39)):
            warnings.warn(f'OpticalSurface {self.name} has unkown surface type {self.osType}')
        if not self.finish in self.allowed_finishes and (not self.finish.isdigit() or not int(self.finish) in range(0,7)):
            warnings.warn(f'OpticalSurface {self.name} has unkown surface finish {self.finish}')

        if addRegistry:
            registry.addSolid(self)

    def __repr__(self):
        return 'OpticalSurface : '+str(self.name)

    def addProperty(self, name, matrix):
        """
        Add a property to this surface from a matrix.

        :param name: key of the surface property
        :type name: str
        :param matrix: matrix defining the value(s) of the property
        :type matrix: Matrix
        """
        self.properties[name] = matrix
