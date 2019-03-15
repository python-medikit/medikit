from medikit.events import ProjectEvent
from medikit.feature.make import Makefile, MakefileEvent
from medikit.feature.pytest import PytestFeature
from medikit.testing import FeatureTestCase

PACKAGE_NAME = 'foo.bar'


class TestPytestFeature(FeatureTestCase):
    feature_type = PytestFeature
    required_features = {'make', 'pytest'}

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners['medikit.on_start']
        assert feature.on_make_generate in listeners['medikit.feature.make.on_generate']

    def test_on_make_generate(self):
        pytest_feature, dispatcher = self.create_feature()

        event = MakefileEvent(PACKAGE_NAME, Makefile(), self.create_config())
        pytest_feature.on_make_generate(event)

        assert {'test'} == set(dict(event.makefile.targets).keys())
        assert {'PYTEST', 'PYTEST_OPTIONS'} == set(event.makefile.environ)

    def test_on_start(self):
        feature, dispatcher = self.create_feature()
        event = ProjectEvent(config=self.create_config(), setup={'name': PACKAGE_NAME})
        feature.on_start(event)
