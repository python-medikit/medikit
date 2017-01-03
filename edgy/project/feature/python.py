# coding: utf-8
"""
TODO
====

* find a way to automate dependency check ?
  https://blog.dbrgn.ch/2013/4/26/pip-list-outdated/

"""

from __future__ import absolute_import, unicode_literals

import os
from getpass import getuser

from edgy.project.events import subscribe

from . import ABSOLUTE_PRIORITY, Feature


class PythonFeature(Feature):
    """
    Basic python support for your project. Adds the requirements/requirements-dev logic, virtualenv support, setup.py
    generation, a few metadata files used by setuptools...

    """

    @subscribe('edgy.project.feature.make.on_generate', priority=ABSOLUTE_PRIORITY)
    def on_make_generate(self, event):
        """
        **Environment variables**

        - ``PYTHON``
        - ``PYTHON_BASENAME``
        - ``PYTHON_REQUIREMENTS_FILE``
        - ``PYTHON_REQUIREMENTS_DEV_FILE``
        - ``PIP`` (should it be renamed to PYTHON_PIP to match the naming pattern?)

        **Make targets**

        - ``install``
        - ``install-dev``
        - ``$(VIRTUAL_ENV)``: either a local brand new python virtualenv or your currently activated virtualenv.

        :param MakefileEvent event:

        """
        # Python related environment
        event.makefile.updateleft(
            (
                'PYTHON',
                '$(shell which python)',
            ),
            (
                'PYTHON_BASENAME',
                '$(shell basename $(PYTHON))',
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

        # Package manager
        event.makefile['PIP'] = '$(VIRTUAL_ENV)/bin/pip'

        # Virtualenv, with external virtual env support.
        event.makefile.add_target(
            '$(VIRTUAL_ENV)',
            '''
            virtualenv -p $(PYTHON) $(VIRTUAL_ENV)
            $(PIP) install -U pip wheel
            ln -fs $(VIRTUAL_ENV)/bin/activate activate-$(PYTHON_BASENAME)
        ''',
            doc='''
            Setup the local virtualenv, or use the one provided by the current environment.
        '''
        )
        event.makefile.set_deps('install', ('$(VIRTUAL_ENV)', ))
        event.makefile.get_target('install').install = ['$(PIP) install -U pip wheel -r $(PYTHON_REQUIREMENTS_FILE)']

        event.makefile.set_deps('install-dev', ('$(VIRTUAL_ENV)', ))
        event.makefile.get_target('install-dev'
                                  ).install = ['$(PIP) install -U pip wheel -r $(PYTHON_REQUIREMENTS_DEV_FILE)']

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
                    [metadata]
                    description-file = README.rst
                '''
        )

        # If requirements files are missing, let's create em with reasonable defaults.
        self.render_file_inline('requirements.txt', '-e .')
        self.render_file_inline('requirements-dev.txt', '-e .[dev]')

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

        context = {
            'url': event.setup.pop('url', 'http://example.com/'),
            'download_url': event.setup.pop('download_url', 'http://example.com/'),
        }

        for k, v in context.items():
            context[k] = context[k].format(
                name=event.setup['name'],
                user=getuser(),
                version='{version}',
            )

        context.update(
            {
                'data_files': event.setup.pop('data_files', {}),
                'entry_points': event.setup.pop('entry_points', {}),
                'extras_require': event.setup.pop('extras_require', {}),
                'install_require': event.setup.pop('install_require', {}),
                'setup': event.setup,
            }
        )

        # Render (with overwriting) the allmighty setup.py
        self.render_file('setup.py', 'python/setup.py.j2', context, override=True)


__feature__ = PythonFeature
