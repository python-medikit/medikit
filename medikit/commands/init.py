import os
from contextlib import contextmanager

from medikit.commands.base import Command
from medikit.events import LoggingDispatcher
from medikit.feature import ProjectInitializer


@contextmanager
def _change_working_directory(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


class InitCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument('target')
        parser.add_argument('--name')
        parser.add_argument('--description')
        parser.add_argument('--license')
        parser.add_argument('--feature', '-f', action='append', dest='features')

    @staticmethod
    def handle(config_filename, **options):
        if os.path.exists(config_filename):
            raise IOError(
                'No config should be present in current directory to initialize (found {})'.format(config_filename)
            )

        config_dirname = os.path.dirname(config_filename)
        if not os.path.exists(config_dirname):
            os.makedirs(config_dirname)

        # Fast and dirty implementation
        # TODO
        # - input validation
        # - getting input from env/git conf (author...),
        # - dispatching something in selected features so maybe they can suggest deps
        # - deps selection
        # - ...
        with _change_working_directory(config_dirname):
            dispatcher = LoggingDispatcher()
            initializer = ProjectInitializer(dispatcher, options)
            initializer.execute()
            from medikit.commands import UpdateCommand
            return UpdateCommand.handle(config_filename)
