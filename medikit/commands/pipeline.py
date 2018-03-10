import datetime
import os

from mondrian import term

from medikit.commands.base import Command
from medikit.commands.utils import _read_configuration
from medikit.events import LoggingDispatcher
from medikit.pipeline import ConfiguredPipeline, logger

START = 'start'
CONTINUE = 'continue'
ABORT = 'abort'
COMPLETE = 'complete'


class PipelineCommand(Command):
    def add_arguments(self, parser):
        parser.add_argument('pipeline', default=None, nargs='?')
        parser.add_argument(
            'action', choices=(
                START,
                CONTINUE,
                ABORT,
            ), nargs='?'
        )
        parser.add_argument('--force', '-f', action='store_true')

    @classmethod
    def handle(cls, config_filename, *, pipeline, action, force=False, verbose=False):
        dispatcher = LoggingDispatcher()
        variables, features, files, config = _read_configuration(dispatcher, config_filename)

        if not pipeline:
            raise ValueError(
                'You must choose a pipeline to run. Available choices: {}.'.format(
                    ', '.join(sorted(config.pipelines.keys()))
                )
            )

        if not pipeline in config.pipelines:
            raise ValueError(
                'Undefined pipeline {!r}. Valid choices are: {}.'.format(
                    pipeline, ', '.join(sorted(config.pipelines.keys()))
                )
            )

        pipeline = ConfiguredPipeline(pipeline, config.pipelines[pipeline])
        path = os.path.dirname(config_filename)
        pipeline_file = os.path.join(path, '.medikit/pipelines', pipeline.name + '.json')
        pipeline_dirname = os.path.dirname(pipeline_file)
        if not os.path.exists(pipeline_dirname):
            os.makedirs(pipeline_dirname)
        elif not os.path.isdir(pipeline_dirname):
            raise NotADirectoryError(
                'The pipeline state path "{}" was found but is not a directory...'.format(pipeline_dirname)
            )

        if not action:
            raise RuntimeError('Choose a pipeline action: start, continue, abort.')

        while action:
            if action == START:
                action = cls._handle_start(pipeline, filename=pipeline_file, force=force)
            elif action == CONTINUE:
                action = cls._handle_continue(pipeline, filename=pipeline_file)
            elif action == ABORT:
                action = cls._handle_abort(pipeline, filename=pipeline_file)
            elif action == COMPLETE:
                target = os.path.join(
                    '.medikit/pipelines',
                    pipeline.name + '.' + str(datetime.datetime.now()).replace(':', '.').replace(' ', '.') + '.json'
                )
                os.rename(pipeline_file, os.path.join(path, target))
                logger.info('Pipeline complete. State saved as “{}”.'.format(target))
                break
            else:
                raise ValueError('Invalid action “{}”.'.format(action))
            force = False

    @classmethod
    def _handle_start(cls, pipeline, *, filename, force=False):
        if os.path.exists(filename):
            if not force:
                raise FileExistsError(
                    'Already started, use `medikit pipeline {name} start --force` to force a restart, or use `medikit pipeline {name} continue`.'.
                    format(name=pipeline.name)
                )
            os.unlink(filename)

        # Initialize pipeline state to "just started".
        pipeline.init()

        # Write the new, empty state file
        with open(filename, 'w+') as f:
            f.write(pipeline.serialize())

        # "Continue", until step 1.
        return CONTINUE

    @classmethod
    def _handle_continue(cls, pipeline, *, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(
                'Pipeline “{}” not started, hence you cannot “continue” it. Are you looking for `medikit pipeline {name} start`?'.
                format(name=pipeline.name)
            )

        # XXX TODO add a lock file during the step and unlock at the end.
        with open(filename) as f:
            pipeline.unserialize(f.read())

        try:
            step = pipeline.next()
            name, current, size, descr = pipeline.name, pipeline.current, len(pipeline), str(step)
            logger.info(
                term.black(' » ').join(
                    (
                        term.lightblue('{} ({}/{})'.format(name.upper(), current, size)),
                        term.yellow('⇩ BEGIN'),
                        term.lightblack(descr),
                    )
                )
            )
            step.run(pipeline.meta)
            if step.complete:
                logger.info(
                    term.black(' » ')
                    .join((
                        term.lightblue('{} ({}/{})'.format(name.upper(), current, size)),
                        term.green('SUCCESS'),
                    )) + '\n'
                )
            else:
                logger.info(
                    term.black(' » ')
                    .join((
                        term.lightblue('{} ({}/{})'.format(name.upper(), current, size)),
                        term.red('FAILED'),
                    )) + '\n'
                )
                return

        except StopIteration:
            return COMPLETE

        with open(filename, 'w+') as f:
            f.write(pipeline.serialize())

        return CONTINUE

    @classmethod
    def _handle_abort(cls, pipeline, *, filename):
        assert os.path.exists(filename)
        try:
            with open(filename) as f:
                pipeline.unserialize(f.read())
            pipeline.abort()
        finally:
            os.unlink(filename)
