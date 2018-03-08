import os

from medikit.commands.base import Command
from medikit.commands.utils import _read_configuration
from medikit.events import LoggingDispatcher
from medikit.pipeline import ConfiguredPipeline

START = 'start'
CONTINUE = 'continue'
ABORT = 'abort'


def _handle_pipeline_action(pipeline, action, *, filename, force=False):
    if action == START:
        if os.path.exists(filename):
            if force:
                os.unlink(filename)
            else:
                raise FileExistsError('Already started, use --force to force a restart, or use continue.')
        pipeline.init()
        with open(filename, 'w+') as f:
            f.write(pipeline.serialize())
        return CONTINUE
    elif action == CONTINUE:
        assert os.path.exists(filename)
        with open(filename) as f:
            pipeline.unserialize(f.read())

        try:
            step = pipeline.next()
            step.logger.info('Running {}.'.format(step))
            step.run(pipeline.meta)
            if step.complete:
                step.logger.info('{} is complete, moving forward.'.format(step))
            else:
                step.logger.warning('{} is NOT complete after run, exiting.'.format(step))
                return

        except StopIteration:
            return

        with open(filename, 'w+') as f:
            f.write(pipeline.serialize())

        return CONTINUE
    elif action == ABORT:
        assert os.path.exists(filename)
        try:
            with open(filename) as f:
                pipeline.unserialize(f.read())
            pipeline.abort()
        finally:
            os.unlink(filename)
    else:
        return


class PipelineCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument('pipeline')
        parser.add_argument(
            'action', choices=(
                START,
                CONTINUE,
                ABORT,
            )
        )
        parser.add_argument('--force', '-f', action='store_true')

    @staticmethod
    def handle(config_filename, *, pipeline, action, force=False, verbose=False):
        dispatcher = LoggingDispatcher()
        variables, features, files, config = _read_configuration(dispatcher, config_filename)

        if not pipeline in config.pipelines:
            raise ValueError(
                'Undefined pipeline {!r}. Valid choices are: {}.'.format(
                    pipeline, ', '.join(sorted(config.pipelines.keys()))
                )
            )
        pipeline = ConfiguredPipeline(pipeline, config.pipelines[pipeline])
        path = os.path.dirname(config_filename)
        pipeline_file = os.path.join(path, '.medikit-pipeline')

        while action:
            action = _handle_pipeline_action(pipeline, action, filename=pipeline_file, force=force)
            force = False
