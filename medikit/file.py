import contextlib
import os
import stat

from whistle import Event


class FileEvent(Event):
    def __init__(self, filename, executable, override):
        super(FileEvent, self).__init__()
        self.executable = executable
        self.filename = filename
        self.override = override


@contextlib.contextmanager
def File(dispatcher, name, *, executable=False, override=False):
    event = FileEvent(name, executable, override)

    if event.override or not os.path.exists(event.filename):
        with open(event.filename, 'w+') as f:
            event.file = f
            event = dispatcher.dispatch('medikit.on_file_opened', event)
            yield f
            event.file = None

        if event.executable and os.path.exists(event.filename):
            st = os.stat(event.filename)
            os.chmod(event.filename, st.st_mode | stat.S_IEXEC)

        dispatcher.dispatch('medikit.on_file_closed', event)
    else:
        yield open('/dev/null', 'w')


@contextlib.contextmanager
def NullFile(dispatcher, name, *, executable=False, override=False):
    event = FileEvent(name, executable, override)

    if event.override or not os.path.exists(event.filename):
        with open('/dev/null', 'w') as f:
            event.file = f
            event = dispatcher.dispatch('medikit.on_file_opened', event)
            yield f
            event.file = None

        dispatcher.dispatch('medikit.on_file_closed', event)
    else:
        yield open('/dev/null', 'w')
