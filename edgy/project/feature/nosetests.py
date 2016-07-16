# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from . import Feature, SUPPORT_PRIORITY


class NosetestsFeature(Feature):
    requires = {'python'}
    conflicts = {'pytest'}

    def configure(self):
        self.dispatcher.add_listener(
            'edgy.project.feature.make.on_generate', self.on_make_generate, priority=SUPPORT_PRIORITY
        )
        self.dispatcher.add_listener(
            'edgy.project.feature.python.on_generate', self.on_python_generate, priority=SUPPORT_PRIORITY
        )

    def on_make_generate(self, event):
        makefile = event.makefile
        makefile.add_target('test', '''
            $(VIRTUAL_ENV)/bin/nosetests -q --with-doctest --with-coverage --cover-package={name}
        '''.format(name=event.package_name), deps=('install-dev',), phony=True)

    def on_python_generate(self, event):
        event.files['requirements'] = '\n'.join((event.files['requirements'], 'nose >=1.3,<1.4', 'coverage >=3.7,<3.8'))


__feature__ = NosetestsFeature
