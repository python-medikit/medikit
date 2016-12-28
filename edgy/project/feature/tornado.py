# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os

from edgy.project.events import subscribe

from . import Feature, SUPPORT_PRIORITY


class TornadoFeature(Feature):
    requires = {'python'}
    conflicts = {'django', 'flask'}

    @subscribe('edgy.project.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile

        makefile.add_target(
            'serve',
            '''
            $(VIRTUAL_ENV)/bin/python -m {name}.app
        '''.format(name=event.package_name),
            deps=('install', ),
            phony=True)

        makefile.add_target(
            'serve-wsgi',
            '''
            $(VIRTUAL_ENV)/bin/python -m {name}.wsgi
        '''.format(name=event.package_name),
            deps=('install', ),
            phony=True)

    @subscribe('edgy.project.on_start', priority=SUPPORT_PRIORITY)
    def on_start(self, event):
        package_path = event.setup['name'].replace('.', os.sep)

        for file in 'app', 'handlers', 'settings', 'wsgi':
            self.render_file(os.path.join(package_path, file + '.py'), os.path.join('tornado', file + '.py.j2'))


__feature__ = TornadoFeature
