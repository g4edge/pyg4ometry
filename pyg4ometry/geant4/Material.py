import sys as _sys
import os as _os
import pkg_resources


def _getClassVariables(obj):
    var_dict = {key:value for key, value in obj.__dict__.items() if not key.startswith('__') and not callable(key)}
    return var_dict


def _makeNISTCompoundList():

    return loadNISTMaterialDict().keys()

def loadNISTMaterialDict():
    nist_materials_dict = {}

    nist_data = pkg_resources.resource_filename(__name__, "bdsim_materials.txt")

    with open(nist_data,"r") as f:
        line  = f.readline()
        while line:
            if line[0] == '#' :
                line = f.readline()
                continue

            line_data = line.split()
            if line_data[0] == "element":
                type = line_data[0]
                z    = int(line_data[1])
                name = line_data[2]
                rho  = float(line_data[3])
                ion  = float(line_data[4])

                nist_materials_dict[name] = {'type':type, 'z':z, 'name':name, 'density':rho, 'ionisation':ion}
            elif line_data[0] == "compatom":
                type = line_data[0]
                ncom = int(line_data[1])
                name = line_data[2]
                rho  = float(line_data[3])
                ion  = float(line_data[4])

                components = []
                for i in range(0,ncom,1) :
                    comLine = f.readline()
                    comLineSplit = comLine.split()
                    z = int(comLineSplit[0])
                    n = int(comLineSplit[1])
                    components.append([z,n])
                nist_materials_dict[name] = {'type':type, 'ncom':ncom, 'name':name, 'density':rho, 'ionisation':ion, 'components':components}

            elif line_data[0] == "compmass":
                type = line_data[0]
                ncom = int(line_data[1])
                name = line_data[2]
                rho  = float(line_data[3])
                ion  = float(line_data[4])

                components = []
                for i in range(0,ncom,1) :
                    comLine = f.readline()
                    comLineSplit = comLine.split()
                    z    = int(comLineSplit[0])
                    frac = float(comLineSplit[1])
                    components.append([z,frac])
                nist_materials_dict[name] = {'type':type, 'ncom':ncom, 'name':name, 'density':rho, 'ionisation':ion, 'components':components}

            line =f.readline()

    return nist_materials_dict

nist_materials_dict = loadNISTMaterialDict()
nist_materials_list = nist_materials_dict.keys()

def MaterialPredefined(name, registry=None):
    """
    Proxy method to construct a NIST compund material - this is just a handle as nothing
    needs to be additionaly defined for a NIST compund. A check is perfored on the name
    to ensure it is a valid NIST specifier.

    Inputs:
        name          - string
    """
    if name not in nist_materials_list:
        raise ValueError("{} is not a NIST compound".format(name))
    return Material(**locals())


def MaterialArbitrary(name, registry=None):
    """Just a name of a material.  WARNING:  It is left to the
    user to ensure that the name is valid.

    Inputs:
        name          - string
    """
    return Material(name=name, arbitrary=True, registry=registry)


def MaterialSingleElement(name, atomic_number, atomic_weight, density, registry=None):
    """
    Proxy method to construct a simple material - full description of the element contained is contained in one definition

    Inputs:
        name          - string
        density       - float, material density in g/cm3
        atomic_number - int, number of protons, commonly known as 'Z'
        atomic_weight  - molar weight in g/mole, commonly known as 'A'
    """
    return Material(**locals())


def MaterialCompound(name, density, number_of_components, registry=None):
    """
    Proxy method to construct a composite material - can be any mixure of Elements and/or Materials

    Inputs:
        name                 - string
        density              - float, material density in g/cm3
        number_of_components - int, number of components in the mixture
    """
    return Material(**locals())


def ElementSimple(name, symbol, Z, A, registry=None):
    """
    Proxy method to construct a simple element - full description of the element contained is contained in one definition

    Inputs:
        name   - string
        symbol - string, chemical formula of the compound
        Z      - int, Atomic number
        A      - float, mass number
    """
    return Element(**locals())


def ElementIsotopeMixture(name, symbol, n_comp, registry=None):
    """
    Proxy method to construct a composite element - a mixture of predefined isotopes

    Inputs:
        name - string
        symbol - string, chemical formula of the compound
        n_comp - int, number of isotope components
    """
    return Element(**locals())


class MaterialBase(object):
    def __init__(self, name, registry=None):
        self.name = name
        self.registry = registry

        if self.registry is not None:
            self.registry.addMaterial(self)

    def get_material_oject(self, material):
        if isinstance(material, str):
            if self.registry is not None:
                try:
                    material_obj = self.registry.materialDict[material]
                except KeyError:
                    raise KeyError("Material {} not found in registry".format(material))
            else:
                raise KeyError("No registry supplied, cannot look up materials by name")
        else:
            material_obj = material

        return material_obj

    def set_registry(self, registry):  # Assign a registry post-construction
        self.registry = registry
        self.registry.addMaterial(self)

        if hasattr(self, "components"):  # Recursively set the registry for all components
            for comp in self.components:
                comp[0].set_registry(registry)

    def __repr__(self):
        return "{}".format(self.name)


