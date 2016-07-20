# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import textwrap

from edgy.event import Event, EventDispatcher
import logging
from blessings import Terminal

term = Terminal()
logger = logging.getLogger()


class ProjectEvent(Event):
    variables = None
    files = None
    setup = None


class LoggingDispatcher(EventDispatcher):
    logger = logging.getLogger()
    indent_level = 0

    @property
    def indent(self):
        return '  '*type(self).indent_level

    def dispatch(self, event_id, event=None):
        should_log = not event_id.startswith('edgy.project.on_file_') or self.logger.getEffectiveLevel() <= logging.DEBUG
        if should_log:
            self.logger.info(self.indent+term.bold('>') +' dispatch ⚡ {}'.format(term.bold(term.blue(event_id))))
        type(self).indent_level += 1
        event = super(LoggingDispatcher, self).dispatch(event_id, event)
        type(self).indent_level -= 1
        if should_log:
            self.logger.info(self.indent+term.bold('<')+' {}'.format(term.black('dispatched '+event_id)))
        return event

    def debug(self, feature, *messages):
        return self.logger.debug(
            '   ✔ ' + term.bold(term.green(feature.__shortname__)) + ' '.join(map(str, messages))
        )

    def info(self, *messages):
        return self.logger.info(self.indent+' '.join(map(str, messages)))


def subscribe(event_id, priority=0):
    """
    Lazy event subscription. Will need to be attached to an event dispatcher using ``attach_subscriptions``

    :param str event_id:
    :param int priority:
    :return:
    """

    def wrapper(f):
        try:
            getattr(f, '__subscriptions__')
        except AttributeError as e:
            f.__subscriptions__ = {}
            f.__doc__ = '' if f.__doc__ is None else textwrap.dedent(f.__doc__).strip()
            if f.__doc__:
                f.__doc__ += '\n'

        f.__subscriptions__[event_id] = priority
        f.__doc__ += '\nListens to ``{}`` event *({})*'.format(event_id, priority)

        return f

    return wrapper


def attach_subscriptions(obj, dispatcher):
    """
    Attach subscriptions to an actual event dispatcher.

    :param object obj:
    :param EventDispatcher dispatcher:
    :return:
    """
    for k in dir(obj):
        f = getattr(obj, k)
        if k[0] != '_' and callable(f) and hasattr(f, '__subscriptions__'):
            for event_id, priority in f.__subscriptions__.items():
                dispatcher.add_listener(event_id, f, priority=priority)
