#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import os
import sys
import warnings
from subprocess import check_output

import mondrian

import medikit
from medikit.commands import START, CONTINUE, ABORT, handle_init, handle_update, handle_pipeline


def main(args=None):
    mondrian.setup(excepthook=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

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

    parser_pipeline = subparsers.add_parser('pipeline', help='Execute multi-steps pipelines (release, etc.).')
    parser_pipeline.set_defaults(handler=handle_pipeline)
    parser_pipeline.add_argument('pipeline')
    parser_pipeline.add_argument(
        'action', choices=(
            START,
            CONTINUE,
            ABORT,
        )
    )
    parser_pipeline.add_argument('--force', '-f', action='store_true')

    options, more_args = parser.parse_known_args(args if args is not None else sys.argv[1:])
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    options = vars(options)
    command, handler = options.pop('command'), options.pop('handler')

    config_filename = os.path.join(os.getcwd(), options.pop('target', '.'), options.pop('config'))

    version = medikit.__version__
    try:
        if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(medikit.__file__)), '.git')):
            try:
                version = check_output(
                    ['git', 'describe'], cwd=os.path.dirname(os.path.dirname(medikit.__file__))
                ).decode('utf-8').strip() + ' (git)'
            except:
                version = check_output(
                    ['git', 'rev-parse', 'HEAD'], cwd=os.path.dirname(os.path.dirname(medikit.__file__))
                ).decode('utf-8').strip()[0:7] + ' (git)'
    except:
        warnings.warn('Git repository found, but could not find version number from the repository.')

    print(mondrian.term.lightwhite_bg(mondrian.term.red('  ✚  Medikit v.' + version + '  ✚  ')))

    if len(more_args):
        return handler(config_filename, more=more_args, **options)
    else:
        return handler(config_filename, **options)


if __name__ == '__main__':
    main()
