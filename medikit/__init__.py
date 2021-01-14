# noinspection PyUnresolvedReferences
from contextlib import contextmanager

import piptools

from medikit._version import __version__

on_start = "medikit.on_start"
on_end = "medikit.on_end"


def listen(event_id, priority=0):
    """
    This is a stub that will be replaced during medikit execution by a real implementation.
    A fake implementation is provided here so that IDEs understand better the Projectfile content.

    See `whistle.dispatcher.EventDispatcher`.

    """

    def wrapper(listener):
        return listener

    return wrapper


def require(*args):
    """
    This is a stub that will be replaced during medikit execution by a real implementation.
    A fake implementation is provided here so that IDEs understand better the Projectfile content.

    See `medikit.config.registry.ConfigurationRegistry.require`.

    """
    return args[0] if len(args) == 1 else args


@contextmanager
def pipeline(name):
    """
    This is a stub that will be replaced during medikit execution by a real implementation.
    A fake implementation is provided here so that IDEs understand better the Projectfile content.

    See `medikit.config.registry.ConfigurationRegistry.pipeline`.

    """
    yield


def joinwords(*args, prefix=None, separator=" ", **kwargs):
    """
    Join words together using a default space separator.
    """
    return separator.join("".join(filter(None, (prefix, arg))) for arg in args).format(**kwargs)


def joinlines(*args, prefix=None, separator="\n", **kwargs):
    """
    Join lines together using a default line feed separator.
    """
    return joinwords(*args, prefix=prefix, separator=separator, **kwargs)


__all__ = ["__version__"]
