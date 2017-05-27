from __future__ import absolute_import

from stevedore import ExtensionManager

from .util import format_file_content


class ConfigurationRegistry():
    def __init__(self):
        self._configs = {}
        self._features = {}

        def register_feature(ext):
            self._features[ext.name] = ext.plugin

        mgr = ExtensionManager(namespace='edgy.project.feature')
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

    import edgy.project
    _require_backup = edgy.project.require
    edgy.project.listen = dispatcher.listen
    edgy.project.require = config.require
    # todo runpy ?
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
    ctx = {'listen': dispatcher.listen}
    exec(code, ctx)
    edgy.project.require = _require_backup

    for k in variables.keys():
        if k in ctx:
            variables[k] = ctx[k]

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
