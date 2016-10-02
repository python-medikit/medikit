# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.project.events import ProjectEvent
from edgy.project.feature.make import Makefile, MakefileEvent
from edgy.project.feature.tornado import TornadoFeature
from edgy.project.testing import FeatureTestCase

PACKAGE_NAME = 'foo.bar'


class TestTornadoFeature(FeatureTestCase):
    feature_type = TornadoFeature

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners['edgy.project.on_start']
        assert feature.on_make_generate in listeners['edgy.project.feature.make.on_generate']

    def test_on_make_generate(self):
        feature, dispatcher = self.create_feature()
        makefile = Makefile()
        event = MakefileEvent(PACKAGE_NAME, makefile)

        # actual call
        feature.on_make_generate(event)

        # check makefile targets
        targets = dict(makefile.targets)
        assert {'serve', 'serve-wsgi'} == set(targets)

    def test_on_start(self):
        feature, dispatcher = self.create_feature()
        event = ProjectEvent(setup={'name': PACKAGE_NAME})
        feature.on_start(event)
