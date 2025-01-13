import pyg4ometry.cli as _cli

from optparse import OptParseError
import os
import pytest
import sys

_skip_root_tests = False
try:
    import ROOT
except ImportError:
    _skip_root_tests = True

_skip_html_tests = False
try:
    import jinja2
except ImportError:
    _skip_html_tests = True


def _pj(filename):
    """
    Append the absolute path to *this* directory to the filename so the tests
    can be run from anywhere.
    """
    return os.path.join(os.path.dirname(__file__), filename)


def test_cli_testing():
    # without the testing=True, the cli should call sys.exit() which
    # we should be able to catch here. Effectively, testing the testing.
    with pytest.raises(SystemExit) as ex:
        _cli.main(["--help"])
    assert ex.type == SystemExit
    assert ex.value.code == 0


def test_cli_help_short():
    with pytest.raises(OptParseError) as ex:
        _cli.main(["--h"], testing=True)
    assert ex.type is OptParseError


def test_cli_help_long():
    with pytest.raises(OptParseError) as ex:
        _cli.main(["--help"], testing=True)
    assert ex.type is OptParseError


# these are done in the order of the definitions added to the parser object in the main function


def test_cli_no_input():
    with pytest.raises(SystemExit) as ex:
        _cli.main([], testing=True)
    assert ex.type == SystemExit
    assert ex.value.code == 1


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
    _cli.main(
        ["-i", testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"], "-C", "50,70,200"],
        testing=True,
    )


def test_cli_clip_long(testdata):
    _cli.main(
        ["-i", testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"], "--clip", "50,70,200"],
        testing=True,
    )


def test_cli_clip_short_rot_tra(testdata):
    _cli.main(
        [
            "-i",
            testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"],
            "-C",
            "50,70,200",
            "-r",
            "0,pi/6,0",
            "-t",
            "0,0,100",
            "-V",
        ],
        testing=True,
    )


def test_cli_clip_short_rot_tra_long(testdata):
    _cli.main(
        [
            "-i",
            testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"],
            "-C",
            "50,70,200",
            "--rotation",
            "0.001,-pi/6,0.0002",
            "--translation",
            "0,-20,-100",
            "-V",
        ],
        testing=True,
    )


def test_cli_compare_short(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "-d", testdata["gdml/001_box.gdml"]], testing=True
    )


def test_cli_compare_long(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "--compare", testdata["gdml/001_box.gdml"]],
        testing=True,
    )


def test_cli_append_short(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "-e", testdata["gdml/001_box.gdml"]], testing=True
    )


def test_cli_append_long(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "--append", testdata["gdml/001_box.gdml"]],
        testing=True,
    )


def test_cli_feature_extract_short(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-f", "0"], testing=True)
    assert ex.type is NotImplementedError


def test_cli_feature_extract_long(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "--feature", "0"], testing=True)
    assert ex.type is NotImplementedError


# gdml loading is tested in every other example
@pytest.mark.skipif(_skip_root_tests, reason="requires ROOT to run")
def test_cli_load_root(testdata):
    _cli.main(["-i", testdata["root/T001_Box.root"]], testing=True)


def test_cli_load_bad_file_type(testdata):
    # we need a file that definitely exists (in the testdata), but isn't one we can load
    with pytest.raises(OSError, match="unknown format:") as ex:
        _cli.main(["-i", testdata["fluka/preprocessor_fragment.geom"]], testing=True)
    assert ex.type == OSError


def test_cli_load_file_not_found():
    with pytest.raises(FileNotFoundError, match="pyg4> input file") as ex:
        _cli.main(["-i", "bananas.gdml"], testing=True)
    assert ex.type == FileNotFoundError


def test_cli_load_fluka(testdata):
    _cli.main(["-i", testdata["fluka/T001_RPP.inp"]], testing=True)


def test_cli_load_stl(testdata):
    _cli.main(["-i", testdata["stl/dog.stl"]], testing=True)


@pytest.mark.skipif(sys.platform == "linux", reason="Test not supported on Linux")
def test_cli_load_stp(testdata):
    _cli.main(["-i", testdata["step/1_BasicSolids_Bodies.step"]], testing=True)


def test_cli_load_g4edgetestdata():
    _cli.main(["-i", "g4edgetestdata/gdml/001_box.gdml"], testing=True)


def test_cli_info_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-I", "reg"], testing=True)


def test_cli_info_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--info", "reg"], testing=True)


