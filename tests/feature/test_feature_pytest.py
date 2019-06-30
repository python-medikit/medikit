import medikit
from medikit.events import ProjectEvent
from medikit.feature.make import Makefile, MakefileEvent
from medikit.feature.pytest import PytestFeature
from medikit.testing import FeatureTestCase

PACKAGE_NAME = "foo.bar"


class TestPytestFeature(FeatureTestCase):
    feature_type = PytestFeature
    required_features = {"python", "make", "pytest"}

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners[medikit.on_start]
        assert feature.on_make_generate in listeners["medikit.feature.make.on_generate"]

    def test_on_make_generate(self):
        pytest_feature, _ = self.create_feature()

        event = MakefileEvent(PACKAGE_NAME, Makefile(), self.create_config())
        pytest_feature.on_make_generate(event)

        assert {"test"} == set(dict(event.makefile.targets).keys())
        assert {"PYTEST", "PYTEST_OPTIONS"} == set(event.makefile.environ)

    def test_on_start(self):
        feature, _ = self.create_feature()
        event = ProjectEvent(config=self.create_config(), setup={"name": PACKAGE_NAME})
        feature.on_start(event)

    def test_set_version(self):
        # test without setting the version, should be the current default
        config = self.create_config()
        event = ProjectEvent(config=config, setup={"name": PACKAGE_NAME})
        feature, _ = self.create_feature()
        feature.on_python_generate(event)
        assert list(config["python"].get_requirements(extra="dev")) == [
            "coverage ~= 4.5",
            "pytest ~= 4.6",
            "pytest-cov ~= 2.7",
        ]

        # test with setting the version, should override the default
        config = self.create_config()
        config.require("pytest").set_version("~=5.0")
        event = ProjectEvent(config=config, setup={"name": PACKAGE_NAME})
        feature, _ = self.create_feature()
        feature.on_python_generate(event)
        assert list(config["python"].get_requirements(extra="dev")) == [
            "coverage ~= 4.5",
            "pytest ~= 5.0",
            "pytest-cov ~= 2.7",
        ]
