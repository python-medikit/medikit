#!/usr/bin/env python

import logging
import os
import sys
import warnings
from subprocess import check_output

import mondrian

import medikit
from medikit.commands.main import MedikitCommand


def main(args=None):
    if not sys.warnoptions:
        logging.captureWarnings(True)
    warnings.simplefilter("default", DeprecationWarning)
    mondrian.setup(excepthook=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    cli = MedikitCommand()

    options, more_args = cli.parser.parse_known_args(args if args is not None else sys.argv[1:])
    if options.verbose:
        logger.setLevel(logging.DEBUG)

    options = vars(options)
    command, handler = options.pop('command'), options.pop('_handler')

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
