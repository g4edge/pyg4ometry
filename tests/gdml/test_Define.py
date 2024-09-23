import pyg4ometry


# #############################
# Define upgrades
# #############################
def test_GdmlDefine_UpgradeToStringExpression():
    r = pyg4ometry.geant4.Registry()

    # number to expression string
    assert pyg4ometry.gdml.upgradeToStringExpression(r, 10) == "10.000000000000000"

    # string to expression string (evaluatable)
    assert pyg4ometry.gdml.upgradeToStringExpression(r, "10+10") == "10+10"

    # string to expression string (unevaluatable)

    x = pyg4ometry.gdml.Constant("x", 1, r)

    try:
        assert pyg4ometry.gdml.upgradeToStringExpression(r, "10*x+10") == "10*x+10"
    except AttributeError:
        pass

    # string but in define dict
    c = pyg4ometry.gdml.Defines.Constant("c", "10", r, True)
    assert pyg4ometry.gdml.upgradeToStringExpression(r, "c") == "c"

    # expression that cannot be evaluated
    try:
        pyg4ometry.gdml.upgradeToStringExpression(r, "z")
    except Exception:
        pass


def test_GdmlDefine_UpgradeToVector():
    r = pyg4ometry.geant4.Registry()

    v = pyg4ometry.gdml.Defines.Position("v", 0, 0, 0, "mm", r, False)

    # vector
    p = pyg4ometry.gdml.Defines.upgradeToVector(v, r, "position", unit="", addRegistry=False)
    assert p.eval() == [0, 0, 0]

    # list to position
    p = pyg4ometry.gdml.Defines.upgradeToVector([0, 0, 0], r, "position", addRegistry=False)
    assert p.eval() == [0, 0, 0]

    # list to rotation
    p = pyg4ometry.gdml.Defines.upgradeToVector([0, 0, 0], r, "rotation", addRegistry=False)
    assert p.eval() == [0, 0, 0]

    # list to scale
    p = pyg4ometry.gdml.Defines.upgradeToVector([0, 0, 0], r, "scale", addRegistry=False)
    assert p.eval() == [0, 0, 0]

    # list to undefined
    p = pyg4ometry.gdml.Defines.upgradeToVector([0, 0, 0], r, "undefined", addRegistry=False)
    assert p is None


# #############################
# ANTLR expressions
# #############################


def test_GdmlDefine_ExpressionInt():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", 1, r)
    assert xc.eval() == 1


def test_GdmlDefine_ExpressionFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", 1.2345, r)
    assert xc.eval() == 1.2345


def test_GdmlDefine_ExpressionScientific1():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", 1e3, r)
    assert xc.eval() == 1000


def test_GdmlDefine_ExpressionScientific2():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", 1.2345e3, r)
    assert xc.eval() == 1234.5


def test_GdmlDefine_ExpressionStringInt():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    assert xc.eval() == 1


def test_GdmlDefine_ExpressionStringFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1.2345", r)
    assert xc.eval() == 1.2345


def test_GdmlDefine_ExpressionStringScientific1():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1E3", r)
    assert xc.eval() == 1000


def test_GdmlDefine_ExpressionStringScientific2():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1.2345E3", r)
    assert xc.eval() == 1234.5


def test_GdmlDefine_ExpressionOperatorAddIntInt():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1+2", r)
    assert xc.eval() == 3


def test_GdmlDefine_ExpressionOperatorAddIntFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "2.3456+1", r)
    assert xc.eval() == 3.3456


def test_GdmlDefine_ExpressionOperatorAddFloatFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1.2345+2.3456", r)
    assert xc.eval() == 3.5801


def test_GdmlDefine_ExpressionOperatorAddFloatInt():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1+2.3456", r)
    assert xc.eval() == 3.3456


def test_GdmlDefine_ExpressionOperatorSubIntInt():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1-2", r)
    assert xc.eval() == -1


def test_GdmlDefine_ExpressionOperatorSubIntFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1-2.3456", r)
    assert xc.eval() == -1.3456000000000001


def test_GdmlDefine_ExpressionOperatorSubFloatInt():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "2.3456-1", r)
    assert xc.eval() == 1.3456000000000001


