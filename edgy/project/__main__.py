#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, print_function

import click
import os

import itertools
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
        ('virtual_env', '.virtualenv-$(PYTHON_BASENAME)',),
    ))

    files = {
        'requirements': '',
        'classifiers': '',
        'version': '',
    }

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


def echo(message=None, section='project', file=None, nl=True, err=False, color=None):
    prefix = (t.red(t.bold(u'ERROR')) if err else (t.black(section)) if section else '')
    return click.echo(prefix + ' - ' + (message or ''), file, nl, err, color)


class LoggingDispatcher(EventDispatcher):
    def dispatch(self, event_id, event=None):
        if not event_id.startswith('edgy.project.on_file_'):
            echo('Dispatching {}'.format(t.bold(t.blue(event_id))), 'event')
        return super(LoggingDispatcher, self).dispatch(event_id, event)

    def echo(self, feature, *messages):
        message = ' '.join(itertools.chain((t.bold(t.green(feature)),), list(map(str, messages))))
        return click.echo(message)


@click.command()
def project_cli():
    dispatcher = LoggingDispatcher()

    variables, features, files, setup = _read_configuration(dispatcher)

    feature_instances = {}
    for feature_name in sorted(features):
        echo(u'Initializing feature {}...'.format(t.bold(t.green(feature_name))), 'init')
        try:
            feature = __import__('edgy.project.feature.' + feature_name, fromlist=('__feature__',)).__feature__
        except (ImportError, AttributeError,) as e:
            echo(u'Feature "{}" does not exist.'.format(feature_name), 'init', err=True, color='red')

        if feature:
            feature_instances[feature_name] = feature(dispatcher)

    event = ProjectEvent()
    event.variables, event.files, event.setup = variables, files, setup

    event = dispatcher.dispatch('edgy.project.on_start', event)
    event = dispatcher.dispatch('edgy.project.on_end', event)

    echo(u'Done.', None)


if __name__ == '__main__':
    project_cli()
