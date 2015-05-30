
import os
from . import Feature

class GitFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=-100)
        self.dispatcher.add_listener('edgy.project.on_file_closed', self.on_file_change)
        self.dispatcher.add_listener('edgy.project.on_end', self.on_end)

    def on_start(self, event):
        if not os.path.exists('.git'):
            os.system('git init')
            os.system('git add Projectfile')
            os.system('git commit -m "initial commit"')

    def on_end(self, event):
        self.render_file_inline('.gitignore', '''
            *.pyc
            *.swp
            /{{ virtualenv_path }}
            /{{ wheelhouse_path }}
            /{{ pipcache_path }}
            /.coverage
            /build
            /dist
            *.egg-info
            /.idea
        ''', event.variables)

    def on_file_change(self, event):
        os.system('git add {}'.format(event.filename))


__feature__ = GitFeature
