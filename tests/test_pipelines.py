import pytest

from medikit.steps import Step


class FailingStep(Step):
    def run(self, meta):
        self.exec('false')
        self.set_complete()

# Issue #64: A failing shell command execution should not be considered as a success.
def test_failing_step():
    step = FailingStep()
    with pytest.raises(RuntimeError):
        step.run({})
    assert not step.complete
