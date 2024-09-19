import numpy as _np
import pytest

import pyg4ometry.mcnp


def test_Plane():
    reg = pyg4ometry.mcnp.Registry()
    p = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    print(p)


def test_PlaneX():
    reg = pyg4ometry.mcnp.Registry()
    px = pyg4ometry.mcnp.PX(1.1, reg=reg)
    print(px)


def test_PlaneY():
    reg = pyg4ometry.mcnp.Registry()
    py = pyg4ometry.mcnp.PY(1.2, reg=reg)
    print(py)


def test_PlaneZ():
    reg = pyg4ometry.mcnp.Registry()
    pz = pyg4ometry.mcnp.PZ(1.3, reg=reg)
    print(pz)


def test_SphereO():
    reg = pyg4ometry.mcnp.Registry()
    so = pyg4ometry.mcnp.SO(1.5, reg=reg)
    print(so)


def test_Sphere():
    reg = pyg4ometry.mcnp.Registry()
    s = pyg4ometry.mcnp.S(1.1, 1.2, 1.3, 1.5, reg=reg)
    print(s)


def test_SphereX():
    reg = pyg4ometry.mcnp.Registry()
    sx = pyg4ometry.mcnp.SX(1.1, 1.5, reg=reg)
    print(sx)


def test_SphereY():
    reg = pyg4ometry.mcnp.Registry()
    sy = pyg4ometry.mcnp.SY(1.2, 1.5, reg=reg)
    print(sy)


def test_SphereZ():
    reg = pyg4ometry.mcnp.Registry()
    sz = pyg4ometry.mcnp.SZ(1.3, 1.5, reg=reg)
    print(sz)


def test_Cylinder_X():
    reg = pyg4ometry.mcnp.Registry()
    c_x = pyg4ometry.mcnp.C_X(1.2, 1.3, 1.5, reg=reg)
    print(c_x)


def test_Cylinder_Y():
    reg = pyg4ometry.mcnp.Registry()
    c_y = pyg4ometry.mcnp.C_Y(1.1, 1.3, 1.5, reg=reg)
    print(c_y)


def test_Cylinder_Z():
    reg = pyg4ometry.mcnp.Registry()
    c_z = pyg4ometry.mcnp.C_Z(1.1, 1.2, 1.5, reg=reg)
    print(c_z)


def test_CylinderX():
    reg = pyg4ometry.mcnp.Registry()
    cx = pyg4ometry.mcnp.CX(1.5, reg=reg)
    print(cx)


def test_CylinderY():
    reg = pyg4ometry.mcnp.Registry()
    cy = pyg4ometry.mcnp.CY(1.5, reg=reg)
    print(cy)


def test_CylinderZ():
    reg = pyg4ometry.mcnp.Registry()
    cz = pyg4ometry.mcnp.CZ(1.5, reg=reg)
    print(cz)
