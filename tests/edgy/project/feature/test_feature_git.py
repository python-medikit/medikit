# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from edgy.event import Event
from edgy.project.events import ProjectEvent
from edgy.project.feature.git import GitFeature
from edgy.project.testing import FeatureTestCase
from mock import patch

PACKAGE_NAME = 'foo.bar'


class TestGitFeature(FeatureTestCase):
    feature_type = GitFeature

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners['edgy.project.on_start']
        assert feature.on_end in listeners['edgy.project.on_end']
        assert feature.on_file_change in listeners['edgy.project.on_file_closed']

    def test_on_start(self):
        feature, dispatcher = self.create_feature()

        with patch('os.path.exists', return_value=False):
            commands = list()
            with patch('os.system', side_effect=commands.append) as os_system:
                feature.on_start(Event())
                assert commands == ['git init', 'git add Projectfile', 'git commit -m "initial commit"']

        with patch('os.path.exists', return_value=True):
            commands = list()
            with patch('os.system', side_effect=commands.append) as os_system:
                feature.on_start(Event())
                assert commands == []

    def test_on_end(self):
        feature, dispatcher = self.create_feature()

        commands = list()
        with patch('edgy.project.file.FileEvent') as fe, \
                patch('os.system', side_effect=commands.append) as os_system \
                :
            feature.on_end(ProjectEvent(setup={'name': PACKAGE_NAME}))
            print(commands)
            print(fe.call_args_list)

    @pytest.skip
    def test_on_file_change(self):
        self.fail()
