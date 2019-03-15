# noinspection PyUnresolvedReferences
import piptools

from medikit._version import __version__

on_start = "medikit.on_start"
on_end = "medikit.on_end"


def listen(*args, **kwargs):
    raise NotImplementedError("This is a stub.")


def require(*args):
    raise NotImplementedError("This is a stub.")


def pipeline(*args):
    raise NotImplementedError("This is a stub.")


__all__ = ["__version__"]
