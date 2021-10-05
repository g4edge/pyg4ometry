from collections import defaultdict as _defaultdict
from copy import deepcopy as _deepcopy
import enum as _enum

from pyg4ometry.geant4 import Material as _Material
from pyg4ometry.geant4 import Element as _Element

class Tests:
    """
    Set of options of which tests to perform and potentially with what tolerance.
    """
    def __init__(self):
        self.names             = True
        self.nDaughters        = True
        self.solidExact        = True
        self.shapeExtent       = True
        self.shapeVolume       = True
        self.placement         = True # i.e. position and rotation
        self.materialClassType = True
        self.materialCompositionType = True # i.e. natoms or mass fraction

        self.toleranceSolidParameterFraction  = 1e-3
        self.toleranceSolidExtentFraction     = 1e-6
        self.toleranceVolumeFraction          = 1e-2
        self.toleranceTranslationFraction     = 1e-6
        self.toleranceScaleFraction           = 1e-3
        self.toleranceRotationFraction        = 1e-6
        self.toleranceMaterialDensityFraction = 1e-4
        self.toleranceMaterialMassFraction    = 1e-4

class TestResult(_enum.Enum):
    """
    A test result can be either pass, fail or not conducted.
    
    Use 0,1 so we can also emplicitly construct this with a Boolean.

    Use the bitwise or operator | and not the keyword 'or'. This bitwise or
    operator returns Failed if either have failed. Only returns
    NotTested if both are not tested. Cannot use bitwise |= as we cannot
    update an Enum internally.
    """
    Failed    = 0
    Passed    = 1
    NotTested = 2

    def __or__(self, other):
        if self == TestResult.NotTested and other == TestResult.NotTested:
            return TestResult.NotTested
        # bool(2) = True here
        return TestResult(bool(self.value) and bool(other.value))

    def __ior__(self, other):
        raise IOError("not implement")

class TestResultNamed:
    def __init__(self, nameIn, testResultIn=TestResult.Failed, detailsIn=""):
        self.testResult = testResultIn
        self.name = nameIn
        self.details = detailsIn

    def __str__(self):
        return ": ".join([self.name, str(self.testResult), self.details])

class ComparisonResult:
    """
    Holder for a test result. Roughly a dict[testname] = list(TestResultNamed)

    Use + and += to append to this object. Uses a default dictionary so no
    need to initialise any key names. Should always append a list even if only
    1 item.

    >>> cr = ComparisonResult()
    >>> cr['nDaughtersTest'] += [TestResultNamed('volume_1', TestResult.Failed, 'different number')]
    >>> cr.Print()
    """
    def __init__(self):
        self.test = _defaultdict(list)
        self.result = TestResult.NotTested
        
    def __getitem__(self,key):
        return self.test[key]

    def __setitem__(self,key,value):
        self.test[key] = value
        for testResNamed in value:
            self.result = self.result | testResNamed.testResult  # or equals operator

    def __add__(self, other):
        result = _deepcopy(self)
        for testName,results in other.test:
            result.test[testName].extend(results)
            for v in results:
                result.result = result.result | v.testResult
        return result

    def __iadd__(self, other):
        self.result = self.result | other.result # this should already be a product of all subtests
        for testName, results in other.test.items():
            self.test[testName].extend(results)
        return self

    def __len__(self):
        return len(self.test)

    def Print(self, testName=None):
        print("Overal result> ",self.result)
        if testName is None:
            for tn,results in self.test.items():
                print('Test> ',tn)
                for result in results:
                    print(result)
        else:
            print('Test> ',testName)
            for result in self.test[testName]:
                print(result)
        print(" ") # for a new line
                    

def Geometry(referenceLV, otherLV, tests=Tests(), includeAllTestResults=True):
    result = LogicalVolumes(referenceLV, otherLV, tests, True, includeAllTestResults)
    return result                   

