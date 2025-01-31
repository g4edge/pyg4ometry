import numbers as _numbers
import numpy as _np
import re as _re
import logging as _log
from . import Units as _Units

_log = _log.getLogger(__name__)


class BasicExpression:
    """
    Holds an expression as a string and can use the expression parser
    in the supplied registry to evaluate it. A registry is required.

    :param name: Name of the expression object
    :type name: str
    :param expressionString: Expression itself as a string e.g. "12.0" or "a + 3.0"
    :type expressionString: str
    :param registry: The registry object to give context for any variables used.
    :type registry: pyg4ometry.geant4.Registry.Registry

    >>> r = pyg4ometry.geant4.Registry()
    >>> a = BasicExpression("a", "3.0", r)
    >>> float(a)
    >>> str(a)
    """

    def __init__(self, name, expressionString, registry):
        self.name = name
        self.expressionString = expressionString
        self.parseTree = None
        self.registry = registry

    def eval(self):
        # short-cut for expressions only having a numeric part.
        num_re = r"-?[0-9]+(?:\.[0-9]+)?(?:e-?[0-9]{1,2})?"
        if _re.match(num_re + "$", self.expressionString):
            return float(self.expressionString)

        # short-cut for expressions only having a numeric part and a unit.
        num_w_unit_re = "(" + num_re + r")(?:\*([a-zA-Z]+))?$"
        match_w_unit = _re.match(num_w_unit_re, self.expressionString)
        if match_w_unit:
            unit = _Units.unit(match_w_unit.group(2))
            if unit is not None:
                return float(match_w_unit.group(1)) * unit

        expressionParser = self.registry.getExpressionParser()
        self.parseTree = expressionParser.parse(self.expressionString)
        value = expressionParser.evaluate(self.parseTree, self.registry.defineDict)
        return value

    def variables(self, allDependents=False):
        expressionParser = self.registry.getExpressionParser()
        self.parseTree = expressionParser.parse(self.expressionString)
        variables = expressionParser.get_variables(self.parseTree)
        if allDependents:
            dependents = []
            for v in variables:
                if v in self.registry.defineDict:
                    define = self.registry.defineDict[v]
                    dependents = define.expression.variables() + dependents  # prepend
            variables = dependents + variables  # prepend
        result = []
        [
            result.append(v) for v in variables if v not in result
        ]  # remove duplicates but preserve prepended order
        return result

    def simp(self):
        # find all variables of the expression and create
        pass

    def __repr__(self):
        return f"{self.name} : {self.expressionString}"

    def __float__(self):
        return self.eval()

    def str(self):
        return "BasicExpression : " + self.name + " : " + str(float(self))


def upgradeToStringExpression(reg, obj):
    """
    Take a float, str, ScalarBase and return string expression.

    :param reg: Registry for lookup in define dictionary
    :type reg: Registry
    :param obj: Object to upgrade
    :type obj: str,float,ScalarBase
    :return: String expression
    :rtype: str
    """
    if isinstance(obj, _numbers.Number):
        # return str(obj)                  # number like so return string
        return f"{obj:.15f}"

    elif isinstance(obj, str):  # or isinstance(obj,unicode) :
        if obj in reg.defineDict:  # not sure if this is needed
            return obj
        else:
            e = BasicExpression("", obj, reg)
            try:
                e.eval()
                return obj
            except Exception as err:
                msg = f"<= Cannot evaluate expression : {obj}"
                if not err.args:
                    err.args = ("",)
                err.args = (*err.args, msg)
                raise

    elif isinstance(obj, ScalarBase):
        if obj.name in reg.defineDict:
            return obj.name  # so a scalar expression in registry
        else:
            return obj.expression.expressionString  # so a scalar expression not in registry

    else:
        raise ValueError("upgradeToStringExpression> unsupported type (" + str(type(obj)) + ")")


def evaluateToFloat(reg, obj):
    try:
        if isinstance(obj, str):
            raise AttributeError
        ans = [evaluateToFloat(reg, item) for item in obj.__iter__()]
    except (AttributeError,):
        if isinstance(obj, _numbers.Number) or isinstance(obj, BasicExpression):
            return float(obj)
        elif isinstance(obj, ScalarBase) or isinstance(obj, VectorBase):
            return obj.eval()
        else:
            evaluatable = BasicExpression("", obj, reg)
        ans = float(evaluatable.eval())
    return ans


