# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from . import Feature


class TornadoFeature(Feature):
    requires = ['python']


__feature__ = TornadoFeature
