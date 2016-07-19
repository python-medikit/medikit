# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

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


def subscribe(event_id, priority=0):
    """
    Lazy event subscription. Will need to be attached to an event dispatcher using ``attach_subscriptions``

    :param str event_id:
    :param int priority:
    :return:
    """

    def wrapper(f):
        f.__subscriptions__ = getattr(f, '__subscriptions__', {})
        f.__subscriptions__[event_id] = priority
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
        v = getattr(obj, k)
        if k[0] != '_' and callable(v) and hasattr(v, '__subscriptions__'):
            for event_id, priority in v.__subscriptions__.items():
                dispatcher.add_listener(event_id, v, priority=priority)
