import argparse
import logging
from contextlib import contextmanager


class CommandGroup:
    def __init__(self, subparsers):
        self.subparsers = subparsers
        self.children = {}

    def add(self, name, command=None, **kwargs):
        child_parser = self.subparsers.add_parser(name, **kwargs)
        self.children[name] = (command or Command)(child_parser)
        return self.children[name]


class Command:
    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.getLogger(type(self).__name__)
            return self._logger

    def __init__(self, parser=None):
        parser = parser or argparse.ArgumentParser()
        parser.set_defaults(_handler=self.handle)
        self.parser = parser
        self.children = {}
        self.add_arguments(parser)

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement this method.
        """
        raise NotImplementedError('Subclasses of {} must provide a handle() method'.format(Command.__name__))

    @contextmanager
    def create_child(self, dest, *, required=False):
        subparsers = self.parser.add_subparsers(dest=dest)
        subparsers.required = required
        self.children[dest] = CommandGroup(subparsers)
        yield self.children[dest]
