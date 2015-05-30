import os
from edgy.project.util import format_file_content

from . import Feature

class PythonFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=-99)

    def on_start(self, event):
        # requirements
        with self.file('requirements.txt', override=True) as f:
            f.write(event.files['requirements'])

        self.render_empty_files('classifiers.txt', 'version.txt', 'README.rst')


        # manifest
        with self.file('MANIFEST.in', override=True) as f:
            f.write(format_file_content('''
                include *.txt
            '''))

        # setup.cfg
        with self.file('setup.cfg', override=True) as f:
            f.write(format_file_content('''
                [egg_info]
                tag_build = dev
                tag_svn_revision = true
            '''))

        # Explode package name so we know which python packages are namespaced and
        # which are not
        package_bits = event.setup['name'].split('.')
        if len(package_bits) > 1:
            event.setup['namespace_packages'] = []
            for i in range(len(package_bits))[1:]:
                event.setup['namespace_packages'].append('.'.join(package_bits[0:i]))

        for i in range(len(package_bits)+1)[1:]:
            _bits = package_bits[0:i]
            package_dir = os.path.join(*_bits)
            if not os.path.exists(package_dir):
                os.makedirs(package_dir)

            package_init_file = os.path.join(package_dir, '__init__.py')
            if not os.path.exists(package_init_file):
                self.render_file(package_init_file, 'python/package_init.py.j2', {'is_namespace': i < len(package_bits)})

        self.render_file('setup.py', 'python/setup.py.j2', {'setup': event.setup}, override=True)

__feature__ = PythonFeature
