import sys

from medikit._version import __version__

try:
    from pip.req import parse_requirements
except ImportError:
    print('Medikit is not yet compatible with pip 10 (like all libraries that depended on any internal api).')
    print()
    print('Please switch back to pip 9.')
    print()
    print('  $ pip install "pip ~=9.0"')
    sys.exit(1)


def listen(*args, **kwargs):
    raise NotImplementedError('This is a stub.')


def require(*args):
    raise NotImplementedError('This is a stub.')


def pipeline(*args):
    raise NotImplementedError('This is a stub.')


__all__ = [
    '__version__',
]
