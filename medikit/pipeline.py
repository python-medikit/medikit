"""
Pipelines are a way to describe a simple step-by-step process, for example the release process.

"""
import datetime
import json
import logging

logger = logging.getLogger(__name__)


def get_identity(step):
    return str(step)


class Pipeline:
    """
    Class to configure a pipeline.

    """

    def __init__(self):
        self.steps = []

    def add(self, step, *, before=None):
        if before:
            insert_at = None
            for i, _step in enumerate(self.steps):
                if before == get_identity(_step):
                    insert_at = i
                    break
            if not insert_at:
                raise ValueError(
                    'Step with identity {!r} not found. Try "show" subcommand to list identities.'.format(before)
                )
            self.steps = self.steps[:insert_at] + [step] + self.steps[insert_at:]
        else:
            self.steps.append(step)
        return self

    def remove(self, identity):
        for i in range(len(self.steps)):
            if identity == get_identity(self.steps[i]):
                del self.steps[i]
                break

    def __iter__(self):
        yield from self.steps


class ConfiguredPipeline:
    """
    Used to actually load run and persist a configured pipeline.
    """

    def __init__(self, name, pipeline, config=None):
        self.name = name
        self.steps = pipeline.steps
        self.meta = {"created": str(datetime.datetime.now())}
        self.config = config

    def __iter__(self):
        yield from self.steps

    def __len__(self):
        return len(self.steps)

    def init(self):
        for step in self.steps:
            step.init()

    def next(self):
        for step in self.steps:
            if not step.complete:
                return step
        raise StopIteration("No step left.")

    @property
    def current(self):
        for i, step in enumerate(self.steps):
            if not step.complete:
                return i + 1
        return len(self)

    def abort(self):
        for step in self.steps:
            step.abort()

    def serialize(self):
        return json.dumps(
            {
                "meta": {**self.meta, "updated": str(datetime.datetime.now())},
                "steps": [[get_identity(step), step.get_state()] for step in self.steps],
            },
            indent=4,
        )

    def unserialize(self, serialized):
        serialized = json.loads(serialized)
        self.meta = serialized.get("meta", {})
        steps = serialized.get("steps", [])
        if len(steps) != len(self.steps):
            raise IOError("Invalid pipeline state storage.")
        for (identity, state), step in zip(steps, self.steps):
            if get_identity(step) != identity:
                raise IOError("Mismatch on step identity.")
            step.set_state(state)
            step.config = self.config
