"""
Adds docker capabilities to your package, using either "docker build" or "rocker build" to create an image containing
your code, in a fully functionnal python virtualenv.

"""
from argparse import Namespace

from medikit.events import subscribe
from medikit.feature import Feature
from medikit.feature.make import which
from medikit.structs import Script

DEFAULT_NAME = '$(shell echo $(PACKAGE) | tr A-Z a-z)'

DOCKER = 'docker'
ROCKER = 'rocker'


class DockerConfig(Feature.Config):
    def __init__(self):
        self._registry = None
        self._user = None
        self._name = DEFAULT_NAME

        self._build_file = None
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

    @property
    def build_file(self):
        if self._build_file is None:
            return self.builder.title() + 'file'
        return self._build_file

    @build_file.setter
    def build_file(self, value):
        self._build_file = value

    def _get_default_variables(self):
        return dict(
            DOCKER=which('docker'),
            DOCKER_BUILD='$(DOCKER) image build',
            DOCKER_BUILD_OPTIONS='--build-arg IMAGE=$(DOCKER_IMAGE) --build-arg TAG=$(DOCKER_TAG)',
            DOCKER_PUSH='$(DOCKER) image push',
            DOCKER_PUSH_OPTIONS='',
            DOCKER_RUN='$(DOCKER) run',
            DOCKER_RUN_COMMAND='',
            DOCKER_RUN_NAME='$(PACKAGE)_run',
            DOCKER_RUN_OPTIONS='',
            DOCKER_RUN_PORTS='',
        )

    def _get_default_image_variables(self):
        return dict(
            DOCKER_BUILD_FILE='',  # will be set at runtime.
            DOCKER_IMAGE='',  # will be set at runtime, see #71.
            DOCKER_TAG='$(VERSION)',
        )

    def disable_builder(self):
        self.builder = None
        self._variables = []
        self.scripts = Namespace()

    def use_default_builder(self):
        self.builder = DOCKER

        self._variables = [
            self._get_default_variables(),
            self._get_default_image_variables(),
        ]

        self.scripts = Namespace(
            build=Script(
                '$(DOCKER_BUILD) -f $(DOCKER_BUILD_FILE) $(DOCKER_BUILD_OPTIONS) -t $(DOCKER_IMAGE):$(DOCKER_TAG) .',
                doc='Build a docker image.',
            ),
            push=Script(
                '$(DOCKER_PUSH) $(DOCKER_PUSH_OPTIONS) $(DOCKER_IMAGE):$(DOCKER_TAG)',
                doc='Push docker image to remote registry.',
            ),
            run=Script(
                '$(DOCKER_RUN) $(DOCKER_RUN_OPTIONS) --interactive --tty --rm --name=$(DOCKER_NAME) $(DOCKER_RUN_PORTS) $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_RUN_COMMAND)',
                doc='Run the default entry point in a container based on our docker image.',
            ),
            shell=Script(
                'DOCKER_RUN_COMMAND="/bin/bash" $(MAKE) docker-run',
                doc='Run bash in a container based on our docker image.',
            ),
        )

    def use_rocker_builder(self):
        self.use_default_builder()

        self.builder = ROCKER

        self._variables = [
            self._get_default_variables(),
            self._get_default_image_variables(),
            dict(
                ROCKER=which('rocker'),
                ROCKER_BUILD='$(ROCKER) build',
                ROCKER_BUILD_OPTIONS='',
                ROCKER_BUILD_VARIABLES=
                '--var DOCKER_IMAGE=$(DOCKER_IMAGE) --var DOCKER_TAG=$(DOCKER_TAG) --var PYTHON_REQUIREMENTS_FILE=requirements-prod.txt',
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

        # Set DOCKER_IMAGE at runtime, see #71.
        if ('DOCKER_BUILD_FILE' in event.makefile) and not event.makefile['DOCKER_BUILD_FILE']:
            event.makefile['DOCKER_BUILD_FILE'] = docker_config.build_file
        if ('DOCKER_IMAGE' in event.makefile) and not event.makefile['DOCKER_IMAGE']:
            event.makefile['DOCKER_IMAGE'] = docker_config.image

        # Targets
        for script_name, script_content in sorted(docker_config.scripts.__dict__.items()):
            event.makefile.add_target(
                'docker-' + script_name,
                script_content,
                phony=True,
                doc=script_content.doc,
            )

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
            self.render_file_inline(
                docker_config.compose_file, '''
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
            '''
            )

        if docker_config.builder == DOCKER:
            self.render_file_inline(docker_config.build_file, '''
                FROM python:3
            ''')
        elif docker_config.builder == ROCKER:
            self.render_file_inline(
                docker_config.build_file, '''
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
        elif docker_config.builder is not None:
            raise NotImplementedError('Unknown builder {}'.format(docker_config.builder))
