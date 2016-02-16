from __future__ import absolute_import

import os

from jinja2 import Environment, PackageLoader
from jinja2 import Template

from edgy.project.file import File
from edgy.project.util import format_file_content

ABSOLUTE_PRIORITY = -100
HIGH_PRIORITY = -80
MEDIUM_PRIORITY = -60
LOW_PRIORITY = -60
SUPPORT_PRIORITY = -20
LAST_PRIORITY = 100

class Feature(object):
    _jinja_environment = None

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.configure()

    def configure(self):
        pass

    def file(self, *args, **kwargs):
        return File(self.dispatcher, *args, **kwargs)

    @property
    def jinja(self):
        if type(self)._jinja_environment is None:
            type(self)._jinja_environemnt = Environment(
                loader=PackageLoader(__name__, 'template')
            )
        return type(self)._jinja_environemnt

    def render(self, template, context=None):
        context = context or {}
        os.path.join(os.path.dirname(__file__), 'template')
        return self.jinja.get_template(template).render(**(context or {}))

    def render_file(self, target, template, context=None, override=False):
        with self.file(target, override=override) as f:
            f.write(format_file_content(self.render(template, context)))

    def render_file_inline(self, target, template_string, context=None, override=False):
        with self.file(target, override=override) as f:
            f.write(format_file_content(Template(template_string).render(**(context or {}))))

    def render_empty_files(self, *targets, **kwargs):
        for target in targets:
            with self.file(target, override=kwargs.pop('override', False)) as f:
                pass
