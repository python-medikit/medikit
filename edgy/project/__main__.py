#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import argparse
import logging
import pprint
import tempfile

import os
import sys
from collections import OrderedDict

import tornado.log
from blessings import Terminal
from piptools.repositories import PyPIRepository
from piptools.resolver import Resolver
from piptools.scripts.compile import get_pip_command

from pip.req import parse_requirements
from piptools.utils import format_requirement
from stevedore import ExtensionManager

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

    variables = OrderedDict()

    files = {filename: '' for filename in DEFAULT_FILES}

    setup = OrderedDict(
        (
            ('name', None, ), ('description', None, ), ('license', None, ), ('entry_points', {}, ),
            ('install_requires', [], ), ('extras_require', {}, ), ('data_files', [], ),
            ('url', 'http://example.com/', ), ('download_url', 'http://example.com/', ),
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

    parser_update = subparsers.add_parser('update', help='Update current project.')
    parser_update.set_defaults(handler=handle_update)

    parser_reqs = subparsers.add_parser('reqs', help='List requirements.')
    parser_reqs.set_defaults(handler=handle_reqs)
    parser_reqs.add_argument('--extra', '-e', default=None)

    options = parser.parse_args(args if args is not None else sys.argv[1:])
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    return options.handler(os.path.join(os.getcwd(), options.config), **vars(options))


def handle_init(config_filename, **kwargs):
    if os.path.exists(config_filename):
        raise IOError(
            'No config should be present in current directory to initialize (found {})'.format(config_filename)
        )

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


def handle_reqs(config_filename, extra=None, **kwargs):
    dispatcher = LoggingDispatcher()
    variables, features, files, setup = _read_configuration(dispatcher, config_filename)
    pip_command = get_pip_command()
    pip_options, _ = pip_command.parse_args([])
    session = pip_command._build_session(pip_options)
    repository = PyPIRepository(pip_options, session)

    tmpfile = tempfile.NamedTemporaryFile(mode='wt', delete=False)
    if extra:
        tmpfile.write('\n'.join(setup['extras_require'][extra]))
    else:
        tmpfile.write('\n'.join(setup['install_requires']))
    tmpfile.flush()
    constraints = list(
        parse_requirements(tmpfile.name, finder=repository.finder, session=repository.session, options=pip_options)
    )

    resolver = Resolver(constraints, repository, prereleases=False, clear_caches=False, allow_unsafe=False)
    print('-e .{}'.format('[' + extra + ']' if extra else ''))
    print()
    print('\n'.join(sorted(format_requirement(req) for req in resolver.resolve(max_rounds=10))))


def handle_update(config_filename, **kwargs):
    dispatcher = LoggingDispatcher()

    variables, features, files, setup = _read_configuration(dispatcher, config_filename)

    feature_instances = {}
    logger.info(
        'Updating {} with {} features'.
        format(t.bold(setup['name']), ', '.join(t.bold(t.green(feature_name)) for feature_name in sorted(features)))
    )

    sorted_features = sorted(features)

    all_features = {}

    def register_feature(ext, all_features=all_features):
        all_features[ext.name] = ext.plugin

    mgr = ExtensionManager(namespace='edgy.project.feature')
    mgr.map(register_feature)

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

    event = ProjectEvent()
    event.variables, event.files, event.setup = variables, files, setup

    # todo: add listener dump list in debug/verbose mode ?

    event = dispatcher.dispatch('edgy.project.on_start', event)

    dispatcher.dispatch('edgy.project.on_end', event)

    logger.info(u'Done.')


if __name__ == '__main__':
    main()
