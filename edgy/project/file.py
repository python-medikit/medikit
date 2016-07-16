from __future__ import absolute_import, unicode_literals

import contextlib
import os

from edgy.event import Event


class FileEvent(Event):
    def __init__(self, filename, override):
        super(FileEvent, self).__init__()
        self.filename = filename
        self.override = override


@contextlib.contextmanager
def File(dispatcher, name, override=False):
    event = FileEvent(name, override)

    if event.override or not os.path.exists(event.filename):
        with open(event.filename, 'w+') as f:
            event.file = f
            event = dispatcher.dispatch('edgy.project.on_file_opened', event)
            yield f
            event.file = None

        dispatcher.dispatch('edgy.project.on_file_closed', event)
    else:
        yield open('/dev/null', 'w')


@contextlib.contextmanager
def NullFile(dispatcher, name, override=False):
    event = FileEvent(name, override)

    if event.override or not os.path.exists(event.filename):
        with open('/dev/null', 'w') as f:
            event.file = f
            event = dispatcher.dispatch('edgy.project.on_file_opened', event)
            yield f
            event.file = None

        dispatcher.dispatch('edgy.project.on_file_closed', event)
    else:
        yield open('/dev/null', 'w')