def upgradeToExpression(reg, obj):
    """
    Helper functions that takes a string and returns an expression object or a string
    """

    # TODO: consider merging into/reusing the upgradeToStringExpression
    as_string = upgradeToStringExpression(reg, obj)
    expression = BasicExpression("", as_string, reg)

    try:
        float(expression)
        return expression
    except ValueError:
        return as_string


def upgradeToVector(var, reg, type="position", unit="", addRegistry=False):
    """
    Take a list [x,y,z] and create a vector

    :param var: input list to create a position, rotation or scale
    :type var: list of str, float, Constant, Quantity, Variable
    :param reg: registry
    :type reg: Registry
    :param type: class type of vector (position, rotation, scale)
    :type type: str
    :param addRegistry: flag to add to registry
    :type addRegistry: bool
    """
    # check units
    if type == "position" and unit == "":
        unit = "mm"
    elif type == "rotation" and unit == "":
        unit = "rad"

    # check if already a vector type
    if isinstance(var, VectorBase):
        return var

    # create appropriate vector type
    if isinstance(var, list) or isinstance(var, _np.ndarray):
        if type == "position":
            return Position("", var[0], var[1], var[2], unit, reg, addRegistry)
        elif type == "rotation":
            return Rotation("", var[0], var[1], var[2], unit, reg, addRegistry)
        elif type == "scale":
            return Scale("", var[0], var[1], var[2], "none", reg, addRegistry)
        else:
            _log.warning(f"vector type {type} not defined")


def upgradeToTransformation(var, reg, addRegistry=False):
    """
    Take a list of lists [[rx,ry,rz],[x,y,z]] and create a transformation [Rotation,Position]

    :param var: input list to create a transformation
    :type var: list of str, float, Constant, Quantity, Variable
    :param reg: registry
    :type reg: Registry
    :param addRegistry: flag to add to registry
    :type addRegistry: bool
    """
    if isinstance(var[0], VectorBase):
        rot = var[0]
    elif isinstance(var[0], list):
        try:
            aunit = var[0][3]
        except:
            aunit = ""
        rot = upgradeToVector(var[0], reg, "rotation", aunit, addRegistry)
    else:
        msg = f"Unknown rotation type: {type(var[0])}"
        raise TypeError(msg)

    if isinstance(var[1], VectorBase):
        tra = var[1]
    elif isinstance(var[1], list):
        try:
            lunit = var[1][3]
        except:
            lunit = ""
        tra = upgradeToVector(var[1], reg, "position", lunit, addRegistry)
    else:
        msg = f"Unknown position type: {type(var[1])}"
        raise TypeError(msg)

    return [rot, tra]


