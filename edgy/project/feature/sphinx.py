# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.project.events import subscribe

from . import Feature, SUPPORT_PRIORITY


class SphinxFeature(Feature):
    @subscribe('edgy.project.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile

        makefile['SPHINX_OPTS'] = ''
        makefile['SPHINX_BUILD'] = '$(VIRTUAL_ENV)/bin/sphinx-build'
        makefile['SPHINX_SOURCEDIR'] = 'docs'
        makefile['SPHINX_BUILDDIR'] = '$(SPHINX_SOURCEDIR)/_build'

        makefile.add_target(
            '$(SPHINX_SOURCEDIR)',
            '''
            $(SPHINX_BUILD) -b html -D latex_paper_size=a4 $(SPHINX_OPTS) $(SPHINX_SOURCEDIR) $(SPHINX_BUILDDIR)/html
        ''',
            deps=('install-dev', ),
            phony=True)


__feature__ = SphinxFeature
