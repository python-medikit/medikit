# coding: utf-8
"""
TODO
====

* find a way to automate dependency check ?
  https://blog.dbrgn.ch/2013/4/26/pip-list-outdated/

"""

from __future__ import absolute_import, unicode_literals

import itertools
import os
import tempfile
from getpass import getuser

from pip._vendor.distlib.util import parse_requirement
from pip.req import parse_requirements
from piptools.repositories import PyPIRepository
from piptools.resolver import Resolver
from piptools.scripts.compile import get_pip_command
from piptools.utils import format_requirement

from edgy.project.events import subscribe
from . import ABSOLUTE_PRIORITY, Feature


class PythonFeature(Feature):
    """
    Basic python support for your project. Adds the requirements/requirements-dev logic, virtualenv support, setup.py
    generation, a few metadata files used by setuptools...

    """

    class Config(Feature.Config):
        def __init__(self):
            self._setup = {}
            self._install_requires = {}
            self._extras_require = {}

        def get(self, item):
            if item == 'install_requires':
                return list(self.get_requirements())
            if item == 'extras_require':
                return {extra: list(self.get_requirements(extra=extra)) for extra in sorted(self._extras_require)}
            return self._setup[item]

        def add_requirements(self, *reqs, **kwargs):
            for req in reqs:
                req = parse_requirement(req)
                if req.name in self._install_requires:
                    raise ValueError('duplicate requirement for {}'.format(req.name))
                self._install_requires[req.name] = req

            for extra, reqs in kwargs.items():
                if not extra in self._extras_require:
                    self._extras_require[extra] = {}
                for req in reqs:
                    req = parse_requirement(req)
                    if req.name in self._extras_require[extra]:
                        raise ValueError('duplicate requirement for {}'.format(req.name))
                    self._extras_require[extra][req.name] = req

            return self

        def get_extras(self):
            return self._extras_require.keys()

        def get_requirements(self, extra=None):
            reqs = self._install_requires if extra is None else self._extras_require[extra]
            for req in sorted(reqs):
                yield reqs[req].requirement

        def setup(self, **kwargs):
            self._setup.update(kwargs)
            return self

        def get_setup(self):
            return self._setup

    @subscribe('edgy.project.feature.make.on_generate', priority=ABSOLUTE_PRIORITY)
    def on_make_generate(self, event):
        """
        **Environment variables**

        - ``PACKAGE``
        - ``PYTHON``
        - ``PYTHON_BASENAME``
        - ``PYTHON_DIR``
        - ``PYTHON_REQUIREMENTS_FILE``
        - ``PYTHON_REQUIREMENTS_DEV_FILE``
        
        **Shortcuts**
        - ``PIP``
        - ``PIP_INSTALL_OPTIONS``

        **Make targets**

        - ``install``
        - ``install-dev``

        :param MakefileEvent event:

        """
        # Python related environment
        event.makefile.updateleft(
            ('PACKAGE', event.package_name, ),
            ('PYTHON', '$(shell which python)', ),
            ('PYTHON_BASENAME', '$(shell basename $(PYTHON))', ),
            ('PYTHON_DIRNAME', '$(shell dirname $(PYTHON))', ),
            ('PYTHON_REQUIREMENTS_FILE', 'requirements.txt', ),
            ('PYTHON_REQUIREMENTS_DEV_FILE', 'requirements-dev.txt', ),
        )

        event.makefile['PIP'] = '$(PYTHON_DIRNAME)/pip'
        event.makefile['PIP_INSTALL_OPTIONS'] = ''

        event.makefile.get_target('install').install = [
            '$(PIP) install -U pip wheel $(PYTHON_PIP_INSTALL_OPTIONS) -r $(PYTHON_REQUIREMENTS_FILE)'
        ]

        event.makefile.get_target('install-dev').install = [
            '$(PIP) install -U pip wheel $(PYTHON_PIP_INSTALL_OPTIONS) -r $(PYTHON_REQUIREMENTS_DEV_FILE)'
        ]

    @subscribe('edgy.project.on_start', priority=ABSOLUTE_PRIORITY)
    def on_start(self, event):
        """
        **Events**

        - ``edgy.project.feature.python.on_generate`` (with the same ``ProjectEvent`` we got, todo: why not deprecate
          it in favor of higher priority edgy.project.on_start?)

        **Files**

        - ``<yourpackage>/__init__.py``
        - ``MANIFEST.in``
        - ``README.rst``
        - ``classifiers.txt``
        - ``requirements-dev.txt``
        - ``requirements.txt``
        - ``setup.cfg``
        - ``setup.py`` (overwritten)
        - ``version.txt``

        :param ProjectEvent event:
        """
        self.dispatcher.dispatch(__name__ + '.on_generate', event)

        # Some metadata that will prove useful.
        self.render_empty_files('classifiers.txt', 'README.rst')
        self.render_file_inline('MANIFEST.in', 'include *.txt')
        self.render_file_inline(
            'setup.cfg', '''
                    [bdist_wheel]
                    # This flag says that the code is written to work on both Python 2 and Python
                    # 3. If at all possible, it is good practice to do this. If you cannot, you
                    # will need to generate wheels for each Python version that you support.
                    universal=1
                    
                    [metadata]
                    description-file = README.rst
                '''
        )

        # Explode package name so we know which python packages are namespaced and
        # which are not.
        package_bits = event.setup['name'].split('.')
        if len(package_bits) > 1:
            event.setup['namespace_packages'] = []
            for i in range(1, len(package_bits)):
                # TODO convert to string type (six?) depending on python version
                event.setup['namespace_packages'].append('.'.join(package_bits[0:i]))

        package_dir = None  # useless, but helps showing the scope of this var
        for i in range(1, len(package_bits) + 1):
            _bits = package_bits[0:i]
            package_dir = os.path.join(*_bits)
            if not os.path.exists(package_dir):
                os.makedirs(package_dir)

            package_init_file = os.path.join(package_dir, '__init__.py')
            if not os.path.exists(package_init_file):
                is_namespace = i < len(package_bits)
                self.render_file(package_init_file, 'python/package_init.py.j2', {'is_namespace': is_namespace})

        # render version file, try to import version from version.txt if available.
        try:
            with open('version.txt') as version_file:
                version = version_file.read().strip()
        except IOError:
            version = '0.0.0'
        self.render_file_inline(os.path.join(package_dir, '_version.py'), "__version__ = '{}'".format(version))

        setup = event.config['python'].get_setup()

        context = {
            'url': setup.pop('url', 'http://example.com/'),
            'download_url': setup.pop('download_url', 'http://example.com/'),
        }

        for k, v in context.items():
            context[k] = context[k].format(
                name=setup['name'],
                user=getuser(),
                version='{version}',
            )

        context.update(
            {
                'data_files': setup.pop('data_files', {}),
                'entry_points': setup.pop('entry_points', {}),
                'extras_require': event.config['python'].get('extras_require'),
                'install_requires': event.config['python'].get('install_requires'),
                'setup': setup,
            }
        )

        # Render (with overwriting) the allmighty setup.py
        self.render_file('setup.py', 'python/setup.py.j2', context, override=True)

    @subscribe('edgy.project.on_end', priority=ABSOLUTE_PRIORITY)
    def on_end(self, event):
        pip_command = get_pip_command()
        pip_options, _ = pip_command.parse_args([])
        session = pip_command._build_session(pip_options)
        repository = PyPIRepository(pip_options, session)

        for extra in itertools.chain((None, ), event.config['python'].get_extras()):
            tmpfile = tempfile.NamedTemporaryFile(mode='wt', delete=False)
            if extra:
                tmpfile.write('\n'.join(event.config['python'].get_requirements(extra=extra)))
            else:
                tmpfile.write('\n'.join(event.config['python'].get_requirements()))
            tmpfile.flush()
            constraints = list(
                parse_requirements(
                    tmpfile.name, finder=repository.finder, session=repository.session, options=pip_options
                )
            )
            resolver = Resolver(constraints, repository, prereleases=False, clear_caches=False, allow_unsafe=False)

            self.render_file_inline(
                'requirements{}.txt'.format('-' + extra if extra else ''),
                '\n'.join(
                    (
                        '-e .{}'.format('[' + extra + ']' if extra else ''), *sorted(
                            format_requirement(req) for req in resolver.resolve(max_rounds=10)
                            if req.name != event.config['python'].get('name')
                        ),
                    )
                )
            )


__feature__ = PythonFeature
