import pytest
import pyfluka

def test_get_overlap_overlap():
    path = "../test_input/region_overlap.inp"
    model = pyfluka.Model(path)

    # GIVEN: a pair of overlapping regions
    # RETURN: the extent of that overlap
    overlap1 = model.regions['overlap1']
    overlap2 = model.regions['overlap2']
    overlap = pyfluka.geometry.get_overlap(overlap1, overlap2)
    expected = pyfluka.geometry.Extent([-2.5, -5., -5.],
                                       [2.5, 5., 5.])
    assert overlap == expected

def test_get_overlap_no_overlap():
    path = "../test_input/region_overlap.inp"
    model = pyfluka.Model(path)
    # GIVEN: a pair of regions which do not overlap
    # RETURN: None
    no_overlap1 = model.regions['no_overlap1']
    no_overlap2 = model.regions['no_overlap2']
    assert pyfluka.geometry.get_overlap(no_overlap1, no_overlap2) is None

def test_connected_zones():
    path = "../test_input/connected_zones.inp"
    model = pyfluka.Model(path)
    region = model.regions['region']
    assert list(region.connected_zones()) == [{0, 1, 2, 3}, {4, 5}, {6}]

def test_write_with_connected_zones_and_zone_map():
    path = "../test_input/connected_zones.inp"
    model = pyfluka.Model(path)
    survey = model.survey()
    # Specifically testing the scenario where you provide both a zone
    # dictionary and a survey.
    model.write_to_gdml(survey=survey, regions={"region": range(6)})

# def test_length_safety_for_single_body_region():
#     path = "../test_input/sphere.inp"
#     model = pyfluka.Model(path)
#     # GIVEN: a region which in which 0 and 1 are not disjoint but 2 is
#     # disjoint with both 0 and 1:
#     region = model.regions['sphere']
#     gdml = region.evaluate().gdml_solid()
#     gdml_trimmed = region.evaluate().gdml_solid(length_safety="trim")
#     assert gdml.pRMax == gdml_trimmed.pRMax + pyfluka.geometry.LENGTH_SAFETY
