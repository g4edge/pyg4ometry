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

class Material:
    """
    This class provides an interface to GDML material definitions. Material definitions are.

    Because of the different options for constructing a material instance the constructor is kwarg only.
    Proxy methods are prodived to instantiate particular types of material. Those proxy methods are:

    Material.simple
    Material.composite
    Material.nist

    It is possible to instantiate a material directly through kwargs. The possible kwargs are (but note some are mutually exclusive):
    name                 - string
    density              - float
    atomic_number        - int
    atomic_weight        - float
    number_of_components - int
    """
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

        elif "arbitrary" in kwargs:
            self.type = "arbitrary"

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
        """
        Proxy method to construct a NIST compund material - this is just a handle as nothing
        needs to be additionaly defined for a NIST compund. A check is perfored on the name
        to ensure it is a valid NIST specifier.

        Inputs:
          name          - string
        """
        if name not in _makeNISTCompoundList():
            raise IOError("{} is not a NIST compound".format(name))
        return cls(**locals())

    @classmethod
    def from_arbitrary_name(cls, name):
        """Just a name of a material.  WARNING:  It is left to the
        user to ensure that the name is valid.

        Inputs:
          name          - string
        """
        return cls(name=name, arbitrary=True)

    @classmethod
    def simple(cls, name, atomic_number, atomic_weight, density):
        """
        Proxy method to construct a simple material - full description of the element contained is contained in one definition

        Inputs:
          name          - string
          density       - float, material density in g/cm3
          atomic_number - int, total number of nucleons, commonly known as 'A'
          atomic_weght  - int, molar weight in g/mole, commonly known as 'a'
        """
        return cls(**locals())

    @classmethod
    def composite(cls, name, density, number_of_components):
        """
        Proxy method to construct a composite material - can be any mixure of Elements and/or Materials

        Inputs:
          name                 - string
          density              - float, material density in g/cm3
          number_of_components - int, number of components in the mixture
        """
        return cls(**locals())

    def add_element_massfraction(self, element, massfraction):
        """
        Add an element as a component to a material as a fraction of the material mass.
        Can only add elements to materials defined as composite.

        Inputs:
          element      - pyg4ometry.geant4.Material.Element instance
          massfraction - float, 0.0 < massfraction <= 1.0
        """
        if not isinstance(element, Element):
            raise IOError("Can only add Element instanes, recieved type {}".format(type(element)))

        if not self.number_of_components:
            raise IOError("This material is not specified as composite, cannot add elements.")

        self.components.append((element, massfraction, "massfraction"))
        _registry.addMaterial(self) #Refresh the registry representation

    def add_element_natoms(self, element, natoms):
        """
        Add an element as a component to a material as a number of atoms in the material molecule.
        Can only add elements to materials defined as composite.

        Inputs:
          element  - pyg4ometry.geant4.Material.Element instance
          natoms   - int, number of atoms in the compound molecule
        """
        if not isinstance(element, Element):
            raise IOError("Can only add Element instanes, recieved type {}".format(type(element)))

        if not self.number_of_components:
            raise IOError("This material is not specified as composite, cannot add elements.")

        self.components.append((element, natoms, "natoms"))
        _registry.addMaterial(self)

    def add_material(self, material, fractionmass):
        """
        Add a material as a component to another material (mixture) as a fraction of the mixture mass.
        Can only add new materials to materials defined as composite.

        Inputs:
          element      - pyg4ometry.geant4.Material.Material instance
          massfraction - float, 0.0 < massfraction <= 1.0
        """
        if not isinstance(material, Material):
            raise IOError("Can only add Material instanes, recieved type {}".format(type(material)))

        if not self.number_of_components:
            raise IOError("This material is not specified as composite, cannot add materials.")

        self.components.append((material, fractionmass, "massfraction"))
        _registry.addMaterial(self)

class Element:
    """
    This class provides an interface to GDML material definitions. Because of the different options for constructing a material instance the constructor is kwarg only.
    Proxy methods are prodived to instantiate particular types of material. Those proxy methods are:

    Element.simple
    Element.composite

    It is possible to instantiate a material directly through kwargs. The possible kwargs are (but note some are mutually exclusive):
    name                 - string
    symbol               - string
    Z                    - int
    A                    - int
    n_comp               - int
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.symbol = kwargs.get("symbol", None)
        self.n_comp = kwargs.get("n_comp", None)
        self.Z = kwargs.get("Z", None)
        self.A = kwargs.get("A", None)
        self.components = []

        if self.n_comp and not self.Z and not self.A:
            self.type = "composite"
        elif self.Z and self.A and not self.n_comp:
            self.type = "simple"
        else:
            raise IOError("Cannot use both atomic number/weight and number_of_components.")

    @classmethod
    def simple(cls, name, symbol, Z, A):
        """
        Proxy method to construct a simple element - full description of the element contained is contained in one definition

        Inputs:
          name   - string
          symbol - string, chemical formula of the compound
          Z      - int, atomic number
          A      - int, mass number
          a      - float, atomic weigth in g/mole
        """
        return cls(**locals())

    @classmethod
    def composite(cls, name, symbol, n_comp):
        """
        Proxy method to construct a composite element - a mixture of predefined isotopes

        Inputs:
          name - string
          symbol - string, chemical formula of the compound
          n_comp - int, number of isotope components
        """
        return cls(**locals())

    def add_isotope(self, isotope, abundance):
        """
        Add an isotope as a component to an element as an abundance fraction in the element.

        Inputs:
          element   - pyg4ometry.geant4.Material.Isotope instance
          abundance - float, 0.0 < abundance <= 1.0
        """
        if not isinstance(isotope, Isotope):
            raise IOError("Can only add Isotope instanes, recieved type {}".format(type(isotope)))

        self.components.append((isotope, abundance, "abundance"))

class Isotope:
    """
    This class that handles isotopes as components of composite materials. An element can be
    defined as a mixture of isotopes.

    Inputs:
        name - string
        Z    - int, atomic number
        N    - int, mass number
        a    - float, molar weigth in g/mole
    """
    def __init__(self, name, Z, N, a):
        self.name = name
        self.Z    = Z
        self.N    = N
        self.a    = a
