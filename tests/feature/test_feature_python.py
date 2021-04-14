from unittest import TestCase

import pytest

import medikit
from medikit.events import ProjectEvent
from medikit.feature.make import MakeFeature, Makefile, MakefileEvent
from medikit.feature.python import PythonConfig, PythonFeature
from medikit.testing import FeatureTestCase

PACKAGE_NAME = "foo.bar"


class TestPythonConfig(TestCase):
    def create_python_config(self):
        return PythonConfig()

    def test_namespace_packages(self):
        config = self.create_python_config()
        config.setup(name=PACKAGE_NAME)
        init_files = list(config.get_init_files())
        assert init_files == [
            ("foo", "foo/__init__.py", {"is_namespace": True}),
            ("foo/bar", "foo/bar/__init__.py", {"is_namespace": False}),
        ]


class TestPythonFeature(FeatureTestCase):
    feature_type = PythonFeature

    def create_config(self):
        config = super().create_config()
        config.require("make")
        python = config.require("python")
        python.setup(name=PACKAGE_NAME)
        return config

    def test_configure(self):
        feature, dispatcher = self.create_feature()
        listeners = dispatcher.get_listeners()

        assert feature.on_start in listeners[medikit.on_start]
        assert feature.on_make_generate in listeners["medikit.feature.make.on_generate"]

    def test_on_make_generate(self):
        python_feature, dispatcher = self.create_feature()
        config = self.create_config()

        python_feature.on_make_generate(MakefileEvent(PACKAGE_NAME, Makefile(), config))

        make_feature, dispatcher = self.create_feature(feature_type=MakeFeature)
        self.create_feature(dispatcher=dispatcher)
        make_feature.on_start(ProjectEvent(config=config, setup={"name": PACKAGE_NAME}))

        assert sorted(dict(make_feature.makefile.targets).keys()) == [
            "clean",
            "help",
            "install",
            "install-dev",
            "medikit",
            "quick",
            "update",
            "update-requirements",
        ]

    def test_on_start(self):
        config = self.create_config()

        feature, dispatcher = self.create_feature()
        event = ProjectEvent(config=config, setup={"name": PACKAGE_NAME, "python_requires": ">=3.5"})
        feature.on_start(event)

        assert event.setup["name"] == PACKAGE_NAME
        assert event.setup["python_requires"] == ">=3.5"

    def test_on_end(self):
        config = self.create_config()

        feature, dispatcher = self.create_feature()
        event = ProjectEvent(config=config, setup={"name": PACKAGE_NAME, "python_requires": ">=3.5"})
        feature.on_end(event)

        assert event.setup["name"] == PACKAGE_NAME
        assert event.setup["python_requires"] == ">=3.5"
        assert not event.config["python"].use_uniform_requirements
        assert not event.config["python"].show_comes_from_info
        assert not event.config["python"].override_requirements

    def test_on_end_uniform_requirements(self):
        config = self.create_config()
        config["python"].use_uniform_requirements = True
        config["python"].show_comes_from_info = True
        config["python"].override_requirements = True

        feature, dispatcher = self.create_feature()
        event = ProjectEvent(config=config, setup={"name": PACKAGE_NAME, "python_requires": ">=3.5"})
        feature.on_end(event)

        assert event.setup["name"] == PACKAGE_NAME
        assert event.setup["python_requires"] == ">=3.5"
        assert event.config["python"].use_uniform_requirements
        assert event.config["python"].show_comes_from_info
        assert event.config["python"].override_requirements
