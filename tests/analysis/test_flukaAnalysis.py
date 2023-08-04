import pytest

import T001_simple_dump


def test_T001_simple_dump(tmptestdir):
    T001_simple_dump.Test(vis=False, interactive=False, fluka=True, outputPath=tmptestdir)
