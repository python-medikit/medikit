# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from collections import OrderedDict
from unittest import TestCase

from edgy.event import EventDispatcher
from edgy.project.events import ProjectEvent, LoggingDispatcher
from edgy.project.feature.make import Makefile, MakefileEvent
from edgy.project.feature.tornado import TornadoFeature
from edgy.project.file import NullFile

PACKAGE_NAME = 'foo.bar'


class TestTornadoFeature(TestCase):
    def test_configure(self):
        dispatcher = EventDispatcher()
        feature = TornadoFeature(dispatcher)
        listeners = dispatcher.get_listeners()
        self.assertIn(feature.on_start, listeners['edgy.project.on_start'])
        self.assertIn(feature.on_make_generate, listeners['edgy.project.feature.make.on_generate'])

    def test_on_make_generate(self):
        dispatcher = EventDispatcher()
        feature = TornadoFeature(dispatcher)
        makefile = Makefile()
        event = MakefileEvent(PACKAGE_NAME, makefile)

        # actual call
        feature.on_make_generate(event)

        targets = dict(makefile.targets)
        self.assertIn('serve', targets)
        self.assertIn('serve-wsgi', targets)

    def test_on_start(self):
        dispatcher = LoggingDispatcher()
        feature = TornadoFeature(dispatcher)
        feature.file_type = NullFile

        event = ProjectEvent()
        event.variables, event.files, event.setup = OrderedDict(), dict(), OrderedDict((('name', PACKAGE_NAME,),))

        feature.on_start(event)
