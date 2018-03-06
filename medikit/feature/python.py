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

from pip._vendor.distlib.util import parse_requirement
from pip.req import parse_requirements
from piptools.repositories import PyPIRepository
from piptools.resolver import Resolver
from piptools.scripts.compile import get_pip_command
from piptools.utils import format_requirement

from medikit.events import subscribe
from medikit.feature import Feature, ABSOLUTE_PRIORITY


def _normalize_requirement(req):
    bits = req.requirement.split()
    if req.extras:
        bits = [bits[0] + '[{}]'.format(','.join(req.extras))] + bits[1:]
    return ' '.join(bits)


class PythonConfig(Feature.Config):
    """ Configuration API for the «python» feature. """

    on_generate = __name__ + '.on_generate'

    def __init__(self):
        self._setup = {}
        self._requirements = {None: {}, 'dev': {}}
        self._constraints = {}
        self._version_file = None
        self._create_packages = True

    @property
    def package_dir(self):
        return '/'.join(self.get('name').split('.'))

    @property
    def version_file(self):
        return self._version_file or os.path.join(self.package_dir, '_version.py')

    @version_file.setter
    def version_file(self, value):
        self._version_file = value

    @property
    def create_packages(self):
        return self._create_packages

    @create_packages.setter
    def create_packages(self, value):
        self._create_packages = bool(value)

    def get(self, item):
        if item == 'install_requires':
            return list(self.get_requirements(with_constraints=True))
        if item == 'extras_require':
            return {
                extra: list(self.get_requirements(extra=extra, with_constraints=True))
                for extra in self.get_extras()
            }
        return self._setup.get(item)

    def get_init_files(self):
        # Explode package name so we know which python packages are namespaced and
        # which are not.
        package_bits = self.get('name').split('.')
        if len(package_bits) > 1:
            # XXX SIDE EFFECT !!!
            self['namespace_packages'] = []
            for i in range(1, len(package_bits)):
                self['namespace_packages'].append('.'.join(package_bits[0:i]))

        for i in range(1, len(package_bits) + 1):
            _bits = package_bits[0:i]
            package_dir = os.path.join(*_bits)
            package_init_file = os.path.join(package_dir, '__init__.py')
            is_namespace = i < len(package_bits)
            yield package_dir, package_init_file, {'is_namespace': is_namespace}

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.setup(**{key: value})

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
            yield _normalize_requirement(req)

    def get_requirements(self, extra=None, with_constraints=False):
        if with_constraints:
            yield from self.get_constraints(extra=extra)
        for name, req in sorted(self._requirements[extra].items()):
            yield _normalize_requirement(req)

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

        :param ProjectEvent event:
        """
        self.dispatcher.dispatch(__name__ + '.on_generate', event)

        # Our config object
        python_config = event.config['python']

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

        # XXX there is an important side effect in get_init_files that defines namespace packages for later use in
        # setup.py rendering. Even if we do not want to create the packages here, it is important to make the call
        # anyway.
        for dirname, filename, context in python_config.get_init_files():
            if python_config.create_packages:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                self.render_file(filename, 'python/package_init.py.j2', context)

        # render version file, try to import version from version.txt if available.
        try:
            with open('version.txt') as f:
                version = f.read().strip()
        except IOError:
            version = '0.0.0'
        self.render_file_inline(python_config.version_file, "__version__ = '{}'".format(version))

        setup = python_config.get_setup()

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
                'extras_require': python_config.get('extras_require'),
                'install_requires': python_config.get('install_requires'),
                'python': python_config,
                'setup': setup,
            }
        )

        # Render (with overwriting) the allmighty setup.py
        self.render_file('setup.py', 'python/setup.py.j2', context, override=True)

    @subscribe('medikit.on_end', priority=ABSOLUTE_PRIORITY)
    def on_end(self, event):
        # Our config object
        python_config = event.config['python']

        # Pip / PyPI
        pip_command = get_pip_command()
        pip_options, _ = pip_command.parse_args([])
        session = pip_command._build_session(pip_options)
        repository = PyPIRepository(pip_options, session)

        for extra in itertools.chain((None,), python_config.get_extras()):
            tmpfile = tempfile.NamedTemporaryFile(mode='wt', delete=False)
            if extra:
                tmpfile.write('\n'.join(python_config.get_requirements(extra=extra)))
            else:
                tmpfile.write('\n'.join(python_config.get_requirements()))
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
                        *(('-r requirements.txt',) if extra else ()),
                        *sorted(
                            format_requirement(req) for req in resolver.resolve(max_rounds=10)
                            if req.name != python_config.get('name')
                        ),
                    )
                )
            )


__feature__ = PythonFeature
