import pytest
import pyfluka
import pygdml

def test_no_union():
    path = "../test_input/grammar/unions.inp"
    model = pyfluka.Model(path)
    r = model.regions['noUnion']
    sph = pygdml.Orb("", 50)
    intersection = pygdml.Intersection(
        "", sph, sph, [[0.0, 0.0, 0.0],
                       pyfluka.vector.Three([25.,   0.,   0.])])
    region_gdml = r.evaluate(optimise=False).gdml_solid()
    assert pygdml.equal_tree(region_gdml, intersection)

def test_minimal_union():
    path = "../test_input/grammar/unions.inp"
    model = pyfluka.Model(path)
    r = model.regions['minBars']
    sph = pygdml.Orb("", 50)
    union = pygdml.Union(
        "", sph, sph, [[0.0, 0.0, 0.0],
                       pyfluka.vector.Three([25.,   0.,   0.])])
    region_gdml = r.evaluate(optimise=False).gdml_solid()
    assert pygdml.equal_tree(region_gdml, union)


def test_minimal_union2():
    path = "../test_input/grammar/unions.inp"
    model = pyfluka.Model(path)
    r = model.regions['oneExtra']
    sph = pygdml.Orb("", 50)
    union = pygdml.Union(
        "", sph, sph, [[0.0, 0.0, 0.0],
                       pyfluka.vector.Three([25.,   0.,   0.])])
    region_gdml = r.evaluate(optimise=False).gdml_solid()
    assert pygdml.equal_tree(region_gdml, union)
