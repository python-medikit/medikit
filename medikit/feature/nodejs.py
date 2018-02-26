"""
NodeJS / Yarn support.

"""

import json
import os
import runpy

from medikit.events import subscribe
from medikit.feature import Feature, LAST_PRIORITY
from medikit.steps.version import PythonVersion


class NodeJSConfig(Feature.Config):
    """ Configuration API for the «nodejs» feature. """

    def __init__(self):
        self._setup = {}
        self._dependencies = {
            None: {},
            'dev': {},
            'peer': {},
            'bundled': {},
            'optional': {},
        }
        self.base_dir = None

    def setup(self, *, base_dir=None):
        if base_dir:
            self.base_dir = base_dir
        return self

    def add_dependencies(self, deps=None, **kwargs):
        if deps:
            self.__add_dependencies(deps)
        for deptype, deps in kwargs.items():
            self.__add_dependencies(deps, deptype=deptype)
        return self

    def get_dependencies(self):
        return {
            deptype + 'Dependencies' if deptype else 'dependencies': deps
            for deptype, deps in self._dependencies.items() if len(deps)
        }

    def __add_dependencies(self, deps, deptype=None):
        if len(deps):
            if deptype not in self._dependencies:
                raise KeyError('Invalid dependency type ' + deptype)
        self._dependencies[deptype].update(deps)


class NodeJSFeature(Feature):
    requires = {'python', 'make'}

    Config = NodeJSConfig

    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile['YARN'] = '$(shell which yarn)'
        event.makefile['NODE'] = '$(shell which node)'

        event.makefile.get_target('install').install += [
            '$(YARN) install --production',
        ]

        event.makefile.get_target('install-dev').install += [
            '$(YARN) install',
        ]

    @subscribe('medikit.on_start')
    def on_start(self, event):
        name = event.config['python'].get('name')

        current_version = PythonVersion.coerce(
            runpy.run_path(event.config['python'].version_file).get('__version__'), partial=True
        )
        current_version.partial = False

        package = {
            'name': name,
            'version': str(current_version),
            'description': event.config['python'].get('description'),
            'author': event.config['python'].get('author'),
            'license': event.config['python'].get('license'),
            **event.config['nodejs'].get_dependencies()
        }

        base_dir = event.config['nodejs'].base_dir or '.'

        self.render_file_inline(
            os.path.join(base_dir, 'package.json'),
            json.dumps(package, sort_keys=True, indent=4),
            override=True,
        )

    @subscribe('medikit.on_end', priority=LAST_PRIORITY)
    def on_end(self, event):
        base_dir = event.config['nodejs'].base_dir or '.'
        os.system('cd {base_dir}; yarn install'.format(base_dir=base_dir))
        os.system('cd {base_dir}; git add yarn.lock'.format(base_dir=base_dir))


__feature__ = NodeJSFeature
