"""
Git version control system support.

"""

import os

from medikit.events import subscribe
from medikit.feature import ABSOLUTE_PRIORITY, Feature


class GitConfig(Feature.Config):
    def __init__(self):
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True


class GitFeature(Feature):
    Config = GitConfig

    @subscribe('medikit.on_start', priority=ABSOLUTE_PRIORITY)
    def on_start(self, event):
        if not event.config['git'].enabled:
            return

        if not os.path.exists('.git'):
            self.dispatcher.info('git', 'Creating git repository...')
            os.system('git init')
            os.system('git add Projectfile')
            os.system('git commit -m "Project initialized using Medikit."')

        def on_file_change(event):
            os.system('git add {}'.format(event.filename))

        self.dispatcher.add_listener('medikit.on_file_closed', on_file_change, priority=-1)

    @subscribe('medikit.on_end')
    def on_end(self, event):
        self.render_file_inline(
            '.gitignore', '''
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
        ''', event.variables
        )

    @subscribe('medikit.feature.make.on_generate', priority=ABSOLUTE_PRIORITY + 1)
    def on_make_generate(self, event):
        event.makefile['VERSION'] = "$(shell git describe 2>/dev/null || git rev-parse --short HEAD)"
