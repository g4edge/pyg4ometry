import ast
import operator
import os.path
import sys

import numpy as np

from pyg4ometry.exceptions import FLUKAError


def _degree_input(f):
    return lambda x: f(x * np.pi / 180)

def _degree_output(f):
    return lambda x: f(x) * 180 / np.pi

_FLUKA_PREDEFINED_IDS = {"Pipipi": np.pi,
                         "Minute": 60,
                         "Hour": 3600,
                         "Day": 86400,
                         "Week": 604800,
                         "Month": 2629745.0927999998,
                         "Year": 31556941.113599997}

_FLUKA_PREDEFINED_FUNCTIONS = {"Sin": np.sin,
                               "Cos": np.cos,
                               "Tan": np.tan,
                               "Exp": np.exp,
                               "Log": np.log,
                               "Abs": abs,
                               "Sind": _degree_input(np.sin),
                               "Cosd": _degree_input(np.cos),
                               "Tand": _degree_input(np.tan),
                               "Asin": np.arcsin,
                               "Acos": np.arccos,
                               "Atan": np.arctan,
                               "Sqrt": np.sqrt,
                               "Sinh": np.arcsinh,
                               "Cosh": np.cosh,
                               "Asind": _degree_output(np.arcsin),
                               "Acosd": _degree_output(np.arccos),
                               "Atand": _degree_output(np.arctan),
                               "Asinh": np.arcsinh,
                               "Acosh": np.arccosh}


def preprocess(filein):
    with open(filein, "r") as f:
        lines = f.readlines()

    preprocessed_lines = []
    directory = os.path.dirname(filein)

    defines = {}
    if_stack = [] # [_IfInfo1, _IfInfo2, ...]
    line_stack = list(reversed(lines)) # a stack of lines

    while line_stack:
        line = line_stack.pop()
        if not line.split(): # If just a line of whitespace
            continue

        line = line.split("!")[0] # "!" comments
        line = line.strip()  # Leading and trailing whitespace

        if not line: # If "!" commented out entire line.
            continue

        if line.startswith("*"): # line starting with "*" comment
            continue

        if line[0] == "#":
            split_line = line.split()
            directive = split_line[0]

            if directive == "#define" or directive == "#undef":
                _parse_preprocessor_define(directive, split_line, defines)
            elif directive == "#include":
                _parse_preprocessor_include(directory,
                                            directive,
                                            split_line,
                                            line_stack)
            elif directive in ["#if", "#elif", "#endif", "#else"]:
                _parse_preprocessor_conditional(directive,
                                                split_line,
                                                defines,
                                                if_stack)
            else:
                raise ValueError(
                    "Unknown preprocessor directive: {}".format(directive))
            continue # Don't include preprocessoes
        if if_stack and not all([e.read_until_next for e in if_stack]):
            continue

        preprocessed_lines.append(line)

    return preprocessed_lines, lines


class _IfInfo(object):
    """Tells us about current conditional and its state at the current line.


    - If the conditional at this level has been satisfied (e.g. if the
      IF has been satisfied then we don't read any subsequent ELIF or
      ELSE clauses, we skip until the next ENDIF).
    - If we should read until the next conditional directive (e.g. if
      the IF or ELIF has been satisfied then we should read all lines
      following this directive until we reach the next conditional directive.

    """
    def __init__(self, any_branch_satisfied, read_until_next):
        self.any_branch_satisfied = any_branch_satisfied
        self.read_until_next = read_until_next

    def __repr__(self):
        return ("<IfInfo: any_branch_satisfied={}, "
                "read_until_next={}>").format(self.any_branch_satisfied,
                                              self.read_until_next)

def _parse_preprocessor_define(directive, split_line, defines):
    directive = split_line[0]
    if directive == "#define": # format = #define var_name (value)?
        name = split_line[1]
        try:
            expression = split_line[2]
            calculator = _Calc(defines)
            value = calculator.evaluate(expression)
        except IndexError:
            value = None
        defines[name] = value
    elif directive == "#undef":
        # must be "undef": format =  #undef var_name
        name = split_line[1]
        # remove name from defines if it has been defined.
        defines.pop(name, None)
    else:
        raise ValueError("Unrecognised define directive: {}".format(
            directive))

def _parse_preprocessor_conditional(directive, split_line, defines, if_stack):
    read_elif = False
    if if_stack:
        read_elif = not if_stack[-1].any_branch_satisfied

    if directive == "#if":
        try:
            variable = split_line[1]
        except IndexError:
            raise FLUKAError("Missing expression in preprocessor #if.")
        if variable in defines:
            if_stack.append(_IfInfo(any_branch_satisfied=True,
                                    read_until_next=True))
        else:
            if_stack.append(_IfInfo(any_branch_satisfied=False,
                                    read_until_next=False))
    elif directive == "#elif" and read_elif:
        try:
            variable = split_line[1]
        except IndexError:
            raise FLUKAError("Missing expression in #elif.")
        if variable in defines:
            if_stack[-1].any_branch_satisfied = True
            if_stack[-1].read_until_next = True
    elif directive == "#elif" and not read_elif:
        if_stack[-1].read_until_next = False
    elif directive == "#else" and read_elif:
        if_stack[-1].any_branch_satisfied = True
        if_stack[-1].read_until_next = True
    elif directive == "#else" and read_elif:
        if_stack[-1].read_until_next = True
    elif directive == "#else" and not read_elif:
        if_stack[-1].read_until_next = False
    elif directive == "#endif":
        if_stack.pop()
    else:
        raise ValueError("Unknown conditional directive state.")

def _parse_preprocessor_include(directory, directive, split_line, line_stack):
    if split_line[0] == "#include":
        filename = split_line[1]
        if not os.path.isabs(filename):
            filename = os.path.join(directory, filename)
        try:
            with open(filename, "r") as f:
                line_stack.extend(reversed(f.readlines())) # read in # reverse
        except IOError:
            raise FLUKAError("Included preprocessor file {} not found.".format(
                filename))
    else:
        raise ValueError("Unknown include preprocessor directive: {}".format(
            split_line[1]))

class _Calc(ast.NodeVisitor):

    op_map = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Invert: operator.neg,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos
    }

    def __init__(self, definitions):
        self.definitions = definitions

    def evaluate(self, expression):
        # Switch to python syntax for exponentiation:
        expression = expression.replace("^", "**")
        tree = ast.parse(expression)
        return self.visit(tree.body[0])

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.op_map[type(node.op)](left, right)

    def visit_UnaryOp(self, node):
        op = self.op_map[type(node.op)]
        operand = self.visit(node.operand)
        return op(operand)

    def visit_Num(self, node):
        return node.n

    def visit_Name(self, node):
        name = node.id
        # The precedence may be wrong here.
        # user defines
        try:
            return self.definitions[name]
        except KeyError:
            pass
        # fluka builtin defines
        try:
            return _FLUKA_PREDEFINED_IDS[name]
        except KeyError:
            pass
        # fluka builtin function names
        try:
            return _FLUKA_PREDEFINED_FUNCTIONS[name]
        except KeyError:
            raise FLUKAError("Unknown name in preprocessor define: {}".format(
                name))

    def visit_Call(self, node):
        function = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        return function(*args)

    def visit_Expr(self, node):
        return self.visit(node.value)


if __name__ == '__main__':
    preprocess(sys.argv[1])
