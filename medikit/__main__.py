#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import argparse
import logging
import os
import sys
from collections import OrderedDict
from contextlib import contextmanager

from blessings import Terminal

from medikit.config import read_configuration, load_features
from medikit.events import LoggingDispatcher, ProjectEvent
from medikit.feature import ProjectInitializer
from medikit.settings import DEFAULT_FEATURES, DEFAULT_FILES
from medikit.logging import getLogger

# Globals

logger = getLogger()

t = Terminal()


def _read_configuration(dispatcher, config_filename):
    """
    Prepare the python context and delegate to the real configuration reader (see config.py)

    :param EventDispatcher dispatcher:
    :return tuple: (variables, features, files, setup)
    """
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict()

    files = {filename: '' for filename in DEFAULT_FILES}

    setup = OrderedDict(
        (
            (
                'name',
                None,
            ),
            (
                'description',
                None,
            ),
            (
                'license',
                None,
            ),
            (
                'entry_points',
                {},
            ),
            (
                'install_requires',
                [],
            ),
            (
                'extras_require',
                {},
            ),
            (
                'data_files',
                [],
            ),
            (
                'url',
                'http://example.com/',
            ),
            (
                'download_url',
                'http://example.com/',
            ),
        )
    )

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
    parser_init.add_argument('target')
    parser_init.add_argument('--name')
    parser_init.add_argument('--description')
    parser_init.add_argument('--license')
    parser_init.add_argument('--feature', '-f', action='append', dest='features')

    parser_update = subparsers.add_parser('update', help='Update current project.')
    parser_update.set_defaults(handler=handle_update)

    options = parser.parse_args(args if args is not None else sys.argv[1:])
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    options = vars(options)
    handler = options.pop('handler')

    config_filename = os.path.join(os.getcwd(), options.pop('target', '.'), options.pop('config'))

    return handler(config_filename, **options)


@contextmanager
def _change_working_directory(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def handle_init(config_filename, **options):
    if os.path.exists(config_filename):
        raise IOError(
            'No config should be present in current directory to initialize (found {})'.format(config_filename)
        )

    config_dirname = os.path.dirname(config_filename)
    if not os.path.exists(config_dirname):
        os.makedirs(config_dirname)

    # Fast and dirty implementation
    # TODO
    # - input validation
    # - getting input from env/git conf (author...),
    # - dispatching something in selected features so maybe they can suggest deps
    # - deps selection
    # - ...
    with _change_working_directory(config_dirname):
        dispatcher = LoggingDispatcher()
        initializer = ProjectInitializer(dispatcher, options)
        initializer.execute()
        return handle_update(config_filename)


def handle_update(config_filename, **kwargs):
    dispatcher = LoggingDispatcher()

    variables, features, files, setup, config = _read_configuration(dispatcher, config_filename)

    feature_instances = {}
    logger.info(
        'Updating {} with {} features'.format(
            t.bold(setup['name']), ', '.join(t.bold(t.green(feature_name)) for feature_name in sorted(features))
        )
    )

    all_features = load_features()

    sorted_features = sorted(features)  # sort to have a predictable display order
    for feature_name in sorted_features:
        logger.debug('Initializing feature {}...'.format(t.bold(t.green(feature_name))))
        try:
            feature = all_features[feature_name]
        except KeyError as exc:
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

    event = ProjectEvent(config=config)
    event.variables, event.files, event.setup = variables, files, setup

    # todo: add listener dump list in debug/verbose mode ?

    event = dispatcher.dispatch('medikit.on_start', event)

    dispatcher.dispatch('medikit.on_end', event)

    logger.info(u'Done.')


if __name__ == '__main__':
    main()