def test_GdmlDefine_FuncAbs():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "abs(-1)", r)
    assert xc.eval() == 1.0


# #############################
# Constants
# #############################
def test_GdmlDefine_ConstantSetName():
    r = pyg4ometry.geant4.Registry()
    c = pyg4ometry.gdml.Constant("xc", "1", r)
    c.setName("testName")
    assert c.name == "testName"
    assert c.expression.name == "expr_testName"


def test_GdmlDefine_ConstantOperatorAddExpressionExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    yc = pyg4ometry.gdml.Constant("yc", "2", r)
    assert (xc + yc).eval() == 3


def test_GdmlDefine_ConstantOperatorAddExpressionFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    assert (xc + 10).eval() == 11


def test_GdmlDefine_ConstantOperatorAddFloatExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    assert (10 + xc).eval() == 11


def test_GdmlDefine_ConstantOperatorSubExpressionExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    yc = pyg4ometry.gdml.Constant("yc", "2", r)
    assert (xc - yc).eval() == -1


def test_GdmlDefine_ConstantOperatorSubExpressionFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    assert (xc - 10).eval() == -9


def test_GdmlDefine_ConstantOperatorSubExpressionFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    assert (10 - xc).eval() == 9


def test_GdmlDefine_ConstantOperatorMulExpressionExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    yc = pyg4ometry.gdml.Constant("yc", "5", r)
    assert (xc * yc).eval() == 25


def test_GdmlDefine_ConstantOperatorMulExpressionFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    assert (xc * 5).eval() == 25


def test_GdmlDefine_ConstantOperatorMulFloatExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    assert (5 * xc).eval() == 25


def test_GdmlDefine_ConstantOperatorDivExpressionExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    yc = pyg4ometry.gdml.Constant("yc", "10", r)
    assert (xc / yc).eval() == 0.5


def test_GdmlDefine_ConstantOperatorDivExpressionFloat():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    assert (xc / 10).eval() == 0.5


def test_GdmlDefine_ConstantOperatorDivFloatExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    assert (10.0 / xc).eval() == 2


def test_GdmlDefine_ConstantOperationNegExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    assert (-xc).eval() == -5


def test_GdmlDefine_ConstantOperatorEqual():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    yc = pyg4ometry.gdml.Constant("yc", "5", r)
    zc = pyg4ometry.gdml.Constant("zc", "10", r)
    assert xc == yc
    assert xc != zc


def test_GdmlDefine_ConstantOperatorNotEqual():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    yc = pyg4ometry.gdml.Constant("yc", "5", r)
    zc = pyg4ometry.gdml.Constant("zc", "10", r)
    assert xc == yc
    assert xc != zc


def test_GdmlDefine_ConstantOperatorLessThan():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    yc = pyg4ometry.gdml.Constant("yc", "10", r)
    assert xc < yc
    assert yc > xc


def test_GdmlDefine_ConstantOperatorGreaterThan():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "10", r)
    yc = pyg4ometry.gdml.Constant("yc", "5", r)
    assert xc > yc
    assert yc < xc


def test_GdmlDefine_ConstantOperatorLessThanOrEqual():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "5", r)
    yc = pyg4ometry.gdml.Constant("yc", "10", r)
    zc = pyg4ometry.gdml.Constant("zc", "5", r)
    assert xc <= yc
    assert xc <= zc
    assert yc >= xc


def test_GdmlDefine_ConstantOperatorGreaterThanOrEqual():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "10", r)
    yc = pyg4ometry.gdml.Constant("yc", "5", r)
    zc = pyg4ometry.gdml.Constant("zc", "10", r)
    assert xc >= yc
    assert xc >= zc
    assert yc <= xc


def test_GdmlDefine_ConstantSinExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.sin(xc).eval() - 0.09983341664682815) < 1e-14


def test_GdmlDefine_ConstantCosExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.cos(xc).eval() - 0.9950041652780257) < 1e-14


def test_GdmlDefine_ConstantTanExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.tan(xc).eval() - 0.10033467208545055) < 1e-14


def test_GdmlDefine_ConstantExpExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.exp(xc).eval() - 1.1051709180756477) < 1e-14


