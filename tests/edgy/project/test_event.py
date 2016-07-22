# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from collections import OrderedDict
from unittest import TestCase

import pytest
from edgy.project.events import ProjectEvent


class TestProjectEvent(TestCase):

    def _test_constructor(self, **kwargs):
        e = ProjectEvent(**kwargs)

        variables, files, setup = kwargs.get('variables', {}), kwargs.get('files', {}), kwargs.get('setup', {})
        assert isinstance(e.variables, OrderedDict)
        assert len(e.variables) == len(variables)
        assert isinstance(e.files, dict)
        assert len(e.files) == len(files)
        assert isinstance(e.setup, OrderedDict)
        assert len(e.setup) == len(setup)

    def test_basics(self):
        self._test_constructor()
        self._test_constructor(variables={}, files={}, setup={})
        self._test_constructor(variables={'foo': 'bar'}, files={}, setup={'name': 'my.pkg'})

        with pytest.raises(TypeError):
            self._test_constructor(unknown='foo')



