# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os

from edgy.project.events import subscribe

from . import ABSOLUTE_PRIORITY, Feature


class GitFeature(Feature):
    @subscribe('edgy.project.on_start', priority=ABSOLUTE_PRIORITY)
    def on_start(self, event):
        if not os.path.exists('.git'):
            self.dispatcher.info('git', 'Creating git repository...')
            os.system('git init')
            os.system('git add Projectfile')
            os.system('git commit -m "initial commit"')

    @subscribe('edgy.project.on_end')
    def on_end(self, event):
        self.render_file_inline('.gitignore', '''
            *.egg-info
            *.iml
            *.pyc
            *.swp
            /.cache
            /.coverage
            /.idea
            /.python*-*
            /build
            /dist
            /htmlcov
            /pylint.html
        ''', event.variables)

    @subscribe('edgy.project.on_file_closed')
    def on_file_change(self, event):
        os.system('git add {}'.format(event.filename))


__feature__ = GitFeature
