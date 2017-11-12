"""
The «python» feature contains all the base logic associated to managing python package.

Overview
::::::::

.. code-block:: python

    from medikit import require

    # load python feature (idempotent).
    python = require('python')

    # configure our package.
    python.setup(
        name = 'awesome-library',
        author = 'Chuck Norris',
    )

    # add base and extras requirements, with "loose" versionning (the frozen version fits better in requirements*.txt)
    python.add_requirements(
        'django',
        dev=[
            'pytest',
        ],
    )

"""

import itertools
import os
import tempfile
from getpass import getuser

from medikit.events import subscribe
from medikit.feature import Feature, ABSOLUTE_PRIORITY
from pip._vendor.distlib.util import parse_requirement
from pip.req import parse_requirements
from piptools.repositories import PyPIRepository
from piptools.resolver import Resolver
from piptools.scripts.compile import get_pip_command
from piptools.utils import format_requirement


class PythonConfig(Feature.Config):
    """ Configuration API for the «python» feature. """

    def __init__(self):
        self._setup = {}
        self._requirements = {None: {}, 'dev': {}}
        self._constraints = {}

    def get(self, item):
        if item == 'install_requires':
            return list(self.get_requirements(with_constraints=True))
        if item == 'extras_require':
            return {
                extra: list(self.get_requirements(extra=extra, with_constraints=True))
                for extra in self.get_extras()
            }
        return self._setup[item]

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.setup(key=value)

    def __contains__(self, item):
        return bool(self.get(item))

    def add_constraints(self, *reqs, **kwargs):
        self.__add_constraints(reqs)
        for extra, reqs in kwargs.items():
            self.__add_constraints(reqs, extra=extra)
        return self

    def add_requirements(self, *reqs, **kwargs):
        self.__add_requirements(reqs)
        for extra, reqs in kwargs.items():
            self.__add_requirements(reqs, extra=extra)
        return self

    def get_extras(self):
        return sorted(filter(None, self._requirements.keys()))

    def get_constraints(self, extra=None):
        for name, req in sorted(self._constraints.get(extra, {}).items()):
            yield req.requirement

    def get_requirements(self, extra=None, with_constraints=False):
        if with_constraints:
            yield from self.get_constraints(extra=extra)
        for name, req in sorted(self._requirements[extra].items()):
            yield req.requirement

    def setup(self, **kwargs):
        self._setup.update(kwargs)
        return self

    def get_setup(self):
        return self._setup

    def __add_constraints(self, reqs, extra=None):
        if len(reqs):
            if extra not in self._constraints:
                self._constraints[extra] = {}
        for req in reqs:
            req = parse_requirement(req)
            if req.name in self._constraints[extra]:
                raise ValueError('Duplicate constraint for {}.'.format(req.name))
            self._constraints[extra][req.name] = req

    def __add_requirements(self, reqs, extra=None):
        if len(reqs):
            if extra not in self._requirements:
                self._requirements[extra] = {}
        for req in reqs:
            req = parse_requirement(req)
            if req.name in self._requirements[extra]:
                raise ValueError('Duplicate requirement for {}.'.format(req.name))
            self._requirements[extra][req.name] = req


class PythonFeature(Feature):
    """
    Adds the requirements/requirements-dev logic, virtualenv support, setup.py generation, a few metadata files used by
    setuptools...

    """

    requires = {'make'}

    Config = PythonConfig

    @subscribe('medikit.feature.make.on_generate', priority=ABSOLUTE_PRIORITY)
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
            (
                'PACKAGE',
                event.package_name,
            ),
            (
                'PYTHON',
                '$(shell which python)',
            ),
            (
                'PYTHON_BASENAME',
                '$(shell basename $(PYTHON))',
            ),
            (
                'PYTHON_DIRNAME',
                '$(shell dirname $(PYTHON))',
            ),
            (
                'PYTHON_REQUIREMENTS_FILE',
                'requirements.txt',
            ),
            (
                'PYTHON_REQUIREMENTS_DEV_FILE',
                'requirements-dev.txt',
            ),
        )

        event.makefile['PIP'] = '$(PYTHON_DIRNAME)/pip'
        event.makefile['PIP_INSTALL_OPTIONS'] = ''

        event.makefile.get_target('install').install = [
            '$(PIP) install -U pip wheel $(PIP_INSTALL_OPTIONS) -r $(PYTHON_REQUIREMENTS_FILE)'
        ]

        event.makefile.get_target('install-dev').install = [
            '$(PIP) install -U pip wheel $(PIP_INSTALL_OPTIONS) -r $(PYTHON_REQUIREMENTS_DEV_FILE)'
        ]

    @subscribe('medikit.on_start', priority=ABSOLUTE_PRIORITY)
    def on_start(self, event):
        """
        **Events**

        - ``medikit.feature.python.on_generate`` (with the same ``ProjectEvent`` we got, todo: why not deprecate
          it in favor of higher priority medikit.on_start?)

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
        package_bits = event.config['python'].get('name').split('.')
        if len(package_bits) > 1:
            event.config['python']['namespace_packages'] = []
            for i in range(1, len(package_bits)):
                event.config['python']['namespace_packages'].append('.'.join(package_bits[0:i]))

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
                'entry_points': setup.pop('entry_points', {}),
                'extras_require': event.config['python'].get('extras_require'),
                'install_requires': event.config['python'].get('install_requires'),
                'setup': setup,
            }
        )

        # Render (with overwriting) the allmighty setup.py
        self.render_file('setup.py', 'python/setup.py.j2', context, override=True)

    @subscribe('medikit.on_end', priority=ABSOLUTE_PRIORITY)
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
                        '-e .{}'.format('[' + extra + ']' if extra else ''),
                        *sorted(
                            format_requirement(req) for req in resolver.resolve(max_rounds=10)
                            if req.name != event.config['python'].get('name')
                        ),
                    )
                )
            )


__feature__ = PythonFeature
