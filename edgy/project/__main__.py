#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals, absolute_import, print_function

import os
import sys
import textwrap

from collections import OrderedDict
from edgy.event import Event, EventDispatcher as BaseEventDispatcher

from .config import read_configuration
from .file import File
from .util import format_file_content

class ArgumentParser(object):
    from argparse import ArgumentParser as ArgumentParserType

    def __init__(self):
        self.parser = type(self).ArgumentParserType()
        self.subparsers = self.parser.add_subparsers(dest="command")
        init_parser = self.subparsers.add_parser('init')

    def parse_args(self, args=None, namespace=None):
        return self.parser.parse_args(args, namespace)

class EventDispatcher(BaseEventDispatcher):
    def listen(self, event_name, priority=0):
        def wrapper(listener):
            self.add_listener(event_name, listener, priority)
            return listener
        return wrapper

def _read_configuration():
    config_filename = os.path.join(os.getcwd(), 'Projectfile')
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict((
        ('virtualenv_path', '.$(PYTHON_BASENAME)-virtualenv', ),
        ('wheelhouse_path', '.$(PYTHON_BASENAME)-wheelhouse', ),
        ('pipcache_path', '.$(PYTHON_BASENAME)-pipcache', ),
    ))

    files = {
        'requirements': '',
        'classifiers': '',
        'version': '',
    }

    setup = OrderedDict((
        ('name', None, ),
        ('description', None, ),
        ('license', None, ),
        ('url', 'http://example.com/', ),
        ('download_url', 'http://example.com/', ),
    ))

    features = {
        'git',
        'make',
        'python',
        'nosetests',
        'pylint',
    }

    return read_configuration(config_filename, variables, features, files, setup)

class ProjectEvent(Event):
    variables = None
    files = None
    setup = None

def main(args=None):
    parser = ArgumentParser()
    dispatcher = EventDispatcher()

    # XXX Temporary debug snippet
    #@dispatcher.listen('edgy.project.on_file_closed')
    #def on_file_closed(event):
    #    print 'on_file_closed', event.filename

    variables, features, files, setup = _read_configuration()
    feature_instances = {}
    for feature_name in features:
        try:
            feature = __import__('edgy.project.feature.' + feature_name, fromlist=('__feature__', )).__feature__
        except (ImportError, AttributeError, ) as e:
            print('Error while importing feature "{}" ...'.format(feature_name))
            raise

        if feature:
            feature_instances[feature_name] = feature(dispatcher)

    event = ProjectEvent()
    event.variables, event.files, event.setup = variables, files, setup
    event = dispatcher.dispatch('edgy.project.on_start', event)
    event = dispatcher.dispatch('edgy.project.on_end', event)


if __name__ == '__main__':
    main()
