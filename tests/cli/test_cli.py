import pyg4ometry.cli as _cli

from optparse import OptParseError
import os
import pytest


def _pj(filename):
    """
    Append the absolute path to *this* directory to the filename so the tests
    can be run from anywhere.
    """
    return os.path.join(os.path.dirname(__file__), filename)


def test_cli_testing():
    # without the testing=True, the cli should call sys.exit() which
    # we should be able to catch here. Effectively, testing the testing.
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        _cli.main(["--help"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 42


def test_cli_help():
    with pytest.raises(OptParseError) as ex:
        _cli.main(["--help"], testing=True)
    assert ex.type is OptParseError


# these are done in the order of the definitions added to the parser object in the main function

def test_cli_analysis_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-a"], testing=True)


def test_cli_analysis_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--analysis"], testing=True)


def test_cli_bounding_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-b"], testing=True)


def test_cli_bounding_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--bounding"], testing=True)


def test_cli_checkoverlaps_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-c"], testing=True)


def test_cli_checkoverlaps_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--checkoverlaps"], testing=True)


def test_cli_clip_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-C"], testing=True)


def test_cli_clip_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--clip"], testing=True)


def test_cli_compare_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-d", testdata["gdml/001_box.gdml"]], testing=True)


def test_cli_compare_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--compare", testdata["gdml/001_box.gdml"]], testing=True)


def test_cli_append_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-e", testdata["gdml/001_box.gdml"]], testing=True)


def test_cli_append_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--append", testdata["gdml/001_box.gdml"]], testing=True)


def test_cli_feature_extract_short(testdata):
    # TODO - change once implememted
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-f", "0"], testing=True)
    assert ex.type is NotImplementedError


def test_cli_feature_extract_long(testdata):
    # TODO - change once implememted
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "--feature", "0"], testing=True)
    assert ex.type is NotImplementedError


# gdml loading is tested in every other example
def test_cli_load_root(testdata):
    _cli.main(["-i", testdata["root/T001_Box.root"]], testing=True)


def test_cli_load_fluka(testdata):
    _cli.main(["-i", testdata["fluka/T001_RPP.inp"]], testing=True)


def test_cli_load_stl(testdata):
    _cli.main(["-i", testdata["stl/dog.stl"]], testing=True)


def test_cli_load_stp(testdata):
    _cli.main(["-i", testdata["step/1_BasicSolids_Bodies.step"]], testing=True)

def test_cli_view_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-v"], testing=True)


def test_cli_view_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--view"], testing=True)


def test_cli_info_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-I", "reg"], testing=True)


def test_cli_info_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--info", "reg"], testing=True)


def test_cli_info_long_tree(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--info", "tree"], testing=True)


def test_cli_info_long_instances(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--info", "instances"], testing=True)


def test_cli_logical_short(testdata):
    _cli.main(["-i", testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"], "-l", "m1_centre_container_lv0x7fc499f3bce0"], testing=True)


def test_cli_logical_long(testdata):
    _cli.main(["-i", testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"], "--logical", "m1_centre_container_lv0x7fc499f3bce0"], testing=True)


def test_cli_materials_short(testdata):
    # TODO - change once implememted
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-m", "Fe"], testing=True)
    assert ex.type is NotImplementedError


def test_cli_materials_long(testdata):
    # TODO - change once implememted
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "--material", "Fe"], testing=True)
    assert ex.type is NotImplementedError