#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import click
import os

from blessings import Terminal
from collections import OrderedDict
from edgy.event import Event, EventDispatcher

from .config import read_configuration


# Globals
t = Terminal()


def _read_configuration(dispatcher):
    config_filename = os.path.join(os.getcwd(), 'Projectfile')
    if not os.path.exists(config_filename):
        raise IOError('Could not find project description file (looked in {})'.format(config_filename))

    variables = OrderedDict((
        ('virtual_env', '.virtualenv-$(PYTHON_BASENAME)', ),
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
        ('install_requires', [], ),
        ('entry_points', {}, ),
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

def echo(message=None, file=None, nl=True, err=False, color=None):
    prefix = (t.red(t.bold(u'ERROR:')) if err else t.black(u'[edgy.project]')) + ' '
    return click.echo(prefix+(message or ''), file, nl, err, color)

@click.command()
def project_cli():
    dispatcher = EventDispatcher()

    echo(u'Reading Projectfile...')
    variables, features, files, setup = _read_configuration(dispatcher)

    feature_instances = {}
    for feature_name in sorted(features):
        try:
            feature = __import__('edgy.project.feature.' + feature_name, fromlist=('__feature__', )).__feature__
        except (ImportError, AttributeError, ) as e:
            echo(u'Error while importing feature "{}" ...'.format(feature_name), err=True, color='red')
            raise

        if feature:
            feature_instances[feature_name] = feature(dispatcher)

        echo(u'Feature "{}" loaded ({}).'.format(feature_name, feature))

    event = ProjectEvent()
    event.variables, event.files, event.setup = variables, files, setup
    event = dispatcher.dispatch('edgy.project.on_start', event)
    event = dispatcher.dispatch('edgy.project.on_end', event)

    echo(u'Done.')


if __name__ == '__main__':
    project_cli()
