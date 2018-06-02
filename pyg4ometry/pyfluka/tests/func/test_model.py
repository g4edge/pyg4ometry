import pytest
import pyfluka

def test_check_overlaps():
    # GIVEN: an input file with overlapping regions
    # RETURN: a dictionary with the names of the regions as keys.
    path = "../test_input/region_overlap.inp"
    model = pyfluka.Model(path)
    overlaps = model.check_overlaps()
    assert {"overlap1", "overlap2"} == set(overlaps.keys())
