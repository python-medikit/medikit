import os

from medikit.events import subscribe
from . import Feature, SUPPORT_PRIORITY


class PytestFeature(Feature):
    # TODO: http://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner

    requires = {'python'}
    conflicts = {'nosetests'}

    @subscribe('medikit.feature.python.on_generate')
    def on_python_generate(self, event):
        event.config['python'].add_requirements(
            dev=['coverage ~=4.4', 'pytest ~=3.4', 'pytest-cov ~=2.5', 'pytest-sugar ~=0.9.1']
        )

    @subscribe('medikit.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile
        makefile['PYTEST'] = '$(PYTHON_DIRNAME)/pytest'
        makefile['PYTEST_OPTIONS'] = '--capture=no --cov=$(PACKAGE) --cov-report html'.format(
            path=event.package_name.replace('.', os.sep)
        )
        makefile.add_target(
            'test', '''
            $(PYTEST) $(PYTEST_OPTIONS) tests
        ''', deps=('install-dev', ), phony=True
        )

    @subscribe('medikit.on_start', priority=SUPPORT_PRIORITY)
    def on_start(self, event):
        tests_dir = 'tests'
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir)

        gitkeep_file = os.path.join(tests_dir, '.gitkeep')

        if not os.path.exists(gitkeep_file):
            self.render_empty_files(gitkeep_file)

        self.render_file('.coveragerc', 'pytest/coveragerc.j2')
        self.render_file('.travis.yml', 'pytest/travis.yml.j2')


__feature__ = PytestFeature
