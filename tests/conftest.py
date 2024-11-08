import shutil
import uuid
from getpass import getuser
from pathlib import Path
from tempfile import gettempdir
import sys
import os

import pytest
from g4edgetestdata import G4EdgeTestData

_tmptestdir = Path(gettempdir()) / f"pygama-tests-{getuser()}-{uuid.uuid4()!s}"

sys.path.append(os.path.join(os.path.dirname(__file__), "compare/"))
sys.path.append(os.path.join(os.path.dirname(__file__), "features/"))
sys.path.append(os.path.join(os.path.dirname(__file__), "fluka/"))
sys.path.append(os.path.join(os.path.dirname(__file__), "geant4/"))

pytest_plugins = [
    "geant4.test_box",
]


@pytest.fixture(scope="session")
def tmptestdir():
    _tmptestdir.mkdir()
    return _tmptestdir


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0 and _tmptestdir.exists():
        shutil.rmtree(_tmptestdir)


@pytest.fixture(scope="session")
def testdata():
    g4data = G4EdgeTestData()
    g4data.checkout("8bc13ee")
    return g4data
