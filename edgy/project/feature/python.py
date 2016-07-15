# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os

from . import ABSOLUTE_PRIORITY, Feature


class PythonFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=ABSOLUTE_PRIORITY)
        self.dispatcher.add_listener('edgy.project.feature.make.on_generate', self.on_make_generate,
                                     priority=ABSOLUTE_PRIORITY)

    def on_make_generate(self, event):
        # Package manager
        event.makefile['PIP'] = '$(VIRTUAL_ENV)/bin/pip'

        # Virtualenv, with external virtual env support.
        event.makefile.add_target('$(VIRTUAL_ENV)', '''
            virtualenv -p $(PYTHON) $(VIRTUAL_ENV)
            $(PIP) install -U pip\>=8.1.2,\<9 wheel\>=0.29,\<1.0
            ln -fs $(VIRTUAL_ENV)/bin/activate activate-$(PYTHON_BASENAME)
        ''', doc='''
            Setup the local virtualenv, or use the one provided by the current environment.
        ''')
        event.makefile.set_deps('install', ('$(VIRTUAL_ENV)',))
        event.makefile.get_target('install').install = [
            '$(PIP) install -Ur $(PYTHON_REQUIREMENTS_FILE)'
        ]

        event.makefile.set_deps('install-dev', ('$(VIRTUAL_ENV)',))
        event.makefile.get_target('install-dev').install = [
            '$(PIP) install -Ur $(PYTHON_REQUIREMENTS_DEV_FILE)'
        ]

        # Python related environment
        event.makefile.updateleft(
            ('PYTHON', '$(shell which python)',),
            ('PYTHON_BASENAME', '$(shell basename $(PYTHON))',),
            ('PYTHON_REQUIREMENTS_FILE', 'requirements.txt',),
            ('PYTHON_REQUIREMENTS_DEV_FILE', 'requirements-dev.txt',),
        )

    def on_start(self, event):
        self.dispatcher.dispatch(__name__ + '.on_generate', event)

        # Some metadata that will prove useful.
        self.render_empty_files('classifiers.txt', 'version.txt', 'README.rst')
        self.render_file_inline('MANIFEST.in', 'include *.txt')
        self.render_file_inline('setup.cfg', '''
                    [metadata]
                    description-file = README.rst
                ''')

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

        for i in range(1, len(package_bits) + 1):
            _bits = package_bits[0:i]
            package_dir = os.path.join(*_bits)
            if not os.path.exists(package_dir):
                os.makedirs(package_dir)

            package_init_file = os.path.join(package_dir, '__init__.py')
            if not os.path.exists(package_init_file):
                self.render_file(package_init_file, 'python/package_init.py.j2',
                                 {'is_namespace': i < len(package_bits)})

        # Render (with overwriting) the allmighty setup.py
        self.render_file('setup.py', 'python/setup.py.j2', {
            'setup': event.setup,
            'url': event.setup.pop('url', 'http://example.com/'),
            'download_url': event.setup.pop('download_url', 'http://example.com/'),
            'extras_require': event.setup.pop('extras_require', {}),
            'install_require': event.setup.pop('install_require', {}),
            'entry_points': event.setup.pop('entry_points', {}),
        }, override=True)


__feature__ = PythonFeature
