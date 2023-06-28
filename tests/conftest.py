import shutil
import uuid
from getpass import getuser
from pathlib import Path
from tempfile import gettempdir

import pytest
from g4edgetestdata import G4EdgeTestData

_tmptestdir = Path(gettempdir()) / f"pygama-tests-{getuser()}-{uuid.uuid4()!s}"

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
    g4data.checkout("04af6cb")
    return g4data
