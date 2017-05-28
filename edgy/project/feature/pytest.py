# coding: utf-8
"""
TODO:

* http://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
from edgy.project.events import subscribe

from . import Feature, SUPPORT_PRIORITY


class PytestFeature(Feature):
    requires = {'python'}
    conflicts = {'nosetests'}

    @subscribe('edgy.project.feature.python.on_generate')
    def on_python_generate(self, event):
        event.config['python'].add_requirements(
            dev=[
                'coverage >=4.4,<5.0',
                'pytest >=3.1,<4.0',
                'pytest-cov >=2.5,<3.0',
            ]
        )

    @subscribe('edgy.project.feature.make.on_generate', priority=SUPPORT_PRIORITY)
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

    @subscribe('edgy.project.on_start', priority=SUPPORT_PRIORITY)
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
