# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.project.events import subscribe

from . import Feature, SUPPORT_PRIORITY


class YapfFeature(Feature):
    requires = {'python'}

    @subscribe('edgy.project.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile
        makefile['YAPF'] = '$(VIRTUAL_ENV)/bin/yapf'
        makefile['YAPF_OPTIONS'] = '-rip'
        makefile.add_target(
            'format', '''
            $(YAPF) $(YAPF_OPTIONS) .
        ''', deps=('install-dev', ), phony=True)

    @subscribe('edgy.project.on_start', priority=SUPPORT_PRIORITY)
    def on_start(self, event):
        self.render_file('.style.yapf', 'yapf/style.yapf.j2')


__feature__ = YapfFeature
