import pyg4ometry as _pyg4
import pyg4ometry.pyoce as _oce

def oce2Geant4_traverse(xcaf,label,greg) :
    name = _oce.find_TDataStd_Name_From_Label(label)
    loc  = _oce.find_XCAFDoc_Location_From_Label(label)

    print(name)
    if loc is not None :
        loc.Get().ShallowDump()

    for i in range(1, label.NbChildren() + 1, 1):
        b, child = label.FindChild(i, False)
        oce2Geant4_traverse(xcaf,child,greg)

    rlabel = _oce.TDF_Label()
    xcaf.shapeTool().GetReferredShape(label, rlabel)
    if not rlabel.IsNull():
        oce2Geant4_traverse(xcaf,rlabel,greg)

def oce2Geant4(xcaf, shapeName) :
    greg = _pyg4.geant4.Registry()

    label = _oce.findOCCShapeByName(xcaf.shapeTool(), shapeName)
    if label is None :
        print("Cannot find shape, exiting")
        return

    # find name of shape
    name = _oce.find_TDataStd_Name_From_Label(label)

    # traverse cad and make geant4 geometry
    oce2Geant4_traverse(xcaf, label, greg)


