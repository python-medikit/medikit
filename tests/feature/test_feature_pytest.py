# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from edgy.project.events import ProjectEvent
from edgy.project.feature.make import MakeFeature, Makefile, MakefileEvent
from edgy.project.feature.pytest import PytestFeature
from edgy.project.testing import FeatureTestCase

PACKAGE_NAME = 'foo.bar'


class TestPytestFeature(FeatureTestCase):
    feature_type = PytestFeature

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners['edgy.project.on_start']
        assert feature.on_make_generate in listeners['edgy.project.feature.make.on_generate']

    def test_on_make_generate(self):
        pytest_feature, dispatcher = self.create_feature()

        event = MakefileEvent(PACKAGE_NAME, Makefile())
        pytest_feature.on_make_generate(event)

        assert {'test'} == set(dict(event.makefile.targets).keys())
        assert {'PYTEST', 'PYTEST_OPTIONS'} == set(event.makefile.environ)

    def test_on_start(self):
        feature, dispatcher = self.create_feature()
        event = ProjectEvent(setup={'name': PACKAGE_NAME})
        feature.on_start(event)

