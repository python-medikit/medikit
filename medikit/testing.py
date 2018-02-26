from unittest import TestCase

from medikit.config import ConfigurationRegistry
from medikit.events import LoggingDispatcher
from medikit.feature import Feature
from medikit.file import NullFile


class FeatureTestCase(TestCase):
    feature_type = Feature
    required_features = set()

    def create_dispatcher(self):
        return LoggingDispatcher()

    def create_feature(self, feature_type=None, dispatcher=None):
        dispatcher = dispatcher or self.create_dispatcher()
        feature = (feature_type or self.feature_type)(dispatcher)
        feature.file_type = NullFile
        return feature, dispatcher

    def create_config(self):
        config = ConfigurationRegistry()
        if len(self.required_features):
            config.require(*self.required_features)
        return config
