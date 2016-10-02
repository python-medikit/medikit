# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from edgy.project.events import ProjectEvent
from edgy.project.feature.make import MakeFeature, Makefile, MakefileEvent
from edgy.project.feature.python import PythonFeature
from edgy.project.testing import FeatureTestCase

PACKAGE_NAME = 'foo.bar'


class TestPythonFeature(FeatureTestCase):
    feature_type = PythonFeature

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners['edgy.project.on_start']
        assert feature.on_make_generate in listeners['edgy.project.feature.make.on_generate']

    def test_on_make_generate(self):
        python_feature, dispatcher = self.create_feature()

        with pytest.raises(KeyError):
            # This should fail, as the install/install-dev targets are defined in MakeFeature
            python_feature.on_make_generate(
                MakefileEvent(PACKAGE_NAME, Makefile())
            )

        make_feature, dispatcher = self.create_feature(feature_type=MakeFeature)
        self.create_feature(dispatcher=dispatcher)
        make_feature.on_start(
            ProjectEvent(setup={'name': PACKAGE_NAME})
        )

        assert sorted(dict(make_feature.makefile.targets).keys()) == [
            '$(VIRTUAL_ENV)',
            'clean',
            'install',
            'install-dev',
        ]

    def test_on_start(self):
        feature, dispatcher = self.create_feature()
        feature.on_start(
            ProjectEvent(setup={'name': PACKAGE_NAME})
        )
