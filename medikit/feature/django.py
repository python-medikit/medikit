"""
The «django» feature adds the django framework to your project.

"""

import os
import random

from medikit.events import subscribe

from . import Feature, SUPPORT_PRIORITY

random = random.SystemRandom()


def generate_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
    return ''.join(random.choice(chars) for i in range(64))


class DjangoConfig(Feature.Config):
    """ Configuration class for the “django” feature. """

    use_jinja2 = True
    """Whether or not to use the Jinja2 templating language."""

    use_whitenoise = True
    """Whether or not to use Whitenoise for the static files."""

    version = '==2.0b1'
    """Which django version requirement do you want?"""

    def __init__(self):
        self.use_jinja2 = self.use_jinja2
        self.use_whitenoise = self.use_whitenoise
        self.version = self.version


class DjangoFeature(Feature):
    requires = {'python'}

    Config = DjangoConfig

    @subscribe('medikit.feature.python.on_generate')
    def on_python_generate(self, event):
        event.config['python'].add_requirements(
            'django ' + event.config['django'].version,
            dev=[
                'django-extensions >=1.9,<1.10',
                'django-debug-toolbar >=1.8,<1.9',
            ],
            prod=[
                'gunicorn ==19.7.1',
            ],
        )

        if event.config['django'].use_jinja2:
            event.config['python'].add_requirements('Jinja2 >=2.10,<2.11', )

        if event.config['django'].use_whitenoise:
            event.config['python'].add_requirements(
                'brotli >=0.6,<0.7',
                'whitenoise ==4.0b4',
            )

        event.config['python'].add_requirements('django-extensions >=1.9,<1.10', )

    @subscribe('medikit.feature.make.on_generate', priority=SUPPORT_PRIORITY)
    def on_make_generate(self, event):
        makefile = event.makefile
        makefile['DJANGO'] = '$(PYTHON) manage.py'
        makefile.add_target('runserver', '''$(DJANGO) runserver''', deps=('install-dev',), phony=True)

    @subscribe('medikit.on_start')
    def on_start(self, event):

        context = {
            **event.config['python'].get_setup(),
            'config_package': 'config',
            'secret_key': generate_secret_key(),
            'use_jinja2': event.config['django'].use_jinja2,
            'use_whitenoise': event.config['django'].use_whitenoise,
        }

        name = context['name']

        # Create configuration
        config_path = 'config'
        if not os.path.exists(config_path):
            os.makedirs(config_path)

        self.render_file('manage.py', 'django/manage.py.j2', context, executable=True, force_python=True)
        self.render_file(os.path.join(config_path, 'settings.py'), 'django/settings.py.j2', context, force_python=True)
        self.render_file(os.path.join(config_path, 'urls.py'), 'django/urls.py.j2', context, force_python=True)
        self.render_file(os.path.join(config_path, 'wsgi.py'), 'django/wsgi.py.j2', context, force_python=True)

        self.dispatcher.dispatch('medikit.feature.django.on_configure')

        if context['use_jinja2']:
            templates_dir = os.path.join(name, 'jinja2', context['name'])
            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir)

        static_dir = os.path.join(name, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        self.render_empty_files(os.path.join(static_dir, 'favicon.ico'))

    '''
    XXX todo use yapf to adjust settings (for example, add some apps).
    @subscribe('medikit.feature.django.on_configure')
    def on_django_configure(self, event):
        original_source, newline, encoding = yapf_api.ReadFile('config/settings.py')
        print(original_source, newline, encoding)
        reformatted_code, encoding, has_change = yapf_api.FormatFile(
            'config/settings.py',
            in_place=True,
        )
        print(reformatted_code, encoding, has_change)
    '''


__feature__ = DjangoFeature
