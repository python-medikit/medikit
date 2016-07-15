#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import argparse
import logging
import os
import sys
from collections import OrderedDict

import tornado.log
from blessings import Terminal
from edgy.event import Event, EventDispatcher
from edgy.project.feature import ProjectInitializer
from edgy.project.settings import DEFAULT_FEATURES, DEFAULT_FILES

from .config import read_configuration

# Globals
logger = logging.getLogger()
tornado.log.enable_pretty_logging(logger=logger)
t = Terminal()

try:
    input = raw_input
except NameError:
    input = input


def _read_configuration(dispatcher, config_filename):
    """
    Prepare the python context and delegate to the real configuration reader (see config.py)

    :param EventDispatcher dispatcher:
    :return tuple: (variables, features, files, setup)
    """
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict((
        ('virtual_env', '.virtualenv-$(PYTHON_BASENAME)',),
    ))

    files = {filename: '' for filename in DEFAULT_FILES}

    setup = OrderedDict((
        ('name', None,),
        ('description', None,),
        ('license', None,),
        ('url', 'http://example.com/',),
        ('download_url', 'http://example.com/',),
        ('extras_require', {},),
        ('install_requires', [],),
        ('entry_points', {},),
    ))

    features = set(DEFAULT_FEATURES)

    return read_configuration(dispatcher, config_filename, variables, features, files, setup)


class ProjectEvent(Event):
    variables = None
    files = None
    setup = None


class LoggingDispatcher(EventDispatcher):
    def dispatch(self, event_id, event=None):
        if not event_id.startswith('edgy.project.on_file_'):
            logger.info('⚡  Dispatching {} ...'.format(t.bold(t.blue(event_id))))
        event = super(LoggingDispatcher, self).dispatch(event_id, event)
        if not event_id.startswith('edgy.project.on_file_'):
            logger.info('   ... {} returned {}'.format(t.bold(t.blue(event_id)), event))
        return event

    def debug(self, feature, *messages):
        return logger.debug(
            '   ✔ ' + t.blue(feature) + ' '.join(map(str, messages))
        )


def main(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', '-c', default='Projectfile')
    parser.add_argument('--verbose', '-v', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_init = subparsers.add_parser('init', help='Initialize a new project.')
    parser_init.set_defaults(handler=handle_init)

    parser_update = subparsers.add_parser('update', aliases=('up',), help='Update current project.')
    parser_update.set_defaults(handler=handle_update)

    options = parser.parse_args(args or sys.argv[1:])
    if options.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug('Parsed command line options: {}'.format(options))

    return options.handler(
        os.path.join(os.getcwd(), options.config)
    )


def handle_init(config_filename):
    if os.path.exists(config_filename):
        raise IOError(
            'No config should be present in current directory to initialize (found {})'.format(config_filename))

    # Fast and dirty implementation
    # TODO
    # - input validation
    # - getting input from env/git conf (author...),
    # - dispatching something in selected features so maybe they can suggest deps
    # - deps selection
    # - ...
    dispatcher = LoggingDispatcher()
    initializer = ProjectInitializer(dispatcher)
    initializer.execute()

    return handle_update(config_filename)


# XXX deprecated
project_cli = main


def handle_update(config_filename):
    dispatcher = LoggingDispatcher()

    variables, features, files, setup = _read_configuration(dispatcher, config_filename)

    feature_instances = {}
    logger.info('Updating {} with {} features'.format(
        t.bold(setup['name']),
        ', '.join(t.bold(t.green(feature_name)) for feature_name in sorted(features))))
    for feature_name in sorted(features):
        logger.debug('Initializing feature {}...'.format(t.bold(t.green(feature_name))))
        try:
            feature = __import__('edgy.project.feature.' + feature_name, fromlist=('__feature__',)).__feature__
        except (ImportError, AttributeError,) as e:
            logger.exception('Feature "{}" does not exist.'.format(feature_name))

        if feature:
            feature_instances[feature_name] = feature(dispatcher)

    event = ProjectEvent()
    event.variables, event.files, event.setup = variables, files, setup

    event = dispatcher.dispatch('edgy.project.on_start', event)
    event = dispatcher.dispatch('edgy.project.on_end', event)

    logger.info(u'Done.')


if __name__ == '__main__':
    main()
