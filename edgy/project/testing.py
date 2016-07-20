# coding: utf-8
from unittest import TestCase

from edgy.project.events import LoggingDispatcher
from edgy.project.feature import Feature
from edgy.project.file import NullFile


class FeatureTestCase(TestCase):
    feature_type = Feature

    def create_dispatcher(self):
        return LoggingDispatcher()

    def create_feature(self, feature_type=None, dispatcher = None):
        dispatcher = dispatcher or self.create_dispatcher()
        feature = (feature_type or self.feature_type)(dispatcher)
        feature.file_type = NullFile
        return feature, dispatcher