def test_GdmlDefine_ConstantLogExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.log(xc).eval() - (-2.3025850929940455)) < 1e-14


def test_GdmlDefine_ConstantLog10Expression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert pyg4ometry.gdml.log10(xc).eval() == -1.0


def test_GdmlDefine_ConstantSqrtExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.sqrt(xc).eval() - 0.31622776601683794) < 1e-14


def test_GdmlDefine_ConstantArcSinExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.asin(xc).eval() - 0.1001674211615598) < 1e-14


def test_GdmlDefine_ConstantArcCosExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.acos(xc).eval() - 1.4706289056333368) < 1e-14


def test_GdmlDefine_ConstantArcTanExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "0.1", r)
    assert abs(pyg4ometry.gdml.atan(xc).eval() - 0.09966865249116204) < 1e-14


def test_GdmlDefine_PowExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "2", r)
    assert pyg4ometry.gdml.pow(xc, 2).eval() == 4


def test_GdmlDefine_AbsExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "-2", r)
    assert (pyg4ometry.gdml.abs(xc)).eval() == 2


def test_GdmlDefine_PowerOperator():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "-2", r)
    assert (xc**2).eval() == 4


def test_GdmlDefine_Min():
    r = pyg4ometry.geant4.Registry()
    a = pyg4ometry.gdml.Constant("a", "-2", r)
    b = pyg4ometry.gdml.Constant("b", "2", r)
    assert pyg4ometry.gdml.min(a, b).eval() == -2


def test_GdmlDefine_Max():
    r = pyg4ometry.geant4.Registry()
    a = pyg4ometry.gdml.Constant("a", "-2", r)
    b = pyg4ometry.gdml.Constant("b", "2", r)
    assert pyg4ometry.gdml.max(a, b).eval() == 2


# #############################
# Quantity
# #############################
def test_GdmlDefine_Quantity():
    r = pyg4ometry.geant4.Registry()
    xq = pyg4ometry.gdml.Quantity("xq", "0.1", "kg", "mass", r)
    assert xq.eval() == 6.241506363094027e23
    assert float(xq) == 6.241506363094027e23
    str(xq)


# #############################
# Variable
# #############################
def test_GdmlDefine_Variable():
    r = pyg4ometry.geant4.Registry()
    xv = pyg4ometry.gdml.Variable("xv", "0.1", r)
    assert xv.eval() == 0.1
    assert float(xv) == 0.1
    str(xv)


# #############################
# Expression
# #############################
def test_GdmlDefine_Expression():
    r = pyg4ometry.geant4.Registry()
    xe = pyg4ometry.gdml.Expression("xe", "0.1", r, True)
    assert xe.eval() == 0.1
    assert float(xe) == 0.1
    str(xe)


# #############################
# Position
# #############################
def test_GdmlDefine_PositionSetName():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", "1", "2", "3", "mm", r)
    v.setName("newName")
    assert v.name == "newName"


def test_GdmlDefine_PositionGetItem():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", "1", "2", "3", "mm", r)

    assert v[0].eval() == 1
    assert v[1].eval() == 2
    assert v[2].eval() == 3

    try:
        v[3]
    except IndexError:
        pass


