import os

import pytest


@pytest.yield_fixture()
def tmpwd(tmpdir):
    old_wd = os.getcwd()
    try:
        os.chdir(str(tmpdir))
        yield tmpdir
    finally:
        os.chdir(old_wd)
