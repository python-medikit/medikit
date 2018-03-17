"""
Basics of medikit.

Required.

"""
import medikit
from medikit.events import subscribe
from medikit.feature import Feature, LAST_PRIORITY


class MedikitConfig(Feature.Config):
    """ Configuration API for the «medikit» feature. """


class MedikitFeature(Feature):
    Config = MedikitConfig

    @subscribe('medikit.feature.make.on_generate', LAST_PRIORITY)
    def on_make_generate(self, event):
        event.makefile['_MEDIKIT_VERSION'] = medikit.__version__
        event.makefile.add_target('medikit', '''
        ''', phony=True, hidden=True)
