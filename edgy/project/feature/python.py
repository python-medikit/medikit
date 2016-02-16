# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os

from . import Feature, ABSOLUTE_PRIORITY


class PythonFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=ABSOLUTE_PRIORITY)

    def on_start(self, event):
        self.dispatcher.dispatch(__name__ + '.on_generate', event)

        self.render_empty_files('classifiers.txt', 'version.txt', 'README.rst')
        self.render_file_inline('MANIFEST.in', 'include *.txt')
        self.render_file_inline('setup.cfg', '''
                [metadata]
                description-file = README.rst
            ''')

        # Explode package name so we know which python packages are namespaced and
        # which are not
        package_bits = event.setup['name'].split('.')
        if len(package_bits) > 1:
            event.setup['namespace_packages'] = []
            for i in range(1, len(package_bits)):
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

        self.render_file('setup.py', 'python/setup.py.j2', {
            'setup': event.setup,
            'url': event.setup.pop('url', 'http://example.com/'),
            'download_url': event.setup.pop('download_url', 'http://example.com/'),
            'extras_require': event.setup.pop('extras_require', {}),
            'install_require': event.setup.pop('install_require', {}),
            'entry_points': event.setup.pop('entry_points', {}),
        }, override=True)


__feature__ = PythonFeature