def operationReturnType(name, strExpr, v1, v2, type1, type2, reg):
    if type1 == Constant and type2 == Constant:
        v = Constant(
            name,
            strExpr,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif (type1 == Constant and type2 == Variable) or (type1 == Variable and type2 == Constant):
        v = Variable(
            name,
            strExpr,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Constant and type2 == Quantity:
        v = Quantity(
            name,
            strExpr,
            unit=v2.unit,
            type=v2.type,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Quantity and type2 == Constant:
        v = Quantity(
            name,
            strExpr,
            unit=v1.unit,
            type=v2.type,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Variable and type2 == Variable:
        v = Variable(
            name,
            strExpr,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Variable and type2 == Quantity:
        v = Quantity(
            name,
            strExpr,
            unit=v2.unit,
            type=v2.type,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Quantity and type2 == Variable:
        v = Quantity(
            name,
            strExpr,
            unit=v1.unit,
            type=v2.type,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Quantity and type2 == Quantity:
        # TODO check if units match
        v = Quantity(
            name,
            strExpr,
            unit=v2.unit,
            type=v2.type,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type1 == Constant:
        v = Constant(
            name,
            strExpr,
            registry=reg,
            addRegistry=False,
        )
        return v
    elif type2 == Constant:
        v = Constant(
            name,
            strExpr,
            registry=reg,
            addRegistry=False,
        )
        return v


class DefineBase:
    """
    Common bits for a define. Must have a name and a registry. Adding
    to the registry can't be done here as it must be done by the derived type.
    """

    def __init__(self, name="", registry=None):
        self.name = name
        self.registry = registry

    def setName(self, name):
        """
        Set name of the object.

        :param name: name of object
        :type name: str
        """
        self.name = name

    def setRegistry(self, registry):
        self.registry = registry


class ScalarBase(DefineBase):
    """
    Base class for all scalars (Constants, Quantity, Variable and 'Expression')
    """

    def __init__(self, typeName, name="", registry=None):
        super().__init__(name, registry)
        self.expression = None
        self._typeName = typeName

    def setName(self, name):
        """
        Set name of scalar

        :param name: name of object
        :type name: str
        """
        super().setName(name)
        self.expression.name = f"expr_{name}"

    def setExpression(self, expressionString):
        """
        Take a string and make it into the BasicExpression type for this object.

        :param expressionString: Expression to store.
        :type expressionString: str
        """
        self.expression = BasicExpression(
            f"expr_{self.name}",
            upgradeToStringExpression(self.registry, expressionString),
            self.registry,
        )

    def setRegistry(self, registry):
        super().setRegistry(registry)
        if self.expression:
            registry.transferDefine(self)

    def eval(self):
        """
        Evaluate the expression

        :return: numerical evaluation of Constant
        :rtype: float
        """
        return self.expression.eval()

    def __repr__(self):
        return self._typeName + f" : {self.name} = {self.expression!s}"

    def __float__(self):
        return self.eval()

    def __add__(self, other):
        v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        v = Constant(
            f"var_{v1}_add_{v2}",
            f"({v1}) + ({v2})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

        # return operationReturnType(f"var_{v1}_add_{v2}",
        #                           f"({v1}) + ({v2})",
        #                           self, other,
        #                           type(self), type(other), self.registry)

    def __sub__(self, other):
        v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        v = Constant(
            f"var_{v1}_sub_{v2}",
            f"({v1}) - ({v2})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

    def __rsub__(self, other):
        v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        v = Constant(
            f"var_{v2}_sub_{v1}",
            f"({v2}) - ({v1})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

    def __mul__(self, other):
        # check to see if other is a vector
        if isinstance(other, VectorBase):
            return other * self

        v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        v = Constant(
            f"var_{v1}_mul_{v2}",
            f"({v1}) * ({v2})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

    def __truediv__(self, other):
        v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        v = Constant(
            f"var_{v1}_div_{v2}",
            f"({v1}) / ({v2})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

    def __rtruediv__(self, other):
        v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        v = Constant(
            f"var_{v2}_div_{v1}",
            f"({v2}) / ({v1})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

    def __neg__(self):
        v1 = upgradeToStringExpression(self.registry, self)

        v = Constant(
            f"var_neg_{v1}",
            f"-({v1})",
            registry=self.registry,
            addRegistry=False,
        )
        return v

    def __abs__(self):
        return abs(self)

    def __pow__(self, power):
        return pow(self, power)

    __radd__ = __add__
    __rmul__ = __mul__


def sin(arg):
    """
    Sin of a ScalarBase object, returns a Constant

    :param arg: Argument of sin
    :type  arg: Constant, Quantity, Variable or Expression
    """

    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"sin_{v1}",
        f"sin({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def cos(arg):
    """
    Cosine of a ScalarBase object, returns a Constant

    :param arg: Argument of cos
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"cos_{v1}",
        f"cos({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def tan(arg):
    """
    Tangent of a ScalarBase object, returns a Constant

    :param arg: Argument of tan
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"tan_{v1}",
        f"tan({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def asin(arg):
    """
    ArcSin of a ScalarBase object, returns a Constant

    :param arg: Argument of asin
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"sin_{v1}",
        f"asin({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def acos(arg):
    """
    ArcCos of a ScalarBase object, returns a Constant

    :param arg: Argument of acos
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"cos_{v1}",
        f"acos({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def atan(arg):
    """
    ArcTan of a ScalarBase object, returns a Constant

    :param arg: Argument of tan
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"tan_{v1}",
        f"atan({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def exp(arg):
    """
    Exponential of a ScalarBase object, returns a Constant

    :param arg: Argument of exp
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"exp_{v1}",
        f"exp({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def log(arg):
    """
    Natural logarithm of a ScalarBase object, returns a Constant

    :param arg: Argument of log
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"log_{v1}",
        f"log({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def log10(arg):
    """
    Base 10 logarithm of a ScalarBase object, returns a Constant

    :param arg: Argument of log10
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"log10_{v1}",
        f"log10({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def sqrt(arg):
    """
    Square root of a ScalarBase object, returns a Constant

    :param arg: Argument of sin
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"sqrt_{v1}",
        f"sqrt({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def pow(arg, power):
    """
    arg raised to power

    :param arg: Argument of x**y
    :type  arg: Constant, Quantity, Variable or Expression
    :param power: y
    :type power: float
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"sqrt_{v1}",
        f"pow({v1},{power!s})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def abs(arg):
    """
    absolute value of arg

    :param arg: Argument of abs(arg)
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg.registry, arg)
    v = Constant(
        f"abs_{v1}",
        f"abs({v1})",
        registry=arg.registry,
        addRegistry=False,
    )
    return v


def min(arg1, arg2):
    """
    absolute value of arg

    :param arg: Argument of abs(arg)
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg1.registry, arg1)
    v2 = upgradeToStringExpression(arg1.registry, arg2)
    v = Constant(
        f"min_{v1}_{v2}",
        f"min({v1},{v2})",
        registry=arg1.registry,
        addRegistry=False,
    )
    return v


def max(arg1, arg2):
    """
    absolute value of arg

    :param arg: Argument of abs(arg)
    :type  arg: Constant, Quantity, Variable or Expression
    """
    v1 = upgradeToStringExpression(arg1.registry, arg1)
    v2 = upgradeToStringExpression(arg1.registry, arg2)
    v = Constant(
        f"min_{v1}_{v2}",
        f"max({v1},{v2})",
        registry=arg1.registry,
        addRegistry=False,
    )
    return v


class Constant(ScalarBase):
    """
    GDML constant define wrapper object

    :param name: of constant for registry
    :type name: str
    :param value: expression for constant
    :type value: float,str,Constant,Quantity,Variable
    :param registry: for storing define
    :type registry: Registry
    :param addRegistry: add constant to registry
    :type addRegistry: bool
    """

    def __init__(self, name, value, registry, addRegistry=True):
        super().__init__("Constant", name, registry)
        self.expression = BasicExpression(
            f"expr_{name}", upgradeToStringExpression(registry, value), registry
        )

        if registry and addRegistry:
            registry.addDefine(self)

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.eval() == other.eval()
        else:
            return self.eval() == other

    def __ne__(self, other):
        if isinstance(other, Constant):
            return self.eval() != other.eval()
        else:
            return self.eval() != other

    def __lt__(self, other):
        if isinstance(other, Constant):
            return self.eval() < other.eval()
        else:
            return self.eval() < other

    def __gt__(self, other):
        if isinstance(other, Constant):
            return self.eval() > other.eval()
        else:
            return self.eval() > other

    def __le__(self, other):
        if isinstance(other, Constant):
            return self.eval() <= other.eval()
        else:
            return self.eval() <= other

    def __ge__(self, other):
        if isinstance(other, Constant):
            return self.eval() >= other.eval()
        else:
            return self.eval() >= other


class Quantity(ScalarBase):
    """
    GDML quantity define wrapper object

    :param name: of constant for registry
    :type name: str
    :param value: expression for constant
    :type value: float,str,Constant,Quantity,Variable
    :param unit: unit of the quantity
    :type unit: str
    :param type: type of quantity
    :type type: not sure
    :param registry: for storing define
    :type registry: Registry
    :param addRegistry: add constant to registry
    :type addRegistry: bool
    """

    def __init__(self, name, value, unit, type, registry, addRegistry=True):
        super().__init__("Quantity", name, registry)
        self.unit = unit
        self.type = type
        self.expression = BasicExpression(
            f"expr_{name}", upgradeToStringExpression(registry, value), registry
        )

        if registry and addRegistry:
            registry.addDefine(self)

    def __repr__(self):
        return self._typeName + f" : {self.name} = {self.expression!s} [{self.unit}] {self.type}"

    def eval(self):
        # it is possible for a quantity not to have a unit and it uses the units of variables in the expression
        if self.unit:
            uval = _Units.unit(self.unit)
        else:
            uval = 1.0

        # evaluate quantity with units baked in
        return super().eval() * uval


class Variable(ScalarBase):
    """
    GDML variable define wrapper object

    :param name: of constant for registry
    :type name: str
    :param value: expression for constant
    :type value: float,str,Constant,Quantity,Variable
    :param registry: for storing define
    :type registry: Registry
    """

    def __init__(self, name, value, registry, addRegistry=True):
        super().__init__("Variable", name, registry)
        self.expression = BasicExpression(
            f"expr_{name}", upgradeToStringExpression(registry, value), registry
        )

        if registry and addRegistry:
            registry.addDefine(self)


class Expression(ScalarBase):
    """
    General expression, does not have an analogue in GDML

    :param name: of constant for registry
    :type name: str
    :param value: expression for constant
    :type value: float,str,Constant,Quantity,Variable
    :param registry: for storing define
    :type registry: Registry
    :param addRegistry: add constant to registry
    :type addRegistry: bool
    """

    def __init__(self, name, value, registry, addRegistry=False):
        super().__init__("Expression", name, registry)
        self.expression = BasicExpression(
            f"expr_{name}", upgradeToStringExpression(registry, value), registry
        )

        if registry and addRegistry:
            registry.addDefine(self)

    def __int__(self):
        return int(self.expression.eval())


class VectorBase:
    def __init__(self, typeName, name, registry):
        self._typeName = typeName
        self.name = name
        self.registry = registry
        self.x = None
        self.y = None
        self.z = None
        self.unit = None

    def __repr__(self):
        return self._typeName + f" : {self.name} = [{self.x!s} {self.y!s} {self.z!s}]"

    def __add__(self, other):
        other = upgradeToVector(other, self.registry, "position", "", False)

        p = Position(
            f"vec_{self.name}_add_{other.name}",
            f"({self.x.expressionString})+({other.x.expressionString})",
            f"({self.y.expressionString})+({other.y.expressionString})",
            f"({self.z.expressionString})+({other.z.expressionString})",
            self.unit,
            self.registry,
            False,
        )
        p.registry = self.registry
        p.x.registry = self.registry
        p.y.registry = self.registry
        p.z.registry = self.registry
        return p

    def __sub__(self, other):
        other = upgradeToVector(other, self.registry, "position", "", False)

        p = Position(
            f"vec_{self.name}_sub_{other.name}",
            f"({self.x.expressionString})-({other.x.expressionString})",
            f"({self.y.expressionString})-({other.y.expressionString})",
            f"({self.z.expressionString})-({other.z.expressionString})",
            self.unit,
            self.registry,
            False,
        )
        p.registry = self.registry
        p.x.registry = self.registry
        p.y.registry = self.registry
        p.z.registry = self.registry
        return p

    def __mul__(self, other):
        # v1 = upgradeToStringExpression(self.registry, self)
        v2 = upgradeToStringExpression(self.registry, other)

        p = Position(
            f"vec_{self.name}_mul_{v2}",
            f"({self.x.expressionString})*({v2})",
            f"({self.y.expressionString})*({v2})",
            f"({self.z.expressionString})*({v2})",
            self.unit,
            self.registry,
            False,
        )
        p.registry = self.registry
        p.x.registry = self.registry
        p.y.registry = self.registry
        p.z.registry = self.registry
        return p

    __rmul__ = __mul__

    def __truediv__(self, other):
        # v1 = upgradeToStringExpression(self.registry,self)
        v2 = upgradeToStringExpression(self.registry, other)

        p = Position(
            f"vec_{self.name}_div_{v2}",
            f"({self.x.expressionString})/({v2})",
            f"({self.y.expressionString})/({v2})",
            f"({self.z.expressionString})/({v2})",
            self.unit,
            self.registry,
            False,
        )
        p.registry = self.registry
        p.x.registry = self.registry
        p.y.registry = self.registry
        p.z.registry = self.registry
        return p

    def setName(self, name):
        """
        Set name of vector

        :param name: name of object
        :type name: str
        """
        self.name = name
        self.x.registry = self.registry
        self.y.registry = self.registry
        self.z.registry = self.registry
        self.x.name = f"expr_{name}_vec_x"
        self.y.name = f"expr_{name}_vec_y"
        self.z.name = f"expr_{name}_vec_z"
        self.registry.addDefine(self)

    def eval(self):
        """
        Evaluate vector

        :return: numerical evaluation of vector
        :rtype: list of floats
        """
        u = _Units.unit(self.unit)
        return [self.x.eval() * u, self.y.eval() * u, self.z.eval() * u]

    def nonzero(self):
        """
        Evaluate vector

        :return: Check if the vector is trivial (all elements zero)
        :rtype: bool
        """
        return any(self.eval())

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError

    def setRegistry(self, registry):
        self.registry = registry
        self.x.registry = self.registry
        self.y.registry = self.registry
        self.z.registry = self.registry


class Position(VectorBase):
    """
    GDML position define wrapper object

    :param x: x component of position
    :type x: float, Constant, Quantity, Variable
    :param y: y component of position
    :type y: float, Constant, Quantity, Variable
    :param z: z component of position
    :type z: float, Constant, Quantity, Variable
    """

    def __init__(self, name, x, y, z, unit="mm", registry=None, addRegistry=True):
        super().__init__("Position", name, registry)

        if unit is not None:
            if not isinstance(unit, str):
                msg = "unit must be None or a string"
                raise ValueError(msg)
            self.unit = unit
        else:
            self.unit = "mm"

        self.x = BasicExpression(
            f"expr_pos_x_{name}",
            upgradeToStringExpression(registry, x),
            registry=registry,
        )
        self.y = BasicExpression(
            f"expr_pos_y_{name}",
            upgradeToStringExpression(registry, y),
            registry=registry,
        )
        self.z = BasicExpression(
            f"expr_pos_z_{name}",
            upgradeToStringExpression(registry, z),
            registry=registry,
        )

        if registry and addRegistry:
            self.registry.addDefine(self)


class Rotation(VectorBase):
    """
    GDML rotation define wrapper object

    :param rx: rotation around x axis
    :type rx: float, Constant, Quantity, Variable
    :param ry: rotation around y axis
    :type ry: float, Constant, Quantity, Variable
    :param rz: rotation around z axis
    :type rz: float, Constant, Quantity, Variable
    """

    def __init__(self, name, rx, ry, rz, unit="rad", registry=None, addRegistry=True):
        super().__init__("Rotation", name, registry)

        if unit is not None:
            if not isinstance(unit, str):
                msg = "unit must be None or a string"
                raise ValueError(msg)
            acceptableUnits = ["rad", "radian", "mrad", "milliradian", "deg", "degree"]
            if unit not in acceptableUnits:
                raise ValueError(
                    'Invalid unit "'
                    + unit
                    + '" in rotation define "'
                    + name
                    + '" - can be one of:  '
                    + ", ".join(acceptableUnits)
                )
            self.unit = unit
        else:
            self.unit = "rad"

        self.x = BasicExpression(
            f"expr_rot_x_{name}",
            upgradeToStringExpression(registry, rx),
            registry=registry,
        )
        self.y = BasicExpression(
            f"expr_rot_y_{name}",
            upgradeToStringExpression(registry, ry),
            registry=registry,
        )
        self.z = BasicExpression(
            f"expr_rot_z_{name}",
            upgradeToStringExpression(registry, rz),
            registry=registry,
        )

        if registry and addRegistry:
            self.registry.addDefine(self)


class Scale(VectorBase):
    """
    GDML scale define wrapper object

    :param sx: x component of scale
    :type sx: float, Constant, Quantity, Variable
    :param sy: y component of scale
    :type sy: float, Constant, Quantity, Variable
    :param sz: z component of scale
    :type sz: float, Constant, Quantity, Variable
    """

    def __init__(self, name, sx, sy, sz, unit=None, registry=None, addRegistry=True):
        super().__init__("Scale", name, registry)

        if unit != None:
            if not isinstance(unit, str):
                msg = "unit must be None or a string"
                raise ValueError(msg)
            self.unit = unit
        else:
            self.unit = "none"

        self.x = BasicExpression(
            f"expr_scl_x_{name}",
            upgradeToStringExpression(registry, sx),
            registry=registry,
        )
        self.y = BasicExpression(
            f"expr_scl_y_{name}",
            upgradeToStringExpression(registry, sy),
            registry=registry,
        )
        self.z = BasicExpression(
            f"expr_scl_z_{name}",
            upgradeToStringExpression(registry, sz),
            registry=registry,
        )

        if registry and addRegistry:
            self.registry.addDefine(self)


class Matrix:
    """
    GDML matrix define wrapper object

    :param name: of matrix for registry
    :type name: str
    :param coldim: is number of columns
    :param coldim: int
    :param values: list of values for matrix
    :type values: list of float, str, Constant, Quantity, Variable
    :param registry: for storing define
    :type registry: Registry
    :param addRegistry: add matrix to registry
    :type addRegistry: bool
    """

    def __init__(self, name, coldim, values, registry=None, addRegistry=True):
        self.name = name
        self.coldim = int(coldim)
        self.registry = registry

        self.values = []
        for i, v in enumerate(values):
            self.values.append(
                Expression(
                    f"matrix_expr_idx{i}_val_{name}",
                    upgradeToStringExpression(registry, v),
                    registry=registry,
                )
            )

        self.values_asarray = _np.array(self.values, dtype=_np.object_)
        if self.coldim > 1:
            self.values_asarray = self.values_asarray.reshape(
                self.coldim, int(len(values) / self.coldim)
            )

        if registry and addRegistry:
            self.registry.addDefine(self)

    def eval(self):
        """
        Evaluate matrix

        :return: numerical evaluation of matrix
        :rtype: numpy.array
        """
        a = _np.array([e.eval() for e in self.values])
        a = a.reshape(self.coldim, int(len(a) / self.coldim))
        return a

    def __repr__(self):
        return f"Matrix : {self.name} = {self.coldim!s} {self.values!s}"

    def __getitem__(self, key):
        if self.name in self.registry.defineDict:
            stridx = ",".join([str(v + 1) for v in key])
            return Expression("dummy_name", self.name + "[" + stridx + "]", self.registry, False)
        else:
            return self.values_asarray[key]


def MatrixFromVectors(e, v, name, registry, eunit="eV", vunit=""):
    """
    Creates a GDML Matrix from an energy and a value vector

    :param name: of matrix of registry
    :type  name: str
    :param e: energy list/vector in units of eunit
    :type e: list or numpy.array - shape (1,)
    :param v: value list/vector in units of vunit
    :type v: list or numpy.array - shape (1,)
    :param registry: for storing define
    :type registry: Registry
    :param eunit: unit for the energy vector (default: eV)
    :type eunit: str
    :param vunit: unit for the value vector (default: unitless)
    :type vunit: str
    """
    assert len(e) == len(v)
    eunit = "*" + eunit if eunit != "" else ""
    vunit = "*" + vunit if vunit != "" else ""

    e = [str(x) + eunit for x in e]
    v = [str(x) + vunit for x in v]

    res = e + v
    res[::2] = e
    res[1::2] = v
    return Matrix(name, 2, res, registry)


class Auxiliary:
    """
    Auxiliary information container object
    """

    # Note that no interpreting or processing is done for auxiliary information
    def __init__(self, auxtype, auxvalue, registry=None, unit="", addRegistry=True):
        self.auxtype = str(auxtype)
        self.auxvalue = str(auxvalue)
        self.auxunit = str(unit)
        self.subaux = []
        self.registry = registry
        if self.registry and addRegistry:
            self.registry.addAuxiliary(self)

    def addSubAuxiliary(self, aux):
        """
        Add a sub-auxiliary inside the scope of the current auxiliary

        :param aux: auxiliary definition
        :type aux: object, gdml.Defines.Auxiliary
        """
        if not isinstance(aux, Auxiliary):
            msg = "Added object must be a gdml.Defines.Auxiliary instance."
            raise ValueError(msg)
        self.subaux.append(aux)
