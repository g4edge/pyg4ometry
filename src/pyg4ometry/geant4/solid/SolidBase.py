#import time as _time
import numpy as _np
from pyg4ometry import config as _config

class SolidBase(object):
    """
    Base class for all solids
    """
    def __init__(self, name, type, registry=None):
        self.name = name
        self.type = type
        self.registry = registry

    def evaluateParameter(self, obj):
        from pyg4ometry.gdml.Defines import evaluateToFloat
        return evaluateToFloat(self.registry, obj)

    def evaluateParameterWithUnits(self, varName):
        import pyg4ometry.gdml.Units as _Units

        var = getattr(self, varName)
        varVal = self.evaluateParameter(var)

        whichUnit = self.varUnits[self.varNames.index(varName)]
        if whichUnit:
            unitVal = _Units.unit(getattr(self, whichUnit))
        else:
            unitVal = 1

        if isinstance(varVal,float):
            return unitVal * varVal
        elif isinstance(varVal,list):
            return [ unitVal * val for val in varVal ]
        else:
            # we just deal with the straightforward cases here
            # solids that are more complicated should override this function
            # for now, just return the value without dealing with units
            return varVal

    def _addProperty(self, attribute):
        #create local setter and getter with a particular attribute name
        if hasattr(self.__class__, attribute):
            return

        getter = lambda self: self._getProperty(attribute)
        setter = lambda self, value: self._setProperty(attribute, value)

        #construct property attribute and add it to the class
        setattr(self.__class__, attribute, property(fget=getter,
                                                    fset=setter,
                                                    doc="Auto-generated method"))

    def _setProperty(self, attribute, value):
        #print "Setting: %s = %s" %(attribute, value) # DEBUG
        # When setting a parameter of a solid, add the solid name
        # to a list of edited solids in the registry. This forces a fresh
        # meshing for visualisation, instead of using the cached mesh.
        self.registry.registerSolidEdit(self)
        setattr(self, '_' + attribute, value)

    def _getProperty(self, attribute):
        #print "Getting: %s" %str(attribute) # DEBUG
        return getattr(self, "_" + attribute)

    def _twoPiValueCheck(self, attribute, aunit="rad"):
        """
        Raises a ValueError if the attribute is over pyg4ometry.config.twoPiComparisonTolerance **over** 2 x pi.
        """
        import pyg4ometry.gdml.Units as _Units  # TODO move circular import
        v = self.evaluateParameter(getattr(self, attribute)) * (_Units.unit(aunit))
        # note no abs() on this check on purpose
        if (v - 2 * _np.pi) > _config.twoPiComparisonTolerance:
            raise ValueError("pDPhi is strictly greater than 2 x pi in solid \"" + self.name + "\"")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        '''
        non_alphanum = set([c for c in name if not c.isalnum()])
        non_alphanum = non_alphanum.difference('_')  # underscores are # OK.
        non_alphanum = non_alphanum.difference('.')  #
        if non_alphanum:
            msg = \
                'Forbidden character(s) in name "{}": {}.'.format(name,
                    list(non_alphanum))
            raise ValueError(msg)
        if not name[0].isalpha():
            msg = \
                'First char of name "{}" must be a letter.'.format(name)
            raise ValueError(msg)
        '''
        self._name = name

    def conver2Tessellated(self):
        """
        return a TessellatedSolid instance based on the mesh of this solid.
        """
        pycsg_mesh = self.mesh()

        from pyg4ometry.geant4.solid import TessellatedSolid
        from pyg4ometry.visualisation import Convert as _Convert
        import vtk as _vtk
        # Use VTK to reduce all polygons to triangles
        # as CSG operations can produce arbitrary polygons
        # which cannot be used in Tessellated Solid
        meshVTKPD = _Convert.pycsgMeshToVtkPolyData(pycsg_mesh)
        vtkFLT = _vtk.vtkTriangleFilter()
        vtkFLT.AddInputData(meshVTKPD)
        vtkFLT.Update()
        triangular = vtkFLT.GetOutput()

        meshTriangular = []
        for i in range(triangular.GetNumberOfCells()):
            pts = triangular.GetCell(i).GetPoints()
            vertices = [pts.GetPoint(i) for i in range(pts.GetNumberOfPoints())]
            # The last 3-tuple is a dummy normal to make it look like STL data
            meshTriangular.append((vertices, (None, None, None)))

        newName = self.name + "_asTesselated"
        reg = self.registry
        mesh_type = TessellatedSolid.MeshType.Stl
        tesselated_solid = TessellatedSolid(newName, meshTriangular, reg, meshtype=mesh_type)

        return tesselated_solid

    #def mesh(self):
    #    start = _time.time()
    #   m = self.pycsgmesh()
    #    elapsed_time_fl = (_time.time() - start)
    #    print(elapsed_time_fl)
    #    print(len(m.polygons))
    #    return m
