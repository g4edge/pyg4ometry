import numpy as _np
import pytest

import pyg4ometry.mcnp


def test_Cell_addSurfaces_constrcutor():
    reg = pyg4ometry.mcnp.Registry()
    p1 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p2 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p3 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p4 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p5 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p6 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    c1 = pyg4ometry.mcnp.Cell([p1, p2, p3, p4, p5, p6], reg=reg)


def test_Cell_addSurface():
    reg = pyg4ometry.mcnp.Registry()
    p1 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p2 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p3 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p4 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p5 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p6 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    c1 = pyg4ometry.mcnp.Cell(reg=reg)
    c1.addSurface(p1)
    c1.addSurface(p2)
    c1.addSurface(p3)
    c1.addSurface(p4)
    c1.addSurface(p5)
    c1.addSurface(p6)


def test_Cell_addSurfaces():
    reg = pyg4ometry.mcnp.Registry()
    p1 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p2 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p3 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p4 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p5 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    p6 = pyg4ometry.mcnp.P(1.1, 1.2, 1.3, 1.4, reg=reg)
    c1 = pyg4ometry.mcnp.Cell(reg=reg)
    c1.addSurfaces([p1, p2, p3, p4, p5, p6])
