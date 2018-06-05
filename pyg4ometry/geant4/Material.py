from Registry import registry as _registry
import sys as _sys

def _getClassVariables(obj):
    var_dict = {key:value for key, value in obj.__dict__.items() if not key.startswith('__') and not callable(key)}
    return var_dict

def _makeNISTCompoundList():
    nist_compount_list = [
        "G4_CELLULOSE_CELLOPHANE",
        "G4_Galactic", "G4_H", "G4_He", "G4_Li",
        "G4_Be", "G4_B", "G4_C", "G4_N",
        "G4_O", "G4_F", "G4_Ne", "G4_Na",
        "G4_Mg", "G4_Al", "G4_Si", "G4_P",
        "G4_S", "G4_Cl", "G4_Ar", "G4_K",
        "G4_Ca", "G4_Sc", "G4_Ti", "G4_V",
        "G4_Cr", "G4_Mn", "G4_Fe", "G4_Co",
        "G4_Ni", "G4_Cu", "G4_Zn", "G4_Ga",
        "G4_Ge", "G4_As", "G4_Se", "G4_Br",
        "G4_Kr", "G4_Rb", "G4_Sr", "G4_Y",
        "G4_Zr", "G4_Nb", "G4_Mo", "G4_Tc",
        "G4_Ru", "G4_Rh", "G4_Pd", "G4_Ag",
        "G4_Cd", "G4_In", "G4_Sn", "G4_Sb",
        "G4_Te", "G4_I", "G4_Xe", "G4_Cs",
        "G4_Ba", "G4_La", "G4_Ce", "G4_Pr",
        "G4_Nd", "G4_Pm", "G4_Sm", "G4_Eu",
        "G4_Gd", "G4_Tb", "G4_Dy", "G4_Ho",
        "G4_Er", "G4_Tm", "G4_Yb", "G4_Lu",
        "G4_Hf", "G4_Ta", "G4_W", "G4_Re",
        "G4_Os", "G4_Ir", "G4_Pt", "G4_Au",
        "G4_Hg", "G4_Tl", "G4_Pb", "G4_Bi",
        "G4_Po", "G4_At", "G4_Rn", "G4_Fr",
        "G4_Ra", "G4_Ac", "G4_Th", "G4_Pa",
        "G4_U", "G4_Np", "G4_Pu", "G4_Am",
        "G4_Cm", "G4_Bk", "G4_Cf", "G4_A-150_TISSUE",
        "G4_ACETONE", "G4_ACETYLENE", "G4_ADENINE", "G4_ADIPOSE_TISSUE_ICRP",
        "G4_AIR", "G4_ALANINE", "G4_ALUMINUM_OXIDE", "G4_AMBER",
        "G4_AMMONIA", "G4_ANILINE", "G4_ANTHRACENE", "G4_B-100_BONE",
        "G4_BAKELITE", "G4_BARIUM_FLUORIDE", "G4_BARIUM_SULFATE", "G4_BENZENE",
        "G4_BERYLLIUM_OXIDE", "G4_BGO", "G4_BLOOD_ICRP", "G4_BONE_COMPACT_ICRU",
        "G4_BONE_CORTICAL_ICRP", "G4_BORON_CARBIDE", "G4_BORON_OXIDE", "G4_BRAIN_ICRP",
        "G4_BUTANE", "G4_N-BUTYL_ALCOHOL", "G4_C-552", "G4_CADMIUM_TELLURIDE",
        "G4_CADMIUM_TUNGSTATE", "G4_CALCIUM_CARBONATE", "G4_CALCIUM_FLUORIDE", "G4_CALCIUM_OXIDE",
        "G4_CALCIUM_SULFATE", "G4_CALCIUM_TUNGSTATE", "G4_CARBON_DIOXIDE", "G4_CARBON_TETRACHLORIDE",
        "G4_CELLULOSE_CELLOPHANE", "G4_CELLULOSE_BUTYRATE", "G4_CELLULOSE_NITRATE", "G4_CERIC_SULFATE",
        "G4_CESIUM_FLUORIDE", "G4_CESIUM_IODIDE", "G4_CHLOROBENZENE", "G4_CHLOROFORM",
        "G4_CONCRETE", "G4_CYCLOHEXANE", "G4_1,2-DICHLOROBENZENE", "G4_DICHLORODIETHYL_ETHER",
        "G4_1,2-DICHLOROETHANE", "G4_DIETHYL_ETHER", "G4_N,N-DIMETHYL_FORMAMIDE", "G4_DIMETHYL_SULFOXIDE",
        "G4_ETHANE", "G4_ETHYL_ALCOHOL", "G4_ETHYL_CELLULOSE", "G4_ETHYLENE",
        "G4_EYE_LENS_ICRP", "G4_FERRIC_OXIDE", "G4_FERROBORIDE", "G4_FERROUS_OXIDE",
        "G4_FERROUS_SULFATE", "G4_FREON-12", "G4_FREON-12B2", "G4_FREON-13",
        "G4_FREON-13B1", "G4_FREON-13I1", "G4_GADOLINIUM_OXYSULFIDE", "G4_GALLIUM_ARSENIDE",
        "G4_GEL_PHOTO_EMULSION", "G4_Pyrex_Glass", "G4_GLASS_LEAD", "G4_GLASS_PLATE",
        "G4_GLUTAMINE", "G4_GLYCEROL", "G4_GUANINE", "G4_GYPSUM",
        "G4_N-HEPTANE", "G4_N-HEXANE", "G4_KAPTON", "G4_LANTHANUM_OXYBROMIDE",
        "G4_LANTHANUM_OXYSULFIDE", "G4_LEAD_OXIDE", "G4_LITHIUM_AMIDE", "G4_LITHIUM_CARBONATE",
        "G4_LITHIUM_FLUORIDE", "G4_LITHIUM_HYDRIDE", "G4_LITHIUM_IODIDE", "G4_LITHIUM_OXIDE",
        "G4_LITHIUM_TETRABORATE", "G4_LUNG_ICRP", "G4_M3_WAX", "G4_MAGNESIUM_CARBONATE",
        "G4_MAGNESIUM_FLUORIDE", "G4_MAGNESIUM_OXIDE", "G4_MAGNESIUM_TETRABORATE", "G4_MERCURIC_IODIDE",
        "G4_METHANE", "G4_METHANOL", "G4_MIX_D_WAX", "G4_MS20_TISSUE",
        "G4_MUSCLE_SKELETAL_ICRP", "G4_MUSCLE_STRIATED_ICRU", "G4_MUSCLE_WITH_SUCROSE", "G4_MUSCLE_WITHOUT_SUCROSE",
        "G4_NAPHTHALENE", "G4_NITROBENZENE", "G4_NITROUS_OXIDE", "G4_NYLON-8062",
        "G4_NYLON-6-6", "G4_NYLON-6-10", "G4_NYLON-11_RILSAN", "G4_OCTANE",
        "G4_PARAFFIN", "G4_N-PENTANE", "G4_PHOTO_EMULSION", "G4_PLASTIC_SC_VINYLTOLUENE",
        "G4_PLUTONIUM_DIOXIDE", "G4_POLYACRYLONITRILE", "G4_POLYCARBONATE", "G4_POLYCHLOROSTYRENE",
        "G4_POLYETHYLENE", "G4_MYLAR", "G4_PLEXIGLASS", "G4_POLYOXYMETHYLENE",
        "G4_POLYPROPYLENE", "G4_POLYSTYRENE", "G4_TEFLON", "G4_POLYTRIFLUOROCHLOROETHYLENE",
        "G4_POLYVINYL_ACETATE", "G4_POLYVINYL_ALCOHOL", "G4_POLYVINYL_BUTYRAL", "G4_POLYVINYL_CHLORIDE",
        "G4_POLYVINYLIDENE_CHLORIDE", "G4_POLYVINYLIDENE_FLUORIDE", "G4_POLYVINYL_PYRROLIDONE", "G4_POTASSIUM_IODIDE",
        "G4_POTASSIUM_OXIDE", "G4_PROPANE", "G4_lPROPANE", "G4_N-PROPYL_ALCOHOL",
        "G4_PYRIDINE", "G4_RUBBER_BUTYL", "G4_RUBBER_NATURAL", "G4_RUBBER_NEOPRENE",
        "G4_SILICON_DIOXIDE", "G4_SILVER_BROMIDE", "G4_SILVER_CHLORIDE", "G4_SILVER_HALIDES",
        "G4_SILVER_IODIDE", "G4_SKIN_ICRP", "G4_SODIUM_CARBONATE", "G4_SODIUM_IODIDE",
        "G4_SODIUM_MONOXIDE", "G4_SODIUM_NITRATE", "G4_STILBENE", "G4_SUCROSE",
        "G4_TERPHENYL", "G4_TESTIS_ICRP", "G4_TETRACHLOROETHYLENE", "G4_THALLIUM_CHLORIDE",
        "G4_TISSUE_SOFT_ICRP", "G4_TISSUE_SOFT_ICRU-4", "G4_TISSUE-METHANE", "G4_TISSUE-PROPANE",
        "G4_TITANIUM_DIOXIDE", "G4_TOLUENE", "G4_TRICHLOROETHYLENE", "G4_TRIETHYL_PHOSPHATE",
        "G4_TUNGSTEN_HEXAFLUORIDE", "G4_URANIUM_DICARBIDE", "G4_URANIUM_MONOCARBIDE", "G4_URANIUM_OXIDE",
        "G4_UREA", "G4_VALINE", "G4_VITON", "G4_WATER_VAPOR",
        "G4_XYLENE", "G4_GRAPHITE", "G4_WATER", "G4_lH2",
        "G4_lN2", "G4_lO2", "G4_lAr", "G4_lBr",
        "G4_lKr", "G4_lXe", "G4_PbWO4", "G4_Galactic",
        "G4_GRAPHITE_POROUS", "G4_LUCITE", "G4_BRASS", "G4_BRONZE",
        "G4_STAINLESS-STEEL", "G4_CR39", "G4_OCTADECANOL", "G4_KEVLAR",
        "G4_DACRON", "G4_NEOPRENE", "G4_CYTOSINE", "G4_THYMINE",
        "G4_URACIL", "G4_DEOXYRIBOSE", "G4_DNA_DEOXYRIBOSE", "G4_DNA_PHOSPHATE",
        "G4_DNA_ADENINE", "G4_DNA_GUANINE", "G4_DNA_CYTOSINE", "G4_DNA_THYMINE",
        "G4_DNA_URACIL"
    ]

    return nist_compount_list

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
