# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from pip._vendor.distlib.util import parse_requirement

from medikit.events import subscribe
from . import Feature, SUPPORT_PRIORITY


class SphinxFeature(Feature):
    class Config(Feature.Config):
        def __init__(self):
            self._theme = None

        def set_theme(self, theme):
            self._theme = parse_requirement(theme)

        def get_theme(self):
            return self._theme

    @subscribe('medikit.feature.python.on_generate')
    def on_python_generate(self, event):
        event.config['python'].add_requirements(dev=[
            'sphinx >=1.6,<2.0',
        ])

        theme = event.config['sphinx'].get_theme()
        if theme:
            event.config['python'].add_requirements(dev=[theme.requirement])

    @subscribe('medikit.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile

        makefile['SPHINX_BUILD'] = '$(PYTHON_DIRNAME)/sphinx-build'
        makefile['SPHINX_OPTIONS'] = ''
        makefile['SPHINX_SOURCEDIR'] = 'docs'
        makefile['SPHINX_BUILDDIR'] = '$(SPHINX_SOURCEDIR)/_build'

        makefile.add_target(
            '$(SPHINX_SOURCEDIR)',
            '''
            $(SPHINX_BUILD) -b html -D latex_paper_size=a4 $(SPHINX_OPTIONS) $(SPHINX_SOURCEDIR) $(SPHINX_BUILDDIR)/html
        ''',
            deps=('install-dev', ),
            phony=True
        )


__feature__ = SphinxFeature
