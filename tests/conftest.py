import os

import pytest


@pytest.yield_fixture()
def tmpwd(tmpdir):
    old_wd = os.getcwd()
    os.chdir(str(tmpdir))
    yield tmpdir
    os.chdir(old_wd)
