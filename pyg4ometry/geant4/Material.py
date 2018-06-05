from Registry import registry as _registry
import sys as _sys
import os as _os

def _getClassVariables(obj):
    var_dict = {key:value for key, value in obj.__dict__.items() if not key.startswith('__') and not callable(key)}
    return var_dict

def _makeNISTCompoundList():
    nist_compound_list = []

    here = _os.path.dirname(_os.path.abspath(__file__))
    nist_data = _os.path.join(here, "bdsim_materials.txt")

    with open(nist_data,"r") as f:
        line  = f.readline()
        while line:
            line_data = line.split()
            if line_data:
                nist_compound_list.append(line_data[1])
            line =f.readline()

    return nist_compound_list

class Material :
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.density = kwargs.get("density", None)
        self.atomic_number = kwargs.get("atomic_number", None)
        self.atomic_weight = kwargs.get("atomic_weight", None)
        self.number_of_components = kwargs.get("number_of_components", None)
        self.components = []

        self.NIST_compounds =  _makeNISTCompoundList()

        if not any(_getClassVariables(self)):
            self.type = "none"

        elif self.name in self.NIST_compounds:
            self.type = "nist"

        elif self.density:
            if self.number_of_components and not self.atomic_number:
                self.type = "composite"
            elif self.atomic_number and self.atomic_weight and not self.number_of_components:
                    self.type = "simple"
            else:
                raise IOError("Cannot use both atomic number/weight and number_of_components.")
        else:
            raise IOError("Density must be specified for custom materials.")

        _registry.addMaterial(self)

    @classmethod
    def nist(cls, name):
        if name not in _makeNISTCompoundList():
            raise IOError("{} is not a NIST compound".format(name))
        return cls(**locals())

    @classmethod
    def simple(cls, name, atomic_number, atomic_weight, density):
        return cls(**locals())

    @classmethod
    def composite(cls, name, density, number_of_components):
        return cls(**locals())

    def add_element_massfraction(self, element, massfraction):
        if not isinstance(element, Element):
            raise IOError("Can only add Element instanes, recieved type {}".format(type(element)))

        if not self.number_of_components:
            raise IOError("This material is not specified as composite, cannot add elements.")

        self.components.append((element, massfraction, "massfraction"))
        _registry.addMaterial(self) #Refresh the registry representation

    def add_element_natoms(self, element, natoms):
        if not isinstance(element, Element):
            raise IOError("Can only add Element instanes, recieved type {}".format(type(element)))

        if not self.number_of_components:
            raise IOError("This material is not specified as composite, cannot add elements.")

        self.components.append((element, natoms, "natoms"))
        _registry.addMaterial(self)

    def add_material(self, material, fractionmass):
        if not isinstance(material, Material):
            raise IOError("Can only add Material instanes, recieved type {}".format(type(material)))

        if not self.number_of_components:
            raise IOError("This material is not specified as composite, cannot add materials.")

        self.components.append((material, fractionmass, "massfraction"))
        _registry.addMaterial(self)

class Element :
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.symbol = kwargs.get("symbol", None)
        self.n_comp = kwargs.get("n_comp", None)
        self.z = kwargs.get("z", None)
        self.a = kwargs.get("a", None)
        self.components = []

        if self.n_comp and not self.z and not self.a:
            self.type = "composite"
        elif self.z and self.a and not self.n_comp:
            self.type = "simple"
        else:
            raise IOError("Cannot use both atomic number/weight and number_of_components.")

    @classmethod
    def simple(cls, name, symbol, z, a):
        return cls(**locals())

    @classmethod
    def composite(cls, name, symbol, n_comp):
        return cls(**locals())

    def add_isotope(self, isotope, abundance):
        if not isinstance(isotope, Isotope):
            raise IOError("Can only add Isotope instanes, recieved type {}".format(type(isotope)))

        self.components.append((isotope, abundance, "abundance"))

class Isotope :
    def __init__(self, name, Z, A, a):
        self.name = name
        self.Z    = Z
        self.A    = A
        self.a    = a
