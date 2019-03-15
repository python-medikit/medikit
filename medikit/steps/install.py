import sys

from medikit.globals import PIP_VERSION
from medikit.steps.exec import System


class Install(System):
    def __init__(self, *packages):
        if not len(packages):
            packages = ("pip " + PIP_VERSION, "wheel", "twine")
        packages = list(sorted(packages))
        super().__init__(sys.executable + " -m pip install --upgrade " + " ".join(map(repr, packages)))
        self.__args__ = (*packages,)
