from __future__ import absolute_import

import os
import textwrap

import six
from blessings import Terminal
from edgy.project.events import attach_subscriptions
from edgy.project.file import File
from edgy.project.settings import DEFAULT_FEATURES
from edgy.project.util import format_file_content
from jinja2 import Environment, PackageLoader, Template

ABSOLUTE_PRIORITY = -100
HIGH_PRIORITY = -80
MEDIUM_PRIORITY = -60
LOW_PRIORITY = -60
SUPPORT_PRIORITY = -20
LAST_PRIORITY = 100

try:
    input = raw_input  # pylint: disable=raw_input-builtin
except NameError:
    input = input  # pylint: disable=input-builtin

term = Terminal()


class Feature(object):
    _jinja_environment = None

    requires = set()
    conflicts = set()

    file_type = staticmethod(File)

    def __init__(self, dispatcher):
        """

        :param LoggingDispatcher dispatcher:
        """
        self.dispatcher = dispatcher
        self.configure()
        attach_subscriptions(self, self.dispatcher)

    def configure(self):
        pass

    def file(self, *args, **kwargs):
        return self.file_type(self.dispatcher, *args, **kwargs)

    @property
    def __name__(self):
        return type(self).__name__

    @property
    def __shortname__(self):
        return self.__name__.replace('Feature', '').lower()

    @property
    def jinja(self):
        if type(self)._jinja_environment is None:
            type(self)._jinja_environment = Environment(loader=PackageLoader(__name__, 'template'))
        return type(self)._jinja_environment

    def _log_file(self, target, override, content=()):
        self.dispatcher.info(
            term.bold(term.red('W!') if override else term.green('W?')), target, '({} bytes)'.format(len(content)))

    def render(self, template, context=None):
        context = context or {}
        os.path.join(os.path.dirname(__file__), 'template')
        return self.jinja.get_template(template).render(**(context or {}))

    def render_file(self, target, template, context=None, override=False):
        with self.file(target, override=override) as f:
            content = format_file_content(self.render(template, context))
            f.write(content)
            self._log_file(target, override, content)

    def render_file_inline(self, target, template_string, context=None, override=False):
        with self.file(target, override=override) as f:
            content = format_file_content(Template(template_string).render(**(context or {})))
            f.write(content)
            self._log_file(target, override, content)

    def render_empty_files(self, *targets, **kwargs):
        override = kwargs.pop('override', False)
        for target in targets:
            with self.file(target, override=override) as f:
                self._log_file(target, override)


class ProjectInitializer(Feature):
    def execute(self):
        context = {}

        context['name'] = input('Name: ')
        context['description'] = input('Description: ')
        context['license'] = input('License [Apache License, Version 2.0]: ').strip() or 'Apache License, Version 2.0'

        context['url'] = ''
        context['download_url'] = ''

        context['author'] = ''
        context['author_email'] = ''

        context['features'] = DEFAULT_FEATURES
        context['install_requires'] = []
        context['extras_require'] = {
            'dev': [
                'coverage >=4.0,<4.2',
                'mock >=2.0,<2.1',
                'nose >=1.3,<1.4',
                'pylint >=1.6,<1.7',
                'pytest >=2.9,<2.10',
                'pytest-cov >=2.3,<2.4',
                'sphinx',
                'sphinx_rtd_theme',
            ]
        }
        context['entry_points'] = {}

        self.render_file('Projectfile', 'Projectfile.j2', context, override=True)


@six.python_2_unicode_compatible
class Script(object):
    def __init__(self, script=None):
        self.script = self.parse_script(script)

    def parse_script(self, script):
        if not script:
            return []
        script = textwrap.dedent(str(script)).strip()
        return script.split('\n')

    def __iter__(self):
        for line in self.script:
            yield line

    def __str__(self):
        return '\n'.join(self.__iter__())
