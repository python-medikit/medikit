#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals, absolute_import, print_function

import os

from collections import OrderedDict
from edgy.event import Event, EventDispatcher

from .config import read_configuration

class ArgumentParser(object):
    from argparse import ArgumentParser as ArgumentParserType

    def __init__(self):
        self.parser = type(self).ArgumentParserType()
        self.subparsers = self.parser.add_subparsers(dest="command")
        init_parser = self.subparsers.add_parser('init')

    def parse_args(self, args=None, namespace=None):
        return self.parser.parse_args(args, namespace)

def _read_configuration(dispatcher):
    config_filename = os.path.join(os.getcwd(), 'Projectfile')
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict((
        ('virtualenv_path', '.virtualenv-$(PYTHON_BASENAME)', ),
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
        ('extras_require', {}, ),
    ))

    features = {
        'git',
        'make',
        'pytest',
        'python',
        'pylint',
    }

    return read_configuration(dispatcher, config_filename, variables, features, files, setup)

class ProjectEvent(Event):
    variables = None
    files = None
    setup = None

def main(args=None):
    parser = ArgumentParser()
    dispatcher = EventDispatcher()

    variables, features, files, setup = _read_configuration(dispatcher)
    feature_instances = {}
    for feature_name in sorted(features):
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
