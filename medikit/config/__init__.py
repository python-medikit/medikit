import runpy

import medikit
from medikit.compat import deprecated_feature
from medikit.config.defaults import setup_default_pipelines
from medikit.config.registry import ConfigurationRegistry
from medikit.settings import DEFAULT_FEATURES
from medikit.utils import format_file_content


def read_configuration(dispatcher, filename, variables, features, files):
    config = ConfigurationRegistry()
    setup_default_pipelines(config)
    default_context = {'listen': dispatcher.listen}

    # monkey patch placeholders
    _listen, _pipeline, _require = medikit.listen, medikit.pipeline, medikit.require
    try:
        medikit.listen, medikit.pipeline, medikit.require = dispatcher.listen, config.pipeline, config.require
        context = runpy.run_path(filename, init_globals=default_context)
    finally:
        # restore old values
        medikit.listen, medikit.pipeline, medikit.require = _listen, _pipeline, _require

    for k in variables.keys():
        if k in context:
            variables[k] = context[k]

    for feature in DEFAULT_FEATURES:
        config.require(feature)

    # Deprecated: enabled and disabled features.
    enable_features, disable_features = context.pop('enable_features', ()), context.pop('disable_features', ())
    if len(enable_features) or len(disable_features):
        with deprecated_feature('0.5.0', '0.6.0', 'Using "enable_features" and "disable_features"', 'require()'):
            for feature in set(enable_features) - set(disable_features):
                config.require(feature)

    # Better: required features.
    features = features | set(config.keys())

    for k in files.keys():
        if k in context:
            files[k] = format_file_content(context[k])

    return variables, features, files, config
