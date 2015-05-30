from __future__ import absolute_import

from . import Feature


class PylintFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.feature.make.on_generate', self.on_make_generate)
        self.dispatcher.add_listener('edgy.project.feature.python.on_generate', self.on_python_generate)

    def on_make_generate(self, event):
        makefile = event.makefile
        makefile.add_target('lint', '''
            $(VIRTUALENV_PATH)/bin/pylint --py3k {name} -f html > pylint.html
        '''.format(name=event.package_name), deps=('install', ), phony=True)

    def on_python_generate(self, event):
        event.files['requirements'] = '\n'.join((event.files['requirements'], 'pylint >=1.4,<1.5', ))


__feature__ = PylintFeature
