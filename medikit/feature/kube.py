"""
Setup make targets to rollout and rollback this project as a deployment onto a Kubernetes cluster.

"""
import json

from medikit.events import subscribe
from medikit.feature import Feature
from medikit.feature.make import which


class KubeConfig(Feature.Config):
    def __init__(self):
        self._targets = dict()
        self._targets_patches = dict()
        self._use_helm = False

    def add_target(self, name, variant=None, *, patch, patch_path=""):
        if not variant in self._targets:
            self._targets[variant] = list()
            self._targets_patches[variant] = dict()

        if name in self._targets[variant]:
            raise ValueError("Kubernetes target {} already defined.".format(name))

        self._targets[variant].append(name)
        self._targets_patches[variant][name] = patch_path, patch

    def get_variants(self):
        return list(self._targets.keys())

    def get_targets(self, variant=None):
        for target in self._targets[variant]:
            yield target, self._targets_patches[variant][target]

    @property
    def use_helm(self):
        return self._use_helm

    def enable_helm(self):
        self._use_helm = True
        return self

    def disable_helm(self):
        self._use_helm = False
        return self


class KubeFeature(Feature):
    Config = KubeConfig

    requires = {"docker"}

    @subscribe("medikit.feature.make.on_generate", priority=-1)
    def on_make_generate(self, event):
        kube_config = event.config["kube"]

        event.makefile["KUBECTL"] = which("kubectl")
        event.makefile["KUBECTL_OPTIONS"] = ""
        event.makefile["KUBECONFIG"] = ""
        event.makefile["KUBE_NAMESPACE"] = "default"

        if kube_config.use_helm:
            event.makefile["HELM"] = which("helm")
            event.makefile["HELM_RELEASE"] = event.config.get_name()

        for variant in kube_config.get_variants():
            targets = list(kube_config.get_targets(variant=variant))
            if len(targets):
                rollout_target = "-".join(filter(None, ("kube-rollout", variant)))
                rollback_target = "-".join(filter(None, ("kube-rollback", variant)))

                rollout_commands, rollback_commands = [], []
                for target, (patch_path, patch) in targets:
                    while patch_path:
                        try:
                            patch_path, _bit = patch_path.rsplit(".", 1)
                        except ValueError:
                            patch_path, _bit = None, patch_path
                        patch = {_bit: patch}

                    rollout_commands.append(
                        "$(KUBECTL) $(KUBECTL_OPTIONS) --namespace=$(KUBE_NAMESPACE) patch {target} -p{patch}".format(
                            target=target, patch=repr(json.dumps(patch))
                        )
                    )

                    rollback_commands.append("$(KUBECTL) rollout undo {target}".format(target=target))

                event.makefile.add_target(
                    rollout_target,
                    "\n".join(rollout_commands),
                    phony=True,
                    doc="Rollout docker image onto kubernetes cluster.",
                )

                event.makefile.add_target(
                    rollback_target,
                    "\n".join(rollback_commands),
                    phony=True,
                    doc="Rollbacks last kubernetes patch operation.",
                )