def test_GdmlDefine_PositionConstructorStrStrStr():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", "1", "2", "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorStrStrFloat():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", "1", "2", 3, "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorStrFloatStr():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", "1", 2, "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorFloatStrStr():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", 1, "2", "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorStrStrExpression():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "3", r)
    v = pyg4ometry.gdml.Position("p", "1", "2", xc, "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorStrExpressionStr():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "2", r)
    v = pyg4ometry.gdml.Position("p", "1", xc, "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorExpressionStrStr():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    v = pyg4ometry.gdml.Position("p", xc, "2", "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorStrStrExprstr():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "3", r)
    v = pyg4ometry.gdml.Position("p", "1", "2", "xc", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorStrExprstrStr():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "2", r)
    v = pyg4ometry.gdml.Position("p", "1", "xc", "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorExprstrStrStr():
    r = pyg4ometry.geant4.Registry()
    xc = pyg4ometry.gdml.Constant("xc", "1", r)
    v = pyg4ometry.gdml.Position("p", "xc", "2", "3", "mm", r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionConstructorUnitNone():
    r = pyg4ometry.geant4.Registry()
    v = pyg4ometry.gdml.Position("p", "1", "2", "3", None, r)
    assert v.eval() == [1, 2, 3]


def test_GdmlDefine_PositionOperatorAdd():
    r = pyg4ometry.geant4.Registry()
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    v2 = pyg4ometry.gdml.Position("v2", "11", "12", "13", "mm", r)
    assert (v1 + v2).eval() == [12, 14, 16]


def test_GdmlDefine_PositionOperatorSub():
    r = pyg4ometry.geant4.Registry()
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    v2 = pyg4ometry.gdml.Position("v2", "11", "12", "13", "mm", r)
    assert (v2 - v1).eval() == [10, 10, 10]


def test_GdmlDefine_PositionOperatorMulFloatPosition():
    r = pyg4ometry.geant4.Registry()
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    assert (10.0 * v1).eval() == [10, 20, 30]


def test_GdmlDefine_PositionOperatorMulPositionFloat():
    r = pyg4ometry.geant4.Registry()
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    assert (v1 * 10.0).eval() == [10, 20, 30]


def test_GdmlDefine_PositionOperatorMulExpressionPosition():
    r = pyg4ometry.geant4.Registry()
    x = pyg4ometry.gdml.Constant("x", "1.5", r)
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    assert (x * v1).eval() == [1.5, 3.0, 4.5]


def test_GdmlDefine_PositionOperatorMulPositionExpression():
    r = pyg4ometry.geant4.Registry()
    x = pyg4ometry.gdml.Constant("x", "1.5", r)
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    assert (v1 * x).eval() == [1.5, 3.0, 4.5]


def test_GdmlDefine_PositionOperatorDivPositionFloat():
    r = pyg4ometry.geant4.Registry()
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    assert (v1 / 10).eval() == [0.1, 0.2, 0.3]


def test_GdmlDefine_PositionOperatorDivPositionExpression():
    r = pyg4ometry.geant4.Registry()
    x = pyg4ometry.gdml.Constant("x", "10.0", r)
    v1 = pyg4ometry.gdml.Position("v1", "1", "2", "3", "mm", r)
    assert (v1 / x).eval() == [0.1, 0.2, 0.3]


# #############################
# Rotations
# #############################
def test_GdmlDefine_Rotation():
    r = pyg4ometry.geant4.Registry()
    r1 = pyg4ometry.gdml.Rotation("r1", 1, 2, 3, "rad", r, True)
    r2 = pyg4ometry.gdml.Rotation("r2", 1, 2, 3, "deg", r, True)
    r3 = pyg4ometry.gdml.Rotation("r3", 1, 2, 3, None, r, True)
    r4 = pyg4ometry.gdml.Rotation("r4", 1, 2, 3, None, r, False)
    str(r1)


# #############################
# Scale
# #############################
def test_GdmlDefine_Scale():
    r = pyg4ometry.geant4.Registry()
    s1 = pyg4ometry.gdml.Scale("s1", 1, 2, 3, None, r, True)
    s2 = pyg4ometry.gdml.Scale("s2", 1, 2, 3, None, r, False)
    str(s1)


# #############################
# Matrix
# #############################
def test_GdmlDefine_MatrixConstructor1x10():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 1, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, False)
    assert (mat.eval() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).all()


def test_GdmlDefine_MatrixConstructor1x10():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, False)


def test_GdmlDefine_Matrix1x10Index():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 1, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, False)
    assert mat[9].eval() == 10


def test_GdmlDefine_Matrix2x5Index():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, False)
    assert mat[0][2].eval() == 3


def test_GdmlDefine_MatrixConstructor1x10AddRegistry():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 1, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, True)
    assert (mat.eval() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).all()


def test_GdmlDefine_MatrixRepr():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, True)
    str(mat)


def test_GdmlDefine_MatrixGetItemInRegistry():
    r = pyg4ometry.geant4.Registry()
    mat = pyg4ometry.gdml.Matrix("mat", 2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], r, True)
    v = mat[0, 0]
    assert v.expression.expressionString == "mat[1,1]"
