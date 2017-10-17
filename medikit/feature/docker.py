"""
Not yet functional.
"""
from medikit.events import subscribe
from medikit.feature import Feature


class DockerFeature(Feature):
    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile['DOCKER'] = "$(shell which docker)"
        event.makefile['DOCKER_PUSH'] = "$(DOCKER) push"
        event.makefile['DOCKER_REGISTRY'] = ""
        event.makefile['DOCKER_NAME'] = ""
        event.makefile['DOCKER_IMAGE'] = ""


__feature__ = DockerFeature
