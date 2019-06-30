"""
Adds the pytest testing framework to your project.

"""

import os

import medikit
from medikit.events import subscribe

from . import SUPPORT_PRIORITY, Feature


class PytestConfig(Feature.Config):
    version = "~=4.6"
    """
    Pytest version to use in dev requirements. You can override this using `set_version(...)`.
    """

    addons = {"coverage": "~=4.5", "pytest-cov": "~=2.7"}
    """
    Additionnal packages to use in dev requirements along with the main pytest packe. You can override this dictionnary.
    """

    def set_version(self, version):
        """
        Overrides Pytest version requirement with your own.
        """
        self.version = version


class PytestFeature(Feature):
    # TODO: http://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner

    Config = PytestConfig

    requires = {"python"}

    @subscribe("medikit.feature.python.on_generate")
    def on_python_generate(self, event):
        config = self.get_config(event)
        python = self.get_config(event, "python")

        python.add_requirements(dev=["pytest " + config.version, *map(" ".join, config.addons.items())])

    @subscribe("medikit.feature.make.on_generate", priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile
        makefile["PYTEST"] = "$(PYTHON_DIRNAME)/pytest"
        makefile["PYTEST_OPTIONS"] = "--capture=no --cov=$(PACKAGE) --cov-report html".format(
            path=event.package_name.replace(".", os.sep)
        )
        makefile.add_target(
            "test",
            """
            $(PYTEST) $(PYTEST_OPTIONS) tests
        """,
            deps=("install-dev",),
            phony=True,
            doc="Runs the test suite.",
        )

    @subscribe(medikit.on_start, priority=SUPPORT_PRIORITY)
    def on_start(self, event):
        tests_dir = "tests"
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir)

        gitkeep_file = os.path.join(tests_dir, ".gitkeep")

        if not os.path.exists(gitkeep_file):
            self.render_empty_files(gitkeep_file)

        self.render_file(".coveragerc", "pytest/coveragerc.j2")
        self.render_file(".travis.yml", "pytest/travis.yml.j2")
