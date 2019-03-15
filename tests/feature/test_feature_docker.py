from medikit.feature.docker import DockerFeature
from medikit.feature.make import Makefile, MakefileEvent
from medikit.testing import FeatureTestCase

PACKAGE_NAME = "bar"


class TestDockerFeature(FeatureTestCase):
    feature_type = DockerFeature
    required_features = {"make", "docker"}

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_make_generate in listeners["medikit.feature.make.on_generate"]
        assert feature.on_end in listeners["medikit.on_end"]

    def test_issue71_override_image_and_default_builder(self):
        feature, dispatcher = self.create_feature()

        config = self.create_config()
        config["docker"].use_default_builder()
        config["docker"].set_remote(registry="example.com", user="acme", name="one")

        event = MakefileEvent(PACKAGE_NAME, Makefile(), config)
        feature.on_make_generate(event)

        assert event.makefile.environ["DOCKER_IMAGE"] == "example.com/acme/one"

    def test_issue71_override_image_and_rocker_builder(self):
        feature, dispatcher = self.create_feature()

        config = self.create_config()
        config["docker"].use_rocker_builder()
        config["docker"].set_remote(registry="example.com", user="acme", name="two")

        event = MakefileEvent(PACKAGE_NAME, Makefile(), config)
        feature.on_make_generate(event)

        assert event.makefile.environ["DOCKER_IMAGE"] == "example.com/acme/two"

    def test_issue71_override_image_without_builder_override(self):
        feature, dispatcher = self.create_feature()

        config = self.create_config()
        config["docker"].set_remote(registry="example.com", user="acme", name="three")

        event = MakefileEvent(PACKAGE_NAME, Makefile(), config)
        feature.on_make_generate(event)

        assert event.makefile.environ["DOCKER_IMAGE"] == "example.com/acme/three"
