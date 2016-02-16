# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.project.feature import ABSOLUTE_PRIORITY


class VirtualenvFeature(object):
    def __init__(self, dispatcher):
        dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=ABSOLUTE_PRIORITY)

    def on_start(self, event):
        pass # todo ? or makefile responsability ? or bundled in python feature ?

__feature__ = VirtualenvFeature
