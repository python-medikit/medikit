# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import os

from edgy.project import settings
from edgy.project.events import subscribe

from . import Feature, SUPPORT_PRIORITY, ABSOLUTE_PRIORITY


class YapfFeature(Feature):
    requires = {'python'}

    @subscribe('edgy.project.feature.python.on_generate')
    def on_python_generate(self, event):
        if not 'extras_require' in event.setup:
            event.setup['extras_require'] = {}

        if not 'dev' in event.setup['extras_require']:
            event.setup['extras_require']['dev'] = []

        event.setup['extras_require']['dev'].append('yapf')

    @subscribe('edgy.project.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile
        makefile['YAPF'] = '$(PYTHON) -m yapf'
        makefile['YAPF_OPTIONS'] = '-rip'
        makefile.add_target(
            'format',
            '''
            $(YAPF) $(YAPF_OPTIONS) .
            $(YAPF) $(YAPF_OPTIONS) Projectfile
        ''',
            deps=('install-dev', ),
            phony=True
        )

    @subscribe('edgy.project.on_start', priority=SUPPORT_PRIORITY)
    def on_start(self, event):
        self.render_file('.style.yapf', 'yapf/style.yapf.j2')

    @subscribe('edgy.project.on_start', priority=ABSOLUTE_PRIORITY - 1)
    def on_before_start(self, event):
        style_config = os.path.join(os.getcwd(), '.style.yapf')
        if os.path.exists(style_config):
            self.dispatcher.info('YAPF_STYLE_CONFIG = ' + style_config)
            settings.YAPF_STYLE_CONFIG = style_config


__feature__ = YapfFeature
