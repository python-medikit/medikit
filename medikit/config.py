from contextlib import contextmanager

from stevedore import ExtensionManager

from medikit import steps
from medikit.pipeline import Pipeline
from medikit.settings import DEFAULT_FEATURES
from medikit.utils import format_file_content


class ConfigurationRegistry():
    def __init__(self):
        self._configs = {}
        self._features = {}
        self._pipelines = {}

        def register_feature(ext):
            self._features[ext.name] = ext.plugin

        mgr = ExtensionManager(namespace='medikit.feature')
        mgr.map(register_feature)

    def __getitem__(self, item):
        return self._configs[item]

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


def read_configuration(dispatcher, filename, variables, features, files):
    config = ConfigurationRegistry()

    # monkey patch placeholders
    import medikit
    _listen, _pipeline, _require = medikit.listen, medikit.pipeline, medikit.require
    medikit.listen, medikit.pipeline, medikit.require = dispatcher.listen, config.pipeline, config.require

    # todo, move this in a configurable place
    with medikit.pipeline('release') as release:
        release.add(steps.Install())
        release.add(steps.BumpVersion())
        release.add(steps.Make('update-requirements'))
        release.add(steps.Make('clean install'))  # test docs
        release.add(steps.System('git add -p .'))
        release.add(steps.Commit('Release: {version}', tag=True))

    # read configuration
    with open(filename) as f:
        # TODO use runpy?
        code = compile(f.read(), filename, 'exec')
    ctx = {'listen': dispatcher.listen}
    exec(code, ctx)

    # restore old values
    medikit.listen, medikit.pipeline, medikit.require = _listen, _pipeline, _require

    for k in variables.keys():
        if k in ctx:
            variables[k] = ctx[k]

    for feature in DEFAULT_FEATURES:
        config.require(feature)

    # old, deprecated way ...
    for feature in set(ctx.pop('enable_features', ())) - set(ctx.pop('disable_features', ())):
        config.require(feature)

    # current way ...
    features = features | set(config.keys())

    for k in files.keys():
        if k in ctx:
            files[k] = format_file_content(ctx[k])

    return variables, features, files, config


_all_features = {}


def load_features():
    if not _all_features:

        def register_feature(ext, all_features=_all_features):
            all_features[ext.name] = ext.plugin

        mgr = ExtensionManager(namespace='medikit.feature')
        mgr.map(register_feature)

    return _all_features
