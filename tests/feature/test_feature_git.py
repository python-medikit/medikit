from unittest.mock import patch

import pytest
from whistle import Event

from medikit.events import ProjectEvent
from medikit.feature.git import GitFeature
from medikit.testing import FeatureTestCase

PACKAGE_NAME = 'foo.bar'


class TestGitFeature(FeatureTestCase):
    feature_type = GitFeature
    required_features = {'git'}

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners['medikit.on_start']
        assert feature.on_end in listeners['medikit.on_end']
        assert feature.on_file_change in listeners['medikit.on_file_closed']

    def test_on_start(self):
        feature, dispatcher = self.create_feature()

        with patch('os.path.exists', return_value=False):
            commands = list()
            with patch('os.system', side_effect=commands.append) as os_system:
                feature.on_start(Event())
                assert commands == [
                    'git init', 'git add Projectfile', 'git commit -m "Project initialized using Medikit."'
                ]

        with patch('os.path.exists', return_value=True):
            commands = list()
            with patch('os.system', side_effect=commands.append) as os_system:
                feature.on_start(Event())
                assert commands == []

    def test_on_end(self):
        feature, dispatcher = self.create_feature()

        commands = list()
        with patch('medikit.file.FileEvent') as fe, \
                patch('os.system', side_effect=commands.append) as os_system \
                :
            feature.on_end(ProjectEvent(config=self.create_config(), setup={'name': PACKAGE_NAME}))

    # TODO
    @pytest.mark.skip()
    def test_on_file_change(self):
        self.fail()
