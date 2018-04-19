import sys

from medikit.steps.exec import System


class Install(System):
    def __init__(self, *packages):
        if not len(packages):
            packages = ('pip ~=10.0', 'wheel', 'twine')
        packages = list(sorted(packages))
        super().__init__(sys.executable + ' -m pip install --upgrade ' + ' '.join(map(repr, packages)))
        self.__args__ = (*packages, )