class Material(MaterialBase):
    """
    This class provides an interface to GDML material definitions. Material definitions are.

    Because of the different options for constructing a material instance the constructor is kwarg only.
    Proxy methods are prodived to instantiate particular types of material. Those proxy methods are:

    MaterialSingleElement
    MaterialCompound
    MaterialPredefined

    It is possible to instantiate a material directly through kwargs.
    The possible kwargs are (but note some are mutually exclusive):
    name                 - string
    density              - float
    atomic_number        - int
    atomic_weight        - float
    number_of_components - int
    """
    def __init__(self, **kwargs):
        super(Material, self).__init__(kwargs.get("name", None), kwargs.get("registry", None))

        self.density = kwargs.get("density", None)
        self.atomic_number = kwargs.get("atomic_number", None)
        self.atomic_weight = kwargs.get("atomic_weight", None)
        self.number_of_components = kwargs.get("number_of_components", None)
        self.components = []
        self.properties = {}

        self._state = {"temperature": None,
                       "temperature_unit": None,
                       "pressure": None,
                       "pressure_unit": None}

        self.NIST_compounds =  nist_materials_list

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
                raise ValueError("Cannot use both atomic number/weight and number_of_components.")
        else:
            raise ValueError("Density must be specified for custom materials.")

    def add_property(self, name, value):
        if self.type == 'nist' or self.type == 'arbitraty':
            raise ValueError("Properties cannot be set of "
                             "predefined or arbitrary materials")
        self.properties[name] = value

    def add_element_massfraction(self, element, massfraction):
        """
        Add an element as a component to a material as a fraction of the material mass.
        Can only add elements to materials defined as composite.

        Inputs:
          element      - pyg4ometry.geant4.Material.Element instance
          massfraction - float, 0.0 < massfraction <= 1.0
        """
        element_obj = self.get_material_oject(element)

        if not isinstance(element_obj, Element):
            raise ValueError("Can only add Element instanes, recieved type {}".format(type(element)))

        if not self.number_of_components:
            raise ValueError("This material is not specified as composite, cannot add elements.")

        self.components.append((element_obj, massfraction, "massfraction"))

    def add_element_natoms(self, element, natoms):
        """
        Add an element as a component to a material as a number of atoms in the material molecule.
        Can only add elements to materials defined as composite.

        Inputs:
          element  - pyg4ometry.geant4.Material.Element instance
          natoms   - int, number of atoms in the compound molecule
        """
        element_obj = self.get_material_oject(element)

        if not isinstance(element_obj, Element):
            raise ValueError("Can only add Element instanes, recieved type {}".format(type(element)))

        if not self.number_of_components:
            raise ValueError("This material is not specified as composite, cannot add elements.")

        self.components.append((element_obj, natoms, "natoms"))

    def add_material(self, material, fractionmass):
        """
        Add a material as a component to another material (mixture) as a fraction of the mixture mass.
        Can only add new materials to materials defined as composite.

        Inputs:
          material     - pyg4ometry.geant4.Material.Material instance
          massfraction - float, 0.0 < massfraction <= 1.0
        """
        material_obj = self.get_material_oject(material)

        if not isinstance(material_obj, Material):
            raise ValueError("Can only add Material instances,"
                             " recieved type {}".format(type(material_obj)))

        if not self.number_of_components:
            raise ValueError("This material is not specified as composite, cannot add materials.")

        self.components.append((material_obj, fractionmass, "massfraction"))

    def set_pressure(self, value, unit="pascal"):
        if self.type in ["predefined", "arbitrary"]:
            raise ValueError("Cannot set pressure for predefined or aribtrary materials.")

        self._state["pressure"] = value
        self._state["pressure_unit"] = unit

    def set_temperature(self, value, unit="K"):
        if self.type in ["nist", "arbitrary"]:
            raise ValueError("Cannot set temperature for predefined or aribtrary materials.")
        self._state["temperature"] = value
        self._state["temperature_unit"] = unit

    @property
    def state(self):
        return self._state

    def __str__(self):
        return self.name


class Element(MaterialBase):
    """
    This class provides an interface to GDML material definitions. Because of the different options
    for constructing a material instance the constructor is kwarg only.
    Proxy methods are prodived to instantiate particular types of material. Those proxy methods are:

    Element.simple
    Element.composite

    It is possible to instantiate a material directly through kwargs.
    The possible kwargs are (but note some are mutually exclusive):
    name                 - string
    symbol               - string
    Z                    - int
    A                    - int
    n_comp               - int
    """
    def __init__(self, **kwargs):
        super(Element, self).__init__(kwargs.get("name", None), kwargs.get("registry", None))

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
            raise ValueError("Cannot use both atomic number/weight and number_of_components.")

    def add_isotope(self, isotope, abundance):
        """
        Add an isotope as a component to an element as an abundance fraction in the element.

        Inputs:
          element   - pyg4ometry.geant4.Material.Isotope instance
          abundance - float, 0.0 < abundance <= 1.0
        """
        isotope_obj = self.get_material_oject(isotope)
        if not isinstance(isotope, Isotope):
            raise ValueError("Can only add Isotope instanes, recieved type {}".format(type(isotope)))

        self.components.append((isotope_obj, abundance, "abundance"))


class Isotope(MaterialBase):
    """
    This class that handles isotopes as components of composite materials. An element can be
    defined as a mixture of isotopes.

    Inputs:
        name - string
        Z    - int, atomic number
        N    - int, mass number
        a    - float, molar weight in g/mole
    """
    def __init__(self, name, Z, N, a, registry=None):
        super(Isotope, self).__init__(name, registry)
        self.Z    = Z
        self.N    = N
        self.a    = a
