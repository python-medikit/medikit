# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os

from . import Feature, ABSOLUTE_PRIORITY


class GitFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=ABSOLUTE_PRIORITY)
        self.dispatcher.add_listener('edgy.project.on_file_closed', self.on_file_change)
        self.dispatcher.add_listener('edgy.project.on_end', self.on_end)

    def on_start(self, event):
        if not os.path.exists('.git'):
            self.dispatcher.echo('git', 'Creating git repository...')
            os.system('git init')
            os.system('git add Projectfile')
            os.system('git commit -m "initial commit"')

    def on_end(self, event):
        self.render_file_inline('.gitignore', '''
            *.egg-info
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

    def on_file_change(self, event):
        os.system('git add {}'.format(event.filename))


__feature__ = GitFeature
