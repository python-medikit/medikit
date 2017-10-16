from medikit.events import LoggingDispatcher
from medikit.feature import Feature
from medikit.file import NullFile
from unittest import TestCase


class FeatureTestCase(TestCase):
    feature_type = Feature

    def create_dispatcher(self):
        return LoggingDispatcher()

    def create_feature(self, feature_type=None, dispatcher=None):
        dispatcher = dispatcher or self.create_dispatcher()
        feature = (feature_type or self.feature_type)(dispatcher)
        feature.file_type = NullFile
        return feature, dispatcher
