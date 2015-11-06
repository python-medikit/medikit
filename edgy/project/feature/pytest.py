from __future__ import absolute_import

from . import Feature


class PytestFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.feature.make.on_generate', self.on_make_generate)

    def on_make_generate(self, event):
        makefile = event.makefile
        makefile['PYTEST_OPTIONS'] = '--reuse-db'
        makefile.add_target('test', '''
            $(VIRTUALENV_PATH)/bin/py.test $(PYTEST_OPTIONS) {name}
        '''.format(name=event.package_name), deps=('install', ), phony=True)


__feature__ = PytestFeature
