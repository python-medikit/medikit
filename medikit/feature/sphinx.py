from pip._vendor.distlib.util import parse_requirement

from medikit.events import subscribe
from . import Feature, SUPPORT_PRIORITY


class SphinxConfig(Feature.Config):
    __usage__ = """
    
        You can customize the theme:
        
        .. code-block:: python
        
            sphinx.theme = 'sphinx_rtd_theme'
            
        Note that this should be a parsable requirement, and it won't be added to your docs/conf.py automatically.
        
        This feature will add the necessary requirements to the python feature (sphinx mostly, and eventually your theme requirement) and setup the correct makefile task to build the html docs. Note that it won't bootstrap your sphinx config file, and you still need to run the following if your documentation does not exist yet:
        
        .. code-block:: shell-session
        
            $ make update-requirements
            $ make install-dev
            $ mkdir docs
            $ cd docs
            $ sphinx-quickstart .
            
        Then, eventually tune the configuration.
        
        .. note::
        
            In the future, we may consider generating it for you if it does not exist, but it's not a priority.
    
    """

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


class SphinxFeature(Feature):
    Config = SphinxConfig

    @subscribe('medikit.feature.python.on_generate')
    def on_python_generate(self, event):
        event.config['python'].add_requirements(dev=[
            'sphinx ~=1.7',
        ])

        theme = event.config['sphinx'].get_theme()
        if theme:
            event.config['python'].add_requirements(dev=[theme.requirement])

    @subscribe('medikit.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile

        makefile['SPHINX_BUILD'] = '$(PYTHON_DIRNAME)/sphinx-build'
        makefile['SPHINX_OPTIONS'] = ''
        makefile['SPHINX_SOURCEDIR'] = 'docs'
        makefile['SPHINX_BUILDDIR'] = '$(SPHINX_SOURCEDIR)/_build'

        makefile.add_target(
            '$(SPHINX_SOURCEDIR)',
            '''
            $(SPHINX_BUILD) -b html -D latex_paper_size=a4 $(SPHINX_OPTIONS) $(SPHINX_SOURCEDIR) $(SPHINX_BUILDDIR)/html
        ''',
            deps=('install-dev', ),
            phony=True
        )
