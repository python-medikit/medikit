# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import datetime

import itertools
import six
import textwrap

from collections import deque
from edgy.event import Event

from . import Feature, HIGH_PRIORITY


@six.python_2_unicode_compatible
class Makefile(object):
    @property
    def targets(self):
        for key in self._target_order:
            yield key, self._target_values[key]

    def __init__(self):
        self._env_order, self._env_values = deque(), {}
        self._target_order, self._target_values = deque(), {}
        self.phony = set()

    def __delitem__(self, key):
        self._env_order.remove(key)
        del self._env_values[key]

    def __getitem__(self, item):
        return self._env_values[item]

    def __setitem__(self, key, value):
        self._env_values[key] = value
        if not key in self._env_order:
            self._env_order.append(key)

    def __iter__(self):
        for key in self._env_order:
            yield key, self._env_values[key]

    def __len__(self):
        return len(self._env_order)

    def __str__(self):
        content = [
            '# This file has been auto-generated.',
            '# All manual changes may be lost, see Projectfile.',
            '#',
            '# Date: ' + six.text_type(datetime.datetime.now()),
            '',
        ]

        if len(self):
            for k, v in self:
                content.append('{} ?= {}'.format(k, v))
            content.append('')

        if len(self.phony):
            content.append('.PHONY: ' + ' '.join(sorted(self.phony)))
            content.append('')

        for target, details in self.targets:
            deps, rule, doc = details
            if doc:
                for line in doc.split('\n'):
                    content.append('# ' + line)
            content.append('{}: {}'.format(target, ' '.join(deps)).strip())

            script = textwrap.dedent(str(rule)).strip()

            for line in script.split('\n'):
                content.append('\t' + line)

            content.append('')

        return '\n'.join(content)

    def add_target(self, target, rule, deps=None, phony=False, first=False, doc=None):
        self._target_values[target] = (
            deps or list(),
            rule,
            textwrap.dedent(doc or '').strip(),
        )
        self._target_order.appendleft(target) if first else self._target_order.append(target)

        if phony:
            self.phony.add(target)

    def get_target(self, target):
        return self._target_values[target][1]

    def set_deps(self, target, deps=None):
        self._target_values[target] = (
            deps or list(),
            self._target_values[target][1],
            self._target_values[target][2],
        )

    def setleft(self, key, value):
        self._env_values[key] = value
        if not key in self._env_order:
            self._env_order.appendleft(key)

    def updateleft(self, *lst):
        for key, value in reversed(lst):
            self.setleft(key, value)


class MakefileEvent(Event):
    def __init__(self, package_name, makefile):
        self.package_name = package_name
        self.makefile = makefile
        super(MakefileEvent, self).__init__()


@six.python_2_unicode_compatible
class InstallScript(object):
    before_install = []
    install = [
        '$(PIP) install -Ur $(PYTHON_REQUIREMENTS_FILE)'
    ]
    after_install = []

    def __str__(self):
        return '\n'.join(
            itertools.chain(
                ['if [ -z "$(QUICK)" ]; then \\'],
                list(map(
                    lambda x: '    {} ; \\'.format(x),
                    itertools.chain(
                        self.before_install,
                        self.install,
                        self.after_install
                    )
                )),
                ['fi']
            )
        )


class MakeFeature(Feature):
    def configure(self):
        self.makefile = Makefile()
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=HIGH_PRIORITY)

    def on_start(self, event):
        for k in event.variables:
            self.makefile[k.upper()] = event.variables[k]

        self.makefile.updateleft(
            ('PYTHON', '$(shell which python)',),
            ('PYTHON_BASENAME', '$(shell basename $(PYTHON))',),
            ('PYTHON_REQUIREMENTS_FILE', 'requirements.txt',),
            ('QUICK', '',),
        )

        self.makefile['PIP'] = '$(VIRTUAL_ENV)/bin/pip'

        # Install
        self.makefile.add_target('install', InstallScript(), deps=('$(VIRTUAL_ENV)',), phony=True, doc='''
            Installs the local project dependencies.
        ''')

        # Virtualenv
        self.makefile.add_target('$(VIRTUAL_ENV)', '''
            virtualenv -p $(PYTHON) $(VIRTUAL_ENV)
            $(PIP) install -U pip\>=8.0,\<9.0 wheel\>=0.24,\<1.0
            ln -fs $(VIRTUAL_ENV)/bin/activate activate-$(PYTHON_BASENAME)
        ''', doc='''
            Setup the local virtualenv.
        ''')

        # Housekeeping
        self.makefile.add_target('clean', '''
            rm -rf $(VIRTUAL_ENV)
        ''', phony=True)

        self.dispatcher.dispatch(__name__ + '.on_generate', MakefileEvent(event.setup['name'], self.makefile))

        self.render_file_inline('Makefile', self.makefile.__str__(), override=True)


__feature__ = MakeFeature
