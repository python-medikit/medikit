from __future__ import absolute_import

from . import Feature


class Flake8Feature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.feature.make.on_generate', self.on_make_generate, priority=-10)

    def on_make_generate(self, event):
        makefile = event.makefile
        makefile.add_target('lint', '''
            $(VIRTUAL_ENV)/bin/flake8 {name}
        '''.format(name=event.package_name), deps=('install', ), phony=True)


__feature__ = Flake8Feature
