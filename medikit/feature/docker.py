"""
Not yet functional.
"""
from medikit.events import subscribe
from medikit.feature import Feature

DEFAULT_NAME = '$(shell echo $(PACKAGE) | tr A-Z a-z)'


class DockerConfig(Feature.Config):
    def __init__(self):
        self._registry = None
        self._user = None
        self._name = DEFAULT_NAME

    def set_remote(self, registry=None, user=None, name=DEFAULT_NAME):
        self._registry = registry
        self._user = user
        self._name = name

    @property
    def image(self):
        return '/'.join(filter(None, (self._registry, self._user, self._name)))


class DockerFeature(Feature):
    Config = DockerConfig

    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        docker_config = event.config['docker']

        # Commands
        event.makefile['DOCKER'] = '$(shell which docker)'
        event.makefile['DOCKER_BUILD'] = '$(DOCKER) build'
        event.makefile['DOCKER_BUILD_OPTIONS'] = ''
        event.makefile['DOCKER_PUSH'] = '$(DOCKER) push'
        event.makefile['DOCKER_PUSH_OPTIONS'] = ''
        event.makefile['DOCKER_RUN'] = '$(DOCKER) run'
        event.makefile['DOCKER_RUN_OPTIONS'] = ''

        # Variables
        event.makefile['DOCKER_IMAGE'] = docker_config.image
        event.makefile['DOCKER_TAG'] = '$(VERSION)'

        # Targets
        event.makefile.add_target(
            'docker-build',
            '''
            $(DOCKER_BUILD) $(DOCKER_BUILD_OPTIONS) -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
        ''',
            phony=True
        )

        event.makefile.add_target(
            'docker-push',
            '''
            $(DOCKER_PUSH) $(DOCKER_PUSH_OPTIONS) $(DOCKER_IMAGE):$(DOCKER_TAG)
        ''',
            phony=True
        )

        event.makefile.add_target(
            'docker-run',
            '''
            $(DOCKER_RUN) -p 8080:8080 $(DOCKER_IMAGE):$(DOCKER_TAG)
        ''',
            phony=True
        )

    @subscribe('medikit.on_end')
    def on_end(self, event):
        self.render_file_inline(
            '.dockerignore', '''
            **/__pycache__
            *.egg-info
            .git
            .idea
            assets.json
            config/docker
            http_cache.sqlite
            node_modules
            static
            static
            touit/assets/dist
        ''', event.variables
        )

        self.render_file_inline(
            'docker-compose.yml', '''
            version: '3'

            volumes:
            
            #   postgres_data: {}
            #   rabbitmq_data: {}

            services:
            
            #   postgres:
            #     image: postgres:10
            #     ports:
            #       - 5432:5432
            #     volumes:
            #       - postgres_data:/var/lib/postgresql/data

            #   rabbitmq:
            #     image: rabbitmq:3
            #     ports:
            #      - 5672:5672
            #    volumes:
            #      - rabbitmq_data:/var/lib/rabbitmq
        
        '''
        )

        self.render_file_inline('Dockerfile', '''
            FROM python:3
        ''')


__feature__ = DockerFeature
