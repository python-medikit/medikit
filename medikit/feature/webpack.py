# coding: utf-8

import os
import random

from medikit.events import subscribe
from . import Feature, SUPPORT_PRIORITY


class WebpackFeature(Feature):
    requires = {'nodejs'}

    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile.get_target('install').install.append('$(YARN) --version')


__feature__ = WebpackFeature
