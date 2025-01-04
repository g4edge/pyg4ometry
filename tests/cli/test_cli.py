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




#test_cli_help()