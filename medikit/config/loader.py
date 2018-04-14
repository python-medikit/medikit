from stevedore import ExtensionManager

_all_features = {}


def load_feature_extensions():
    if not _all_features:

        def register_feature(ext, all_features=_all_features):
            all_features[ext.name] = ext.plugin

        mgr = ExtensionManager(namespace='medikit.feature')
        mgr.map(register_feature)

    return _all_features
