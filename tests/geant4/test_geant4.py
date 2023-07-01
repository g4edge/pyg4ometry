import numpy as _np
import pytest as _pytest

import pyg4ometry.transformation as _trans
from pyg4ometry.geant4.solid import TwoVector

# #############################
# solid two vector
# #############################
def test_Python_TwoVector_T001Constructor():
    v = TwoVector(1,2)

def test_Python_TwoVector_T002Repr():
    v = TwoVector(1,2)
    s = str(v)

def test_Python_TwoVector_T003GetItem():
    v = TwoVector(1,2)
    assert v[0] ==1
    assert v[1]  == 2
    try :
        print(v[2])
    except IndexError :
        pass

def test_Python_TwoVector_T004Add():
    v1 = TwoVector(1,2)
    v2 = TwoVector(3,4)

    i = 5
    f = 6.0
    s = "r"

    assert (v1+v2)[0] == 4
    assert (v1+v2)[1] == 6

    assert (v1+i)[0] == 6
    assert (v1+i)[1] == 7

    assert (v1+f)[0] == 7.0
    assert (v1+f)[1] == 8.0

    try :
        v1+s
    except ValueError :
        pass

def test_Python_TwoVector_T005Sub():
    v1 = TwoVector(1,2)
    v2 = TwoVector(3,4)

    i = 5
    f = 6.0
    s = "r"

    assert (v1-v2)[0] == -2
    assert (v1-v2)[1] == -2

    assert (v1-i)[0] == -4
    assert (v1-i)[1] == -3

    assert (v1-f)[0] == -5.0
    assert (v1-f)[1] == -4.0

    try :
        v1-s
    except ValueError :
        pass


def test_Python_TwoVector_T006Mul():
    v1 = TwoVector(1,2)

    f = 5
    s = "r"

    assert (v1*f)[0] == 5
    assert (v1*f)[1] == 10

    try :
        vv = v1*s
    except ValueError :
        pass

# #############################
# Transformation
# #############################
def test_Python_Rad2Deg() :
    assert _trans.rad2deg(_np.pi) == 180

def test_Python_Deg2Rad() :
    assert _trans.deg2rad(180) == _np.pi

def test_Python_Tbxyz2axisangleX() :
    assert _trans.tbxyz2axisangle([_np.pi/2.0,0.0,0.0]) == [[1.0, 0.0, 0.0], 1.5707963267948966]

def test_Python_Tbxyz2axisangleY() :
    assert _trans.tbxyz2axisangle([0.0,_np.pi/2.0,0.0]) == [[0.0, 1.0, 0.0], 1.5707963267948966]

def test_Python_Tbxyz2axisangleZ() :
    assert _trans.tbxyz2axisangle([0.0,0.0,_np.pi/2.0]) == [[0.0, 0.0, 1.0], 1.5707963267948966]

def test_Python_Matrix2axisangleX() :
    theta = 0.5
    m = _np.array([[             1,              0,              0],
                   [             0, _np.cos(theta),-_np.sin(theta)],
                   [             0, _np.sin(theta), _np.cos(theta)]])
    aa = _trans.matrix2axisangle(m)
    assert _pytest.approx(aa[0]) == [1.0,0.0,0.0]
    assert _pytest.approx(aa[1]) == 0.5

def test_Python_Matrix2axisangleY() :
    theta = 0.5
    m = _np.array([[_np.cos(theta),              0,-_np.sin(theta)],
                   [             0,              1,              0],
                   [_np.sin(theta),              0, _np.cos(theta)]])
    aa = _trans.matrix2axisangle(m)
    assert _pytest.approx(aa[0]) == [0.0, -1.0,0.0]
    assert _pytest.approx(aa[1]) == 0.5

def test_Python_Matrix2axisangleZ() :
    theta = 0.5
    m = _np.array([[_np.cos(theta), -_np.sin(theta),0],
                   [_np.sin(theta), _np.cos(theta) , 0],
                   [             0,               0, 1]])
    aa = _trans.matrix2axisangle(m)
    assert _pytest.approx(aa[0]) == [0.0, 0.0, 1.0]
    assert _pytest.approx(aa[1]) == 0.5

def test_Python_Axisangle2matrixX() :
    print(_trans.axisangle2matrix([1.0,0,0],_np.pi/2.0))

def test_Python_Axisangle2matrixY() :
    print(_trans.axisangle2matrix([0,1,0],_np.pi/2.0))

def test_Python_Axisangle2matrixZ():
    print(_trans.axisangle2matrix([0, 0, 1], _np.pi / 2.0))

def test_Python_Matrix2tbxyz() :
    pass

def test_Python_Tbxyz2matrix() :
    pass

def test_Python_Matrix_MatrixFromTo() :
    print(_trans.matrix_from([0,0,1],[0,1,0]))

# #############################
# Freecad
# #############################
def test_Python_FreeCadImportFail() :
    import sys
    # remove freecad
    for p in sys.path :
        if p.find("freecad") != -1 :
            sys.path.remove(p)

    import pyg4ometry.freecad

# #############################
# Mesh
# #############################


# #############################
# CSG
# #############################

def test_Python_GetLocalMesh():
    import pyg4ometry

    reg = pyg4ometry.geant4.Registry()
    s1 = pyg4ometry.geant4.solid.Box("s1", 10, 10, 10, reg, "mm")
    l1 = pyg4ometry.geant4.LogicalVolume(s1, "G4_Galactic", "l1", reg)
    l1.mesh.getLocalMesh()

def test_Python_Remesh():
    import pyg4ometry

    reg = pyg4ometry.geant4.Registry()
    s1 = pyg4ometry.geant4.solid.Box("s1", 10, 10, 10, reg, "mm")
    l1 = pyg4ometry.geant4.LogicalVolume(s1, "G4_Galactic", "l1", reg)
    l1.mesh.remesh()

