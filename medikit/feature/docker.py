"""
Not yet functional.
"""
from argparse import Namespace

from medikit.events import subscribe
from medikit.feature import Feature
from medikit.structs import Script

DEFAULT_NAME = '$(shell echo $(PACKAGE) | tr A-Z a-z)'

DOCKER = 'docker'
ROCKER = 'rocker'


class DockerConfig(Feature.Config):
    def __init__(self):
        self._registry = None
        self._user = None
        self._name = DEFAULT_NAME

        self._compose_file = None

        self.use_default_builder()

    def set_remote(self, registry=None, user=None, name=DEFAULT_NAME):
        self._registry = registry
        self._user = user
        self._name = name

    @property
    def compose_file(self):
        if self._compose_file is None:
            return 'docker-compose.yml'
        if self._compose_file is False:
            return None
        return self._compose_file

    @compose_file.setter
    def compose_file(self, value):
        self._compose_file = value

    def _get_default_variables(self):
        return dict(
            DOCKER='$(shell which docker)',
            DOCKER_BUILD='$(DOCKER) build',
            DOCKER_BUILD_OPTIONS='',
            DOCKER_PUSH='$(DOCKER) push',
            DOCKER_PUSH_OPTIONS='',
            DOCKER_RUN='$(DOCKER) run',
            DOCKER_RUN_COMMAND='',
            DOCKER_RUN_OPTIONS='',
        )

    def _get_default_image_variables(self):
        return dict(
            DOCKER_IMAGE=self.image,
            DOCKER_TAG='$(VERSION)',
        )

    def use_default_builder(self):
        self.builder = DOCKER

        self._variables = [
            self._get_default_variables(),
            self._get_default_image_variables(),
        ]

        self.scripts = Namespace(
            build=Script('$(DOCKER_BUILD) $(DOCKER_BUILD_OPTIONS) -t $(DOCKER_IMAGE):$(DOCKER_TAG) .'),
            push=Script('$(DOCKER_PUSH) $(DOCKER_PUSH_OPTIONS) $(DOCKER_IMAGE):$(DOCKER_TAG)'),
            run=Script(
                '$(DOCKER_RUN) $(DOCKER_RUN_OPTIONS) --interactive --tty --rm --name=$(PACKAGE)_run -p 8000:8000 $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_RUN_COMMAND)'
            ),
            shell=Script('DOCKER_RUN_COMMAND="/bin/bash" $(MAKE) docker-run'),
        )

    def use_rocker_builder(self):
        self.builder = ROCKER

        self._variables = [
            self._get_default_variables(),
            self._get_default_image_variables(),
            dict(
                ROCKER='$(shell which rocker)',
                ROCKER_BUILD='$(ROCKER) build',
                ROCKER_BUILD_OPTIONS='',
                ROCKER_BUILD_VARIABLES='--var DOCKER_IMAGE=$(DOCKER_IMAGE) --var DOCKER_TAG=$(DOCKER_TAG) --var PYTHON_REQUIREMENTS_FILE=requirements-prod.txt',
            ),
        ]

        self.scripts.build.set('$(ROCKER_BUILD) $(ROCKER_BUILD_OPTIONS) $(ROCKER_BUILD_VARIABLES) .')
        self.scripts.push.set('ROCKER_BUILD_OPTIONS="$(ROCKER_BUILD_OPTIONS) --push" $(MAKE) docker-build')

    @property
    def variables(self):
        for variables in self._variables:
            yield from sorted(variables.items())

    @property
    def image(self):
        return '/'.join(filter(None, (self._registry, self._user, self._name)))


class DockerFeature(Feature):
    Config = DockerConfig

    @subscribe('medikit.feature.make.on_generate', priority=-1)
    def on_make_generate(self, event):
        docker_config = event.config['docker']

        for var, val in docker_config.variables:
            event.makefile[var] = val

        # Targets
        event.makefile.add_target('docker-build', docker_config.scripts.build, phony=True)
        event.makefile.add_target('docker-push', docker_config.scripts.push, phony=True)
        event.makefile.add_target('docker-run', docker_config.scripts.run, phony=True)
        event.makefile.add_target('docker-shell', docker_config.scripts.shell, phony=True)

    @subscribe('medikit.on_end')
    def on_end(self, event):
        docker_config = event.config['docker']

        self.render_file_inline(
            '.dockerignore', '''
            **/__pycache__
            *.egg-info
            .cache
            .git
            .idea
            /Dockerfile
            /Projectfile
            /Rockerfile
            node_modules
            static
        ''', event.variables
        )

        if docker_config.compose_file:
            self.render_file_inline(docker_config.compose_file, '''
                version: '3'

                volumes:
                
                #   postgres_data: {}

                services:
                
                #   postgres:
                #     image: postgres:10
                #     ports:
                #       - 5432:5432
                #     volumes:
                #       - postgres_data:/var/lib/postgresql/data
            ''')

        if docker_config.builder == DOCKER:
            self.render_file_inline('Dockerfile', '''
                FROM python:3
            ''')
        elif docker_config.builder == ROCKER:
            self.render_file_inline(
                'Rockerfile', '''
                FROM python:3
                 
                # Mount cache volume to keep cache persistent from one build to another
                MOUNT /app/.cache
                WORKDIR /app
                
                # Create application user
                RUN useradd --home-dir /app --group www-data app \
                 && pip install -U pip wheel virtualenv \
                 && mkdir /env \
                 && chown app:www-data -R /app /env 
                 
                # Add and install python requirements in a virtualenv
                USER app
                RUN virtualenv -p python3 /env/
                ADD setup.py *.txt /app/
                RUN /env/bin/pip install -r {{ '{{ .PYTHON_REQUIREMENTS_FILE }}' }}

                # Add everything else
                USER root
                ADD . /app
                # IMPORT /static /app
                # IMPORT /assets.json /app
                RUN chown app:www-data -R /app

                # Entrypoint
                USER app
                CMD /env/bin/gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 4
                
                PUSH {{ '{{ .DOCKER_IMAGE }}:{{ .DOCKER_TAG }}' }}
            '''
            )
        else:
            raise NotImplementedError('Unknown builder {}'.format(docker_config.builder))


__feature__ = DockerFeature
