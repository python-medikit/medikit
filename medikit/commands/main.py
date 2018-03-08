from medikit.commands import InitCommand, UpdateCommand, PipelineCommand
from medikit.commands.base import Command


class MedikitCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument('--config', '-c', default='Projectfile')
        parser.add_argument('--verbose', '-v', action='store_true', default=False)

        with self.create_child('command', required=True) as actions:
            # todo aliases for update/init
            # warning: http://bugs.python.org/issue9234
            actions.add('init', InitCommand, help='Create an empty project.')
            actions.add('update', UpdateCommand, help='Update current project.')
            actions.add('pipeline', PipelineCommand, help='Execute multi-steps pipelines (release, etc.).')