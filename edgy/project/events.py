# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.event import Event, EventDispatcher
import logging
from blessings import Terminal

term = Terminal()


class ProjectEvent(Event):
    variables = None
    files = None
    setup = None


class LoggingDispatcher(EventDispatcher):
    logger = logging.getLogger()

    def dispatch(self, event_id, event=None):
        if not event_id.startswith('edgy.project.on_file_'):
            self.logger.info('⚡  Dispatching {} ...'.format(term.bold(term.blue(event_id))))
        event = super(LoggingDispatcher, self).dispatch(event_id, event)
        if not event_id.startswith('edgy.project.on_file_'):
            self.logger.info('   ... {} returned {}'.format(term.bold(term.blue(event_id)), event))
        return event

    def debug(self, feature, *messages):
        return self.logger.debug(
            '   ✔ ' + term.blue(feature) + ' '.join(map(str, messages))
        )
