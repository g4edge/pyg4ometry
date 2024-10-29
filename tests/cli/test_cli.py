import pyg4ometry.cli as _cli

from optparse import OptParseError
import os
import pytest



def _pj(filename):
    """
    Append the absolute path to *this* directory to the filename so the tests
    can be ran from anywhere
    """
    return os.path.join(os.path.dirname(__file__), filename)

def test_cli_help():
    with pytest.raises(OptParseError) as ex:
        _cli.main(["--help"], noExit=True)
    assert ex.type is OptParseError

def test_cli_a(testdata):
    _cli.main(["-i"])



#test_cli_help()