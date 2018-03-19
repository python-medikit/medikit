"""
Setup make targets to rollout and rollback this project as a deployment onto a Kubernetes cluster.

"""
import json

from medikit.events import subscribe
from medikit.feature import Feature
from medikit.feature.make import which


class KubeConfig(Feature.Config):
    def __init__(self):
        self._targets = list()
        self._targets_data = dict()

    def add_target(self, name, *, patch):
        if name in self._targets:
            raise ValueError('Kubernetes target {} already defined.'.format(name))
        self._targets.append(name)
        self._targets_data[name] = patch

    def get_targets(self):
        for target in self._targets:
            yield target, self._targets_data[target]


class KubeFeature(Feature):
    Config = KubeConfig

    requires = {'docker'}

    @subscribe('medikit.feature.make.on_generate', priority=-1)
    def on_make_generate(self, event):
        kube_config = event.config['kube']

        event.makefile['KUBECTL'] = which('kubectl')
        event.makefile['KUBECTL_OPTIONS'] = ''
        event.makefile['KUBECONFIG'] = ''
        event.makefile['KUBE_NAMESPACE'] = 'default'

        event.makefile.add_target(
            'kube-rollout',
            '\n'.join(
                [
                    '$(KUBECTL) $(KUBECTL_OPTIONS) --namespace=$(KUBE_NAMESPACE) patch {target} -p{patch}'.format(
                        target=target,
                        patch=repr(json.dumps(patch)),
                    ) for target, patch in kube_config.get_targets()
                ]
            ),
            phony=True,
            doc='Rollout docker image onto kubernetes cluster.'
        )

        event.makefile.add_target(
            'kube-rollback',
            '\n'.join(
                ['$(KUBECTL) rollout undo {target}'.format(target=target) for target, patch in kube_config.get_targets()]
            ),
            phony=True,
            doc='Rollbacks last kubernetes patch operation.'
        )
