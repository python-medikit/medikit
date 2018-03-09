"""
Webpack support.

This feature is experimental and as though it may work for you, that's not a guarantee. Please use with care.

"""

from medikit.events import subscribe
from . import Feature


class WebpackFeature(Feature):
    requires = {'nodejs'}

    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile.get_target('install').install.append('$(YARN) --version')


__feature__ = WebpackFeature
