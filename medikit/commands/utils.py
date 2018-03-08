import os
from collections import OrderedDict

from medikit.config import read_configuration
from medikit.settings import DEFAULT_FILES, DEFAULT_FEATURES


def _read_configuration(dispatcher, config_filename):
    """
    Prepare the python context and delegate to the real configuration reader (see config.py)

    :param EventDispatcher dispatcher:
    :return tuple: (variables, features, files, config)
    """
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict()

    files = {filename: '' for filename in DEFAULT_FILES}
    features = set(DEFAULT_FEATURES)

    return read_configuration(dispatcher, config_filename, variables, features, files)