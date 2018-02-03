import logging
import os
from contextlib import ContextDecorator

from jinja2 import Environment, PackageLoader, Template
from medikit import settings
from medikit.events import attach_subscriptions
from medikit.file import File
from medikit.settings import DEFAULT_FEATURES
from medikit.utils import is_identifier, format_file_content
from yapf import yapf_api

from mondrian import term

ABSOLUTE_PRIORITY = -100
HIGH_PRIORITY = -80
MEDIUM_PRIORITY = -60
LOW_PRIORITY = -60
SUPPORT_PRIORITY = -20
LAST_PRIORITY = 100


class Feature(object):
    _jinja_environment = None

    requires = set()
    conflicts = set()

    file_type = staticmethod(File)

    class Config(ContextDecorator):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

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
            term.bold(term.red('W!') if override else term.green('W?')), target, '({} bytes)'.format(len(content))
        )

    def render(self, template, context=None):
        context = context or {}
        os.path.join(os.path.dirname(__file__), 'template')
        return self.jinja.get_template(template).render(**(context or {}))

    def render_file(self, target, template, context=None, *, executable=False, override=False, force_python=False):
        with self.file(target, executable=executable, override=override) as f:
            content = format_file_content(self.render(template, context))
            if force_python or target.endswith('.py'):
                content, modified = yapf_api.FormatCode(content, filename=target)
            f.write(content)
            self._log_file(target, override, content)

    def render_file_inline(self, target, template_string, context=None, override=False, force_python=False):
        with self.file(target, override=override) as f:
            content = format_file_content(Template(template_string).render(**(context or {})))
            if force_python or target.endswith('.py'):
                content, modified = yapf_api.FormatCode(
                    content, filename=target, style_config=settings.YAPF_STYLE_CONFIG
                )
            f.write(content)
            self._log_file(target, override, content)

    def render_empty_files(self, *targets, **kwargs):
        override = kwargs.pop('override', False)
        for target in targets:
            with self.file(target, override=override) as f:
                self._log_file(target, override)


class ProjectInitializer(Feature):
    def __init__(self, dispatcher, options):
        super().__init__(dispatcher)
        self.options = options

    def execute(self):
        context = {}

        if self.options.get('name'):
            if not is_identifier(self.options['name']):
                raise RuntimeError('Invalid package name {!r}.'.format(self.options['name']))
            context['name'] = self.options['name']
            logging.info('name = %s', context['name'])
        else:
            context['name'] = input('Name: ')
            while not is_identifier(context['name']):
                logging.error('Invalid name. Please only use valid python identifiers.')
                context['name'] = input('Name: ')

        if self.options.get('description'):
            context['description'] = self.options['description']
        else:
            context['description'] = input('Description: ')

        if self.options.get('license'):
            context['license'] = self.options['license']
        else:
            context['license'
                    ] = input('License [Apache License, Version 2.0]: ').strip() or 'Apache License, Version 2.0'

        context['url'] = ''
        context['download_url'] = ''
        context['author'] = ''
        context['author_email'] = ''

        context['features'] = DEFAULT_FEATURES
        if self.options.get('features'):
            context['features'] = context['features'].union(self.options['features'])

        context['requirements'] = self.options.get('requirements', [])

        self.render_file('Projectfile', 'Projectfile.j2', context, override=True, force_python=True)