def test_Python_ExceptionNullMeshErrorIntersection() :
    import pyg4ometry

    try :
        reg = pyg4ometry.geant4.Registry()
        s1   = pyg4ometry.geant4.solid.Box("s1",10,10,10, reg, "mm")
        s2   = pyg4ometry.geant4.solid.Box("s2",10,10,10, reg, "mm")

        inter = pyg4ometry.geant4.solid.Intersection("inter",s1,s2,[[0,0,0],[0,0,0]],reg)
        raise pyg4ometry.exceptions.NullMeshError(inter)
    except pyg4ometry.exceptions.NullMeshError :
        pass

def test_Python_ExceptionNullMeshErrorSubtraction() :
    import pyg4ometry

    try :
        reg = pyg4ometry.geant4.Registry()
        s1   = pyg4ometry.geant4.solid.Box("s1",10,10,10, reg, "mm")
        s2   = pyg4ometry.geant4.solid.Box("s2",10,10,10, reg, "mm")

        subtra = pyg4ometry.geant4.solid.Subtraction("subtra",s1,s2,[[0,0,0],[0,0,0]],reg)
        raise pyg4ometry.exceptions.NullMeshError(subtra)
    except pyg4ometry.exceptions.NullMeshError :
        pass

def test_Python_ExceptionNullMeshErrorOtherSolid() :
    import pyg4ometry

    try :
        reg = pyg4ometry.geant4.Registry()
        s1   = pyg4ometry.geant4.solid.Box("s1",10,10,10, reg, "mm")
        raise pyg4ometry.exceptions.NullMeshError(s1)
    except pyg4ometry.exceptions.NullMeshError :
        pass

def test_Python_ExceptionNullMeshErrorBasestring() :
    import pyg4ometry

    try :
        raise pyg4ometry.exceptions.NullMeshError("s1")
    except pyg4ometry.exceptions.NullMeshError :
        pass

def test_Python_ExceptionIdenticalNameError() :
    import pyg4ometry

    try :
        raise pyg4ometry.exceptions.IdenticalNameError("solid_name")
    except pyg4ometry.exceptions.IdenticalNameError :
        pass

    try :
        raise pyg4ometry.exceptions.IdenticalNameError("solid_name","solid")
    except pyg4ometry.exceptions.IdenticalNameError :
        pass

##############################
# VtkVisualisation
##############################

def test_Python_VisualisationVtk_setOpacity():
    from pyg4ometry.commontest import BoxTest

    r = BoxTest(False,False)
    v  = r['vtkViewer']
    if v is not None :
        v.setOpacity(0, 0)
        v.setOpacity(0.5,-1)

def test_Python_VisualisationVtk_setWireframe():
    from pyg4ometry.commontest import BoxTest

    r = BoxTest(False,False)
    v  = r['vtkViewer']
    if v is not None :
        v.setWireframe()

def test_Python_VisualisationVtk_setSurface():
    from pyg4ometry.commontest import BoxTest

    r = BoxTest(False,False)
    v  = r['vtkViewer']
    if v is not None :
        v.setSurface()

def test_Python_VisualisationVtk_setWireframe_VisualisationOptions():
    from pyg4ometry.commontest import BoxTest
    import pyg4ometry.visualisation.VtkViewer

    r = BoxTest(False,False)
    lv = r['logicalVolume']
    dv = lv.daughterVolumes[0]
    dv.visOptions.representation = "wireframe"

    v = pyg4ometry.visualisation.VtkViewer()
    v.addLogicalVolume(lv)
    #v.view(interactive=False)

def test_Python_VisualisationVtk_setOpacityOverlap():
    from pyg4ometry.commontest import OverlapCoplTest

    r = OverlapCoplTest(False,False)
    v  = r['vtkViewer']
    if v is not None :
        v.setOpacityOverlap(0)

def test_Python_VisualisationVtk_setWireframeOverlap():
    from pyg4ometry.commontest import OverlapCoplTest

    r = OverlapCoplTest(False,False)
    v  = r['vtkViewer']
    if v is not None :
        v.setWireframeOverlap()

def test_Python_VisualisationVtk_setSurfaceOverlap():
    from pyg4ometry.commontest.OverlapCopl import OverlapCoplTest

    r = OverlapCoplTest(False,False)
    v  = r['vtkViewer']
    if v is not None :
        v.setSurfaceOverlap()

def test_Python_VisualisationVtk_setRandomColours():
    from pyg4ometry.commontest.OverlapCopl import OverlapCoplTest

    r = OverlapCoplTest(False,False)
    v  = r['vtkViewer' ]
    if v is not None :
        v.setRandomColours()

def test_Python_VisualisationVtk_RandomColour():
    from pyg4ometry.commontest import LhcBlmModel as lhc_blm_model
    import pyg4ometry

    wlv = lhc_blm_model.make_lhc_blm()
    v = pyg4ometry.visualisation.VtkViewerColoured(defaultColour="random")
    v.addLogicalVolume(wlv)

def test_Python_VisualisationVtk_DefaultMaterial():
    from pyg4ometry.commontest import LhcBlmModel as lhc_blm_model
    import pyg4ometry
    wlv = lhc_blm_model.make_lhc_blm()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(wlv)

def test_Python_VisualisationVtk_CustomMaterialColours():
    from pyg4ometry.commontest import LhcBlmModel as lhc_blm_model
    import pyg4ometry
    wlv = lhc_blm_model.make_lhc_blm()
    colours = lhc_blm_model.materialToColour
    v = pyg4ometry.visualisation.VtkViewerColoured(materialVisOptions=colours)
    v.addLogicalVolume(wlv)

