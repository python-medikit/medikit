# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

from edgy.project.events import subscribe
from . import Feature


class DockerFeature(Feature):
    @subscribe('edgy.project.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile['DOCKER'] = "$(shell which docker)"
        event.makefile['DOCKER_PUSH'] = "$(DOCKER) push"
        event.makefile['DOCKER_REGISTRY'] = ""
        event.makefile['DOCKER_NAME'] = ""
        event.makefile['DOCKER_IMAGE'] = ""


__feature__ = DockerFeature
