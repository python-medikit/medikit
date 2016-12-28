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
from edgy.event import EventDispatcher
from edgy.project.config import read_configuration
from edgy.project.events import LoggingDispatcher, ProjectEvent
from edgy.project.feature import ProjectInitializer
from edgy.project.settings import DEFAULT_FEATURES, DEFAULT_FILES

# Globals
logger = logging.getLogger()
tornado.log.enable_pretty_logging(logger=logger)
t = Terminal()


def _read_configuration(dispatcher, config_filename):
    """
    Prepare the python context and delegate to the real configuration reader (see config.py)

    :param EventDispatcher dispatcher:
    :return tuple: (variables, features, files, setup)
    """
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict(((
        'virtual_env',
        '.virtualenv-$(PYTHON_BASENAME)', ), ))

    files = {filename: '' for filename in DEFAULT_FILES}

    setup = OrderedDict((
        (
            'name',
            None, ),
        (
            'description',
            None, ),
        (
            'license',
            None, ),
        (
            'entry_points',
            {}, ),
        (
            'install_requires',
            [], ),
        (
            'extras_require',
            {}, ),
        (
            'data_files',
            [], ),
        (
            'url',
            'http://example.com/', ),
        (
            'download_url',
            'http://example.com/', ), ))

    features = set(DEFAULT_FEATURES)

    return read_configuration(dispatcher, config_filename, variables, features, files, setup)


def main(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', '-c', default='Projectfile')
    parser.add_argument('--verbose', '-v', action='store_true', default=False)

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    # todo aliases for update/init
    # warning: http://bugs.python.org/issue9234

    parser_init = subparsers.add_parser('init', help='Initialize a new project.')
    parser_init.set_defaults(handler=handle_init)

    parser_update = subparsers.add_parser('update', help='Update current project.')
    parser_update.set_defaults(handler=handle_update)

    options = parser.parse_args(args if args is not None else sys.argv[1:])
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    return options.handler(os.path.join(os.getcwd(), options.config))


def handle_init(config_filename):
    if os.path.exists(config_filename):
        raise IOError('No config should be present in current directory to initialize (found {})'.format(
            config_filename))

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


def handle_update(config_filename):
    dispatcher = LoggingDispatcher()

    variables, features, files, setup = _read_configuration(dispatcher, config_filename)

    feature_instances = {}
    logger.info('Updating {} with {} features'.format(
        t.bold(setup['name']), ', '.join(t.bold(t.green(feature_name)) for feature_name in sorted(features))))

    sorted_features = sorted(features)
    for feature_name in sorted_features:
        logger.debug('Initializing feature {}...'.format(t.bold(t.green(feature_name))))
        try:
            feature = __import__('edgy.project.feature.' + feature_name, fromlist=('__feature__', )).__feature__
        except (
                ImportError,
                AttributeError, ) as e:
            logger.exception('Feature "{}" not found.'.format(feature_name))

        if feature:
            feature_instances[feature_name] = feature(dispatcher)

            for req in feature_instances[feature_name].requires:
                if not req in sorted_features:
                    raise RuntimeError('Unmet dependency: {} requires {}.'.format(feature_name, req))

            for con in feature_instances[feature_name].conflicts:
                if con in sorted_features:
                    raise RuntimeError('Conflicting dependency: {} conflicts with {}.'.format(con, feature_name))
        else:
            raise RuntimeError('Required feature {} not found.'.format(feature_name))

    event = ProjectEvent()
    event.variables, event.files, event.setup = variables, files, setup

    # todo: add listener dump list in debug/verbose mode ?

    event = dispatcher.dispatch('edgy.project.on_start', event)

    dispatcher.dispatch('edgy.project.on_end', event)

    logger.info(u'Done.')


if __name__ == '__main__':
    main()
