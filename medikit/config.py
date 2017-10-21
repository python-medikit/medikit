from stevedore import ExtensionManager

from medikit.settings import DEFAULT_FEATURES
from medikit.utils import format_file_content


class ConfigurationRegistry():
    def __init__(self):
        self._configs = {}
        self._features = {}

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

    def _require(self, name):
        if not name in self._features:
            raise ValueError('Unknown feature {!r}.'.format(name))

        if name not in self._configs:
            self._configs[name] = self._features[name].Config()

        return self._configs[name]


def read_configuration(dispatcher, filename, variables, features, files, setup):
    config = ConfigurationRegistry()

    import medikit
    _require_backup = medikit.require
    medikit.listen = dispatcher.listen
    medikit.require = config.require
    # todo runpy ?
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
    ctx = {'listen': dispatcher.listen}
    exec(code, ctx)
    medikit.require = _require_backup

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

    for k in setup.keys():
        try:
            setup[k] = config['python'].get(k)
        except KeyError:
            if k in ctx:  # BC
                setup[k] = ctx[k]

        if setup[k] is None:
            raise ValueError('You must provide a value for the setup entry "{}" in your Projectfile.'.format(k))

    return variables, features, files, setup, config


_all_features = {}


def load_features():
    if not _all_features:

        def register_feature(ext, all_features=_all_features):
            all_features[ext.name] = ext.plugin

        mgr = ExtensionManager(namespace='medikit.feature')
        mgr.map(register_feature)

    return _all_features