def test_cli_info_long_tree(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--info", "tree"], testing=True)


def test_cli_info_long_instances(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--info", "instances"], testing=True)


def test_cli_logical_short(testdata):
    _cli.main(
        [
            "-i",
            testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"],
            "-l",
            "m1_centre_container_lv0x7fc499f3bce0",
        ],
        testing=True,
    )


def test_cli_logical_long(testdata):
    _cli.main(
        [
            "-i",
            testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"],
            "--logical",
            "m1_centre_container_lv0x7fc499f3bce0",
        ],
        testing=True,
    )


def test_cli_materials_short(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-m", "Fe"], testing=True)
    assert ex.type is NotImplementedError


def test_cli_materials_long(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "--material", "Fe"], testing=True)
    assert ex.type is NotImplementedError


def test_cli_nullmesh_exception_short(testdata):
    _cli.main(["-i", testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"], "-n"], testing=True)


def test_cli_nullmesh_exception_long(testdata):
    _cli.main(
        ["-i", testdata["gdml/CompoundExamples/bdsim/vkickers.gdml"], "--nullmesh"], testing=True
    )


def test_cli_output_short_gl(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-o", "o.gl"], testing=True)


@pytest.mark.skipif(_skip_html_tests, reason="requires jinja2 to run")
def test_cli_output_short_html(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-o", "o.html"], testing=True)


def test_cli_output_short_gdml(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-o", "o.gdml"], testing=True)


def test_cli_output_long_gdml(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--output", "o.gdml"], testing=True)


def test_cli_output_short_inp(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-o", "o.inp"], testing=True)


def test_cli_output_short_usd(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-o", "o.usd"], testing=True)
    assert ex.type is NotImplementedError


def test_cli_output_short_wrong(testdata):
    with pytest.raises(OSError, match="unknown format:") as ex:
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-o", "o.rarara"], testing=True)
    assert ex.type is OSError


def test_cli_planecutter_short(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "-p", "0,0,0,0,1,0", "-P", "o.vtkp", "-V"],
        testing=True,
    )


def test_cli_planecutter_long(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "--planeCutter", "0,0,0,0,1,0", "-P", "o.vtkp"],
        testing=True,
    )


def test_cli_planecutter_long2(testdata):
    _cli.main(
        [
            "-i",
            testdata["gdml/001_box.gdml"],
            "--planeCutter",
            "0,0,0,0,1,0",
            "--planeCutterOutput",
            "box_cut.vtkp",
        ],
        testing=True,
    )


def test_cli_planecutter_short_wrong(testdata):
    with pytest.raises(ValueError, match="pyg4> must specify -P or --planeCutterOutput file") as ex:
        # no -P given for output - should complain
        _cli.main(["-i", testdata["gdml/001_box.gdml"], "-p", "0,0,0,0,1,0", "-V"], testing=True)
    assert ex.type is ValueError


def test_cli_solid_substitution_short_gdml(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(
            ["-i", testdata["gdml/001_box.gdml"], "-s", "Box,px=10,py=20,pz=30", "-x", "box1Vol"],
            testing=True,
        )
    assert ex.type is NotImplementedError


def test_cli_solid_substitution_long_gdml(testdata):
    # TODO - change once implemented
    with pytest.raises(NotImplementedError) as ex:
        _cli.main(
            [
                "-i",
                testdata["gdml/001_box.gdml"],
                "--solid",
                "Box,px=10,py=20,pz=30",
                "-x",
                "box1Vol",
                "-V",
            ],
            testing=True,
        )
    assert ex.type is NotImplementedError


def test_cli_gltf_scale_short(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "-S", "1000.0", "-o", "o_scaled.gl"], testing=True
    )


def test_cli_gltf_scale_long(testdata):
    _cli.main(
        ["-i", testdata["gdml/001_box.gdml"], "--gltfScale", "1000.0", "-o", "o_scaled.gl"],
        testing=True,
    )


def test_cli_view_short(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "-v"], testing=True)


def test_cli_view_long(testdata):
    _cli.main(["-i", testdata["gdml/001_box.gdml"], "--view"], testing=True)


def test_cli_citation_short(testdata):
    with pytest.raises(SystemExit) as ex:
        _cli.main(["-z"], testing=True)
    assert ex.type is SystemExit
    assert ex.value.code == 0


def test_cli_citation_long(testdata):
    with pytest.raises(SystemExit) as ex:
        _cli.main(["--citation"], testing=True)
    assert ex.type is SystemExit
    assert ex.value.code == 0


# for debugging in pycharm
# import g4edgetestdata
# d = g4edgetestdata.G4EdgeTestData()
# test_cli_materials_long(d)
