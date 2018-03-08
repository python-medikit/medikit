import sys
import warnings
from contextlib import contextmanager

from packaging import version

import medikit


@contextmanager
def deprecated_feature(deprecated_in, removed_in, feature, replacement):
    current_version = version.parse(medikit.__version__)
    deprecated_in = version.parse(deprecated_in)
    removed_in = version.parse(removed_in)
    print(current_version, deprecated_in, removed_in)
    print(sys.warnoptions)
    if current_version < deprecated_in:
        warnings.warn(
            'Using {} is pending deprecation starting at {} and will stop working at {}.\nPlease use {} instead.'.
            format(feature, deprecated_in, removed_in, replacement), PendingDeprecationWarning
        )
        yield
    elif current_version < removed_in:
        warnings.warn(
            'Using {} is deprecated since {} and will stop working at {}.\nPlease use {} instead.'.format(
                feature, deprecated_in, removed_in, replacement
            ), DeprecationWarning
        )
        yield
    else:
        raise RuntimeError(
            'Using {} is not supported anymore since {}. Use {} instead.'.format(feature, removed_in, replacement)
        )
