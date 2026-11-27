import textwrap

import pytest

import pyg4ometry
from pyg4ometry.exceptions import FLUKAError
from pyg4ometry.fluka.preprocessor import preprocess


def _write(tmp_path, text, name="input.inp"):
    path = tmp_path / name
    path.write_text(textwrap.dedent(text))
    return str(path)


def _lines(tmp_path, text, defines=None):
    return preprocess(_write(tmp_path, text), defines=defines)[0]


_IF_ELIF_ELSE = """\
    #if box
    BOX_LINE
    #elif sphere
    SPHERE_LINE
    #else
    ELSE_LINE
    #endif
    """


def test_preprocess_no_defines(tmp_path):
    assert _lines(tmp_path, _IF_ELIF_ELSE) == ["ELSE_LINE"]


def test_preprocess_define_list(tmp_path):
    assert _lines(tmp_path, _IF_ELIF_ELSE, defines=["box"]) == ["BOX_LINE"]
    assert _lines(tmp_path, _IF_ELIF_ELSE, defines=["sphere"]) == ["SPHERE_LINE"]


def test_preprocess_define_single_string(tmp_path):
    assert _lines(tmp_path, _IF_ELIF_ELSE, defines="sphere") == ["SPHERE_LINE"]


def test_preprocess_define_first_branch_wins(tmp_path):
    assert _lines(tmp_path, _IF_ELIF_ELSE, defines=["sphere", "box"]) == ["BOX_LINE"]


def test_preprocess_define_dict_values(tmp_path):
    text = """\
    #if flag
    FLAG_LINE
    #endif
    #define derived width*2
    #if derived
    DERIVED_LINE
    #endif
    """
    defines = {"flag": None, "width": "1.5 + 1.5"}
    assert _lines(tmp_path, text, defines=defines) == ["FLAG_LINE", "DERIVED_LINE"]


def test_preprocess_file_undef_overrides_external(tmp_path):
    text = """\
    #undef box
    #if box
    BOX_LINE
    #else
    ELSE_LINE
    #endif
    """
    assert _lines(tmp_path, text, defines=["box"]) == ["ELSE_LINE"]


def test_preprocess_ifdef_ifndef(tmp_path):
    text = """\
    #ifdef box
    IFDEF_LINE
    #endif
    #ifndef box
    IFNDEF_LINE
    #else
    IFNDEF_ELSE_LINE
    #endif
    """
    assert _lines(tmp_path, text) == ["IFNDEF_LINE"]
    assert _lines(tmp_path, text, defines=["box"]) == ["IFDEF_LINE", "IFNDEF_ELSE_LINE"]


def test_preprocess_nested_with_defines(tmp_path):
    text = """\
    #if outer
    #if inner
    BOTH
    #else
    OUTER_ONLY
    #endif
    #else
    #if inner
    INNER_ONLY
    #endif
    #endif
    """
    assert _lines(tmp_path, text, defines=["outer", "inner"]) == ["BOTH"]
    assert _lines(tmp_path, text, defines=["outer"]) == ["OUTER_ONLY"]
    assert _lines(tmp_path, text, defines=["inner"]) == ["INNER_ONLY"]
    assert _lines(tmp_path, text) == []


def test_preprocess_defines_apply_to_includes(tmp_path):
    _write(tmp_path, _IF_ELIF_ELSE, name="included.inp")
    text = """\
    #include included.inp
    """
    assert _lines(tmp_path, text, defines=["sphere"]) == ["SPHERE_LINE"]


def test_preprocess_if_zero_is_false(tmp_path):
    text = """\
    #if 0
    DISABLED
    #endif
    """
    assert _lines(tmp_path, text) == []


@pytest.mark.parametrize("bad", [[""], ["two words"], [1], {"": None}])
def test_preprocess_invalid_define_name(tmp_path, bad):
    with pytest.raises(FLUKAError):
        _lines(tmp_path, _IF_ELIF_ELSE, defines=bad)


@pytest.mark.parametrize("directive", ["#elif box", "#else", "#endif"])
def test_preprocess_unmatched_conditional(tmp_path, directive):
    with pytest.raises(FLUKAError):
        _lines(tmp_path, directive + "\n")


_GEOMETRY = """\
    TITLE
    preprocessor defines test
    GEOBEGIN                                                              COMBNAME
        0    0
    SPH blkbody    0.0 0.0 0.0 1000.0
    SPH void       0.0 0.0 0.0 100.0
    #if box
    RPP target     -10.0 10.0 -10.0 10.0 -10.0 10.0
    #else
    SPH target     0.0 0.0 0.0 10.0
    #endif
    END
    BLKHOLE      5 +blkbody -void
    VOID         5 +void -target
    TARGET       5 +target
    END
    GEOEND
    ASSIGNMA    BLCKHOLE   BLKHOLE
    ASSIGNMA      VACUUM      VOID
    ASSIGNMA      COPPER    TARGET
    STOP
    """


def test_reader_defines(tmp_path):
    filename = _write(tmp_path, _GEOMETRY)

    default = pyg4ometry.fluka.Reader(filename).getRegistry()
    assert type(default.bodyDict["target"]).__name__ == "SPH"

    with_box = pyg4ometry.fluka.Reader(filename, defines=["box"]).getRegistry()
    assert type(with_box.bodyDict["target"]).__name__ == "RPP"


def test_preprocess_dollar_substitution(tmp_path):
    text = """\
    #define L 1
    #define LmXC 715
    #define coil 8.2
    #define half coil/2
    #define flag
    XYP zu1    -$LmXC
    XYP zd1    $LmXC
    ZCC c1     $coil $coil $half
    RPP r1     -$L $L 0 $L 0 1
    RPP f1     $flag $missing $Lx
    """
    lines = _lines(tmp_path, text)
    assert [line.split() for line in lines] == [
        ["XYP", "zu1", "-715"],
        ["XYP", "zd1", "715"],
        ["ZCC", "c1", "8.2", "8.2", "4.1"],
        ["RPP", "r1", "-1", "1", "0", "1", "0", "1"],
        ["RPP", "f1", "$flag", "$missing", "$Lx"],
    ]


def test_preprocess_dollar_substitution_keeps_fixed_format_columns(tmp_path):
    # values are right-aligned to where the $name token ended
    text = """\
    #define w -.235482
    #define n 2
    BEAM             1.0                         $w        $n              PROTON
    """
    original = textwrap.dedent(text).splitlines()[2]
    (line,) = _lines(tmp_path, text)
    assert line.split() == ["BEAM", "1.0", "-0.235482", "2", "PROTON"]
    assert line.index("-0.235482") + len("-0.235482") == original.index("$w") + len("$w")
    assert line.index(" 2 ") + 2 == original.index("$n") + len("$n")
    assert line.index("PROTON") == original.index("PROTON")


def test_preprocess_dollar_substitution_keeps_a_separator(tmp_path):
    text = """\
    #define c 12.5
    ZCC x $c $c 1
    """
    assert _lines(tmp_path, text)[0].split() == ["ZCC", "x", "12.5", "12.5", "1"]


def test_preprocess_dollar_substitution_external_defines(tmp_path):
    text = """\
    XYP z1    $zpos
    """
    assert _lines(tmp_path, text, defines={"zpos": "Sqrt(4) * 10"})[0].split() == ["XYP", "z1", "20.0"]
    assert _lines(tmp_path, text, defines={"zpos": 3})[0].split() == ["XYP", "z1", "3"]
