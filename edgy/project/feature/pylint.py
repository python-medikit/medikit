# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.project.events import subscribe

from . import Feature, SUPPORT_PRIORITY


class PylintFeature(Feature):
    requires = ['python']

    @subscribe('edgy.project.feature.python.on_generate')
    def on_python_generate(self, event):
        event.config['python'].add_requirements(dev=['pylint >=1.6,<1.7'])

    @subscribe('edgy.project.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile
        makefile.add_target(
            'lint',
            '''
            $(PYTHON_DIRNAME)/pylint --py3k $(PACKAGE) -f html > pylint.html
        '''.format(name=event.package_name),
            deps=('install-dev', ),
            phony=True
        )

    @subscribe('edgy.project.feature.python.on_generate', priority=SUPPORT_PRIORITY)
    def on_python_generate(self, event):
        event.files['requirements'] = '\n'.join((event.files['requirements'], 'pylint >=1.4,<1.5', ))


__feature__ = PylintFeature
