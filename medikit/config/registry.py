from collections import OrderedDict
from contextlib import contextmanager

from stevedore import ExtensionManager

from medikit.pipeline import Pipeline


class ConfigurationRegistry():
    def __init__(self):
        self._configs = {}
        self._features = {}
        self._pipelines = {}
        self._variables = OrderedDict()

        def register_feature(ext):
            self._features[ext.name] = ext.plugin

        mgr = ExtensionManager(namespace='medikit.feature')
        mgr.map(register_feature)

    def __getitem__(self, item):
        return self._configs[item]

    def __contains__(self, item):
        return item in self._configs

    def set_vars(self, **variables):
        self._variables.update(variables)

    def get_var(self, name, default=None):
        return self._variables.get(name, default)

    @property
    def variables(self):
        return self._variables

    @property
    def package_name(self):
        if 'python' in self:
            return self['python'].get('name')
        else:
            name = self.get_var('PACKAGE')
            if not name:
                raise RuntimeError('You must define a package name, using either python.setup() or PACKAGE = ...')
            return name

    def keys(self):
        return self._configs.keys()

    def require(self, *args):
        if len(args) == 1:
            return self._require(args[0])
        elif len(args) > 1:
            return tuple(map(self._require, args))
        raise ValueError('Empty.')

    @contextmanager
    def pipeline(self, name):
        if not name in self._pipelines:
            self._pipelines[name] = Pipeline()
        yield self._pipelines[name]

    @property
    def pipelines(self):
        return self._pipelines

    def _require(self, name):
        if not name in self._features:
            raise ValueError('Unknown feature {!r}.'.format(name))

        if name not in self._configs:
            self._configs[name] = self._features[name].Config()

        return self._configs[name]