def LogicalVolumes(referenceLV, otherLV, tests, recursive=False, includeAllTestResults=False):
    result = ComparisonResult()

    rlv = referenceLV  # shortcuts
    olv = otherLV

    if tests.names:
        result += _Names("logicalVolumeName", rlv.name, olv.name, rlv.name, includeAllTestResults)
    result += Solids(rlv.solid, olv.solid, tests, rlv.name, includeAllTestResults)
    result += Materials(rlv.material, olv.material, tests, rlv.name, includeAllTestResults)

    if len(olv.daughterVolumes) != len(rlv.daughterVolumes):
        details =  "# daughters: ('"+rlv.name+"') : "+str(len(rlv.daughterVolumes))
        details += ", ('"+olv.name+"') : "+str(len(olv.daughterVolumes))
        result['nDaughters'] += [TestResultNamed(rlv.name, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['nDaughters'] += [TestResultNamed(rlv.name, TestResult.Passed)]

    result += _Meshes(rlv.name, rlv.mesh, olv.mesh, tests)

    # if not recursive return now and don't loop over daughter physical volumes
    if not recursive:
        return result
    
    # shortcuts
    r = recursive
    iatr = includeAllTestResults

    # iterate over daughters
    for dName,rDaughter in rlv._daughterVolumesDict.items():
        if dName in olv._daughterVolumesDict:
            oDaughter = olv._daughterVolumesDict[dName]

            # check types
            expectedType = rDaughter.type
            if expectedType != oDaughter.type:
                details =  "daughter types in '"+dName+"': (ref): "+str(expectedType)
                details += ", (other): "+str(oDaughter.type)
                result['daughterType'] += [TestResultNamed(rlv.name, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['daughterType'] += [TestResultNamed(rlv.name, TestResult.Passed)]

            # do custom type check
            if expectedType == "placement":
                result += PhysicalVolumes(rDaughter, oDaughter, tests, r, rlv.name, iatr)
            elif expectedType == "assembly":
                result += AssemblyVolumes(rDaughter, oDaughter, tests, r, iatr)
            elif expectedType == "replica":
                result += ReplicaVolumes(rDaughter, oDaughter, tests, iatr)
            elif expectedType == "division":
                result += DivisionVolumes(rDaughter, oDaughter, tests, iatr)
            elif expectedType == "parameterised":
                result += ParameterisedVolumes(rDaughter, oDaughter, tests, iatr)
            else:
                # LN: don't know what to SkinSurface, BorderSurface and Loop
                pass
        
        else:
            # missing daughter in other lv
            details = "dName found in lv: '"+rlv.name+"' but not in '"+olv.name+"'"
            result['missingDaughter'] += [TestResultNamed(dName, TestResult.Failed, details)]
    
    # test if more daughters in other                                       
    if len(olv.daughterVolumes) > len(rlv.daughterVolumes):
        rSet = set([d.name for d in rlv.daughterVolumes])
        oSet = set([d.name for d in olv.daughterVolumes])
        extraNames = oSet - rSet # ones in oSet but not in rSet
        # extra daughters in other lv                                   
        details = "extra daughter"
        if len(extraNames) > 1:
            details += "s "
        details += "[" + ", ".join(extraNames) + "]"
        result['extraDaughter'] += [TestResultNamed(rlv.name, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['extraDaughter'] += [TestResultNamed(rlv.name, TestResult.Passed)]

    return result

def PhysicalVolumes(referencePV, otherPV, tests, recursive=False, lvName="", includeAllTestResults=False):
    """
    lvName is an optional parent object name to help in print out details decode where the placement is.
    """
    result = ComparisonResult()

    rpv = referencePV # shortcuts
    opv = otherPV

    if tests.names:
        result += _Names("placementName", rpv.name, opv.name, lvName, includeAllTestResults)
    if tests.placement:
        result += _Vector("rotation", rpv.rotation, opv.rotation, tests, includeAllTestResults)
        result += _Vector("position", rpv.position, opv.position, tests, includeAllTestResults)
    result += _Vector("scale", rpv.scale, opv.scale, tests, includeAllTestResults)
    result += _CopyNumber(rpv.name, rpv.copyNumber, opv.copyNumber, tests, includeAllTestResults)
    result += LogicalVolumes(rpv.logicalVolume, opv.logicalVolume, tests, recursive, includeAllTestResults)
    return result

def AssemblyVolumes(referenceAV, otherAV, tests, recursive=False, includeAllTestResults=False):
    result = ComparisonResult()

    rav = referenceAV
    oav = otherAV

    if tests.names:
        result += _Names("assemblyName", rav.name, oav.name, rav.name, includeAllTestResults)

    # compare placements inside assembly

    # compare meshes as we would do for a logical?

    result.result = result.result | TestResult.Passed
    return result

def ReplicaVolumes(referenceRV, otherRV, tests, includeAllTestResults=False):
    result = ComparisonResult()
    return result

def DivisionVolumes(referenceRV, otherRV, tests, includeAllTestResults=False):
    result = ComparisonResult()
    return result

def ParameterisedVolumes(referenceRV, otherRV, tests, includeAllTestResults=False):
    result = ComparisonResult()
    return result

def Materials(referenceMaterial, otherMaterial, tests, lvName="", includeAllTestResults=False):
    """
    This tests assumes both referenceMaterial and otherMaterial are derived from the 
    type pyg4ometry.geant4._Material.Material.

    Compares, name, classname, density, n components
    """
    result = ComparisonResult()

    rm = referenceMaterial
    om = otherMaterial

    testName = ": ".join(list(filter(None, [lvName, rm.name])))

    if tests.names:
        result += _Names("materialName", rm.name, om.name, lvName, includeAllTestResults)

    if tests.materialClassType:
        if type(om) != type(rm):
            details = "material type: (reference): "+str(type(rm))+", (other): "+str(type(om))
            result['materialType'] += [TestResultNamed(testName, TestResult.Failed, details)]
        elif includeAllTestResults:
            result['materialType'] += [TestResultNamed(testName, TestResult.Passed)]

    if rm.type == "nist" or om.type == "nist":
        if includeAllTestResults:
            result['materialDensity'] += [TestResultNamed(testName, TestResult.NotTested)]
            result['materialNComponents'] += [TestResultNamed(testName, TestResult.NotTested)]
            result['materialComponentType'] += [TestResultNamed(testName, TestResult.NotTested)]
            result['materialComponentMassFraction'] += [TestResultNamed(testName, TestResult.NotTested)]
        result.result = result.result | TestResult.Passed
        return result

    # density
    dDensity = om.density - rm.density
    if dDensity != 0: # avoid zero division
        if (dDensity / rm.density) > tests.toleranceMaterialDensityFraction:
            details = "density: (reference): "+str(rm.density)+", (other): "+str(om.density)
            result['materialDensity'] += [TestResultNamed(testName, TestResult.Failed, details)]
        elif includeAllTestResults:
            result['materialDensity'] += [TestResultNamed(testName, TestResult.Passed)]
            
    # n components of material
    if om.number_of_components != rm.number_of_components:
        details = "# components: (reference): "+str(rm.number_of_components)
        details += ", (other): "+str(om.number_of_components)
        result['materialNComponents'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['materialNComponents'] += [TestResultNamed(testName, TestResult.Passed)]
            
    # components and fractions
    if om.number_of_components == rm.number_of_components:
        for i in range(rm.number_of_components):
            rc, oc = rm.components[i], om.components[i]
            # we expect these each to be a tuple of (object, number, "type of fraction"

            # we don't test component names as this doesn't matter if they're functionally
            # the same as judged by other parameters.

            # component type
            rComponentType, oComponentType = rc[2], oc[2]
            if rComponentType != oComponentType:
                if tests.materialCompositionType:
                    details =  "material component type: (reference): "+str(rComponentType)
                    details += ", (other): "+str(oComponentType)
                    result['materialComponentType'] += [TestResultNamed(testName, TestResult.Failed, details)]
                break # we can't possibly make a more detailed comparison now
            elif includeAllTestResults:
                result['materialComponentType'] += [TestResultNamed(testName, TestResult.Passed)]
                
            # component fraction
            rFrac, oFrac = rc[1], oc[1]
            if rComponentType == "natoms":
                # integer comparison
                if rFrac != oFrac:
                    details =  "natoms: component (i): "+str(i)+", named: "+str(rc[0].name)
                    details += ": (reference): "+str(rFrac)+", (other): "+str(oFrac)
                    result['materialComponentNAtoms'] += [TestResultNamed(testName, TestResult.Failed, details)]
                elif includeAllTestResults:
                    result['materialComponentNAtoms'] += [TestResultNamed(testName, TestResult.Passed)]
            else:
                # fractional float comparison
                dFrac = oFrac - rFrac
                if dFrac != 0: # avoid zero division
                    if (dFrac / rFrac) > tests.toleranceMaterialMassFraction:
                        details =  "mass fraction: component (i): "+str(i)+", named: "+str(rc[0].name)
                        details += ": (reference): "+str(rFrac)+", (other): "+str(oFrac)
                        result['materialComponentMassFraction'] += [TestResultNamed(testName, TestResult.Failed, details)]
                elif includeAllTestResults:
                    result['materialComponentMassFraction'] += [TestResultNamed(testName, TestResult.Passed)]

            # components themselves
            if type(rc[0]) is _Material:
                result += Materials(rc[0], oc[0], tests, lvName, includeAllTestResults)
            elif type(rc[0]) is _Element:
                result += _Elements(rc[0], oc[0], tests, lvName, includeAllTestResults)
            else:
                print(type(rc))

    result.result = result.result | TestResult.Passed
    return result

def _Elements(referenceElement, otherElement, tests, lvName="", includeAllTestResults=False):
    result = ComparisonResult()

    re = referenceElement
    oe = otherElement

    testName = ": ".join(list(filter(None, [lvName, re.name])))
    
    if tests.names:
        result += _Names("elementName", re.name, oe.name, lvName, includeAllTestResults)

    if re.type != oe.type:
        details = "element type: (reference): "+str(re.type)+", (other): "+str(oe.type)
        result['elementType'] += [TestResultNamed(testName, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['elementType'] += [TestResultNamed(testName, TestResult.Passed)]

    if re.type == oe.type:
        # can only do comparison if they're the same type
        if re.type == "simple":
            # compare A
            if re.A != re.A:
                details = "element A: (reference): "+str(re.A)+", (other): "+str(oe.A)
                result['elementA'] += [TestResultNamed(testName, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['elementA'] += [TestResultNamed(testName, TestResult.Passed)]
            # compare Z
            if re.Z != re.Z:
                details = "element Z: (reference): "+str(re.Z)+", (other): "+str(oe.Z)
                result['elementZ'] += [TestResultNamed(testName, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['elementZ'] += [TestResultNamed(testName, TestResult.Passed)]

        elif re.type == "composite":
            if re.n_comp != re.n_comp:
                details = "element n_comp: (reference): "+str(re.n_comp)+", (other): "+str(oe.n_comp)
                result['elementNComp'] += [TestResultNamed(testName, TestResult.Failed, details)]
            elif includeAllTestResults:
                result['elementNComp'] += [TestResultNamed(testName, TestResult.Passed)]

        else:
            pass
    result.result = result.result | TestResult.Passed
    return result

def Solids(referenceSolid, otherSolid, tests, lvName="", includeAllTestResults=False):
    """
    """
    result = ComparisonResult()

    rs = referenceSolid
    os = otherSolid

    testName = ": ".join(list(filter(None, [lvName, rs.name])))
    
    if tests.names:
        result += _Names("solidName", rs.name, os.name, lvName, includeAllTestResults)
        
    if tests.solidExact:
        # solid type
        if rs.type != os.type:
            details = "solid type: (reference): "+str(rs.type)
            result['solidExactType'] += [TestResultNamed(testName, TestResult.Failed, details)]
        elif includeAllTestResults:
            result['solidExactType'] += [TestResultNamed(testName, TestResult.Passed)]

        if rs.type == os.type:
            # can only compare variables if they're the same type
            for var in rs.varNames:
                rv, ov = float(getattr(rs,var)), float(getattr(os,var))
                dv = ov - rv
                if dv != 0:
                    if (dv / rv) > tests.toleranceSolidParameterFraction:
                        details = "solid parameter '"+var+"': (reference): "+str(rv)+", (other): "+str(ov)
                        result['solidExactParameter'] += [TestResultNamed(testName, TestResult.Failed, details)]
                    elif includeAllTestResults:
                        result['solidExactParameter'] += [TestResultNamed(testName, TestResult.Passed)]
    
    return result

def _Names(testName, str1, str2, parentName="", includeAllTestResults=False):
    result = ComparisonResult()

    nameTest = str1 == str2
    if not nameTest:
        details = "'"+str1+"' != '"+str2+"'"
        result[testName] = [TestResultNamed("_".join(list(filter(None, [parentName, str1]))), TestResult.Failed, details)]
    elif includeAllTestResults:
        result[testName] = [TestResultNamed("_".join(list(filter(None, [parentName, str1]))), TestResult.Passed)]

    result.result = result.result | TestResult.Passed
    return result

def _Vector(vectortype, r1, r2, tests, includeAllTestResults=False):
    result = ComparisonResult()

    tols = {'rotation' : tests.toleranceRotationFraction,
            'position' : tests.toleranceTranslationFraction,
            'scale'    : tests.toleranceScaleFraction}
    tolerance = tols[vectortype]
    
    for v in ['x','y','z']:
        rc, oc = float(getattr(r1,v)),float(getattr(r2,v))
        drc = oc - rc
        if drc != 0:
            if (drc / rc) > tolerance:
                details = v+": (reference): "+str(rc)+", (other): "+str(oc)
                result[vectortype] += [TestResultNamed(r1.name, TestResult.Failed, details)]
            elif includeAllTestResults:
                result[vectortype] += [TestResultNamed(r1.name, TestResult.Passed)]
    
    return result

def _CopyNumber(pvname, c1, c2, tests, includeAllTestResults=False):
    result = ComparisonResult()

    if c1 != c2:
        details = "copy number: (reference): "+str(c1)+", (other): "+str(c2)
        result['copyNumber'] += [TestResultNamed(pvname, TestResult.Failed, details)]
    elif includeAllTestResults:
        result['copyNumber'] += [TestResultNamed(pvname, TestResult.Passed)]
    
    return result

def _Meshes(lvname, referenceMesh, otherMesh, tests):
    result = ComparisonResult()

    rm = referenceMesh
    om = otherMesh
    
    if tests.shapeExtent:
        if rm and om:
            # can only compare if meshes exist
            [rmMin, rmMax] = rm.getBoundingBox()
            [omMin, omMax] = om.getBoundingBox()
            for i in range(3):
                dMin = omMin[i] - rmMin[i]
                if dMin != 0:
                    if (dMin / rmMin[i]) > tests.toleranceSolidExtentFraction:
                        details =  "axis-aligned bounding box lower edge: component i: "+str(i)
                        details += ", (reference): "+str(omMin[i])+", (other): "+str(omMin[i])
                        result['shapeExtentBoundingBoxMin'] += [TestResultNamed(lvname, TestResult.Failed, details)]
                dMax = omMax[i] - rmMax[i]
                if dMax != 0:
                    if (dMax / rmMax[i]) > tests.toleranceSolidExtentFraction:
                        details =  "axis-aligned bounding box upper edge: component i: "+str(i)
                        details += ", (reference): "+str(omMax[i])+", (other): "+str(omMax[i])
                        result['shapeExtentBoundingBoxMax'] += [TestResultNamed(lvname, TestResult.Failed, details)]
            # no include all tests here as just too many
        else:
            # explicitly flag as we were meant to test but can't
            result['shapeExtent'] += [TestResultNamed(lvname, TestResult.NotTested, "no meshes")]

    if tests.shapeVolume:
        if rm and om:
            # can only compare if meshes exist
            # TODO can't see any method on meshes to calculate this
            pass
        else:
            # explicitly flag as we were meant to test but can't
            result['shapeVolume'] += [TestResultNamed(lvname, TestResult.NotTested, "no meshes")]

    return result

def Registries(reference, other):
    pass
