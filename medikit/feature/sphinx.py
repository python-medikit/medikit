from pip._vendor.distlib.util import parse_requirement

from medikit.events import subscribe

from . import SUPPORT_PRIORITY, Feature


class SphinxConfig(Feature.Config):
    def __init__(self):
        self._theme = None

    def set_theme(self, theme):
        """
        Sets the theme. Prefer using the .theme property.

        :param theme: Requirement for theme
        """
        self._theme = parse_requirement(theme)

    def get_theme(self):
        """
        Gets the theme. Prefer using the .theme property.

        :return: parsed requirement
        """
        return self._theme

    theme = property(
        fget=get_theme, fset=set_theme, doc="Sphinx theme to use, that should be parsable as a requirement."
    )

    version = "~=3.4"
    """
    Sphinx version to use. You can override this using `set_version(...)`.
    """

    def set_version(self, version):
        """Overrides package version."""
        self.version = version

    with_autobuild = False


class SphinxFeature(Feature):
    Config = SphinxConfig

    @subscribe("medikit.feature.python.on_generate")
    def on_python_generate(self, event):
        sphinx_config: SphinxConfig = self.get_config(event)
        python_config = self.get_config(event, "python")

        python_config.add_requirements(dev=["sphinx " + sphinx_config.version])
        theme = sphinx_config.get_theme()
        if theme:
            python_config.add_requirements(dev=[theme.requirement])

    @subscribe("medikit.feature.make.on_generate", priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile

        makefile["SPHINX_BUILD"] = "$(PYTHON_DIRNAME)/sphinx-build"
        makefile["SPHINX_OPTIONS"] = ""
        makefile["SPHINX_SOURCEDIR"] = "docs"
        makefile["SPHINX_BUILDDIR"] = "$(SPHINX_SOURCEDIR)/_build"

        makefile.add_target(
            "$(SPHINX_SOURCEDIR)",
            """
            $(SPHINX_BUILD) -b html -D latex_paper_size=a4 $(SPHINX_OPTIONS) $(SPHINX_SOURCEDIR) $(SPHINX_BUILDDIR)/html
        """,
            deps=("install-dev",),
            phony=True,
        )

        # optionnal feature: autobuild
        sphinx_config: SphinxConfig = self.get_config(event)
        if sphinx_config.with_autobuild:
            # Sphinx
            makefile["SPHINX_AUTOBUILD"] = "$(PYTHON_DIRNAME)/sphinx-autobuild"
            makefile.add_target(
                "docs-autobuild",
                "$(SPHINX_AUTOBUILD) --port 8001 $(SPHINX_SOURCEDIR) $(shell mktemp -d)",
                phony=True,
                doc="Run a webserver for sphinx documentation, with autoreload (requires sphinx-autobuild).",
            )
