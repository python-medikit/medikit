"""
NodeJS / Yarn support.

"""

import json
import os

from medikit.events import subscribe
from medikit.feature import Feature, LAST_PRIORITY


class NodeJSFeature(Feature):
    requires = {'python', 'make'}

    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile['YARN'] = '$(shell which yarn)'
        event.makefile['NODE'] = '$(shell which node)'

        event.makefile.get_target('install').install += [
            '$(YARN) install --production',
        ]

        event.makefile.get_target('install-dev').install += [
            '$(YARN) install',
        ]

    @subscribe('medikit.on_start')
    def on_start(self, event):
        package = {
            'name': event.config['python'].get('name'),
            'version': '0.0.0',
            'description': event.config['python'].get('description'),
            'author': event.config['python'].get('author'),
            'license': event.config['python'].get('license'),
        }

        self.render_file_inline(
            'package.json',
            json.dumps(package),
        )

    @subscribe('medikit.on_end', priority=LAST_PRIORITY)
    def on_end(self, event):
        os.system('yarn install')
        os.system('git add yarn.lock')


__feature__ = NodeJSFeature
