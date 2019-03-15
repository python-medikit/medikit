import logging
import os
import runpy
from collections import OrderedDict
from contextlib import contextmanager

from mondrian import term
from stevedore import ExtensionManager
from whistle import EventDispatcher

import medikit
from medikit.pipeline import Pipeline
from medikit.utils import run_command

logger = logging.getLogger(__name__)


class ConfigurationRegistry:
    def __init__(self, dispatcher: EventDispatcher):
        self._configs = {}
        self._features = {}
        self._pipelines = {}
        self._variables = OrderedDict()

        self.dispatcher = dispatcher
        self.resources = OrderedDict()

        def register_feature(ext):
            self._features[ext.name] = ext.plugin

        def on_load_feature_failure(mgr, entrypoint, err):
            logger.exception("Exception caught while loading {}.".format(entrypoint), err)

        mgr = ExtensionManager(namespace="medikit.feature", on_load_failure_callback=on_load_feature_failure)
        mgr.map(register_feature)

        dispatcher.add_listener(medikit.on_end, self.write_resources)

    def __getitem__(self, item):
        return self._configs[item]

    def __contains__(self, item):
        return item in self._configs

    def set_vars(self, **variables):
        self._variables.update(variables)

    def get_var(self, name, default=None):
        return self._variables.get(name, default)

    @property
    def variables(self):
        return self._variables

    @property
    def package_name(self):
        if "python" in self:
            return self["python"].get("name")
        else:
            name = self.get_var("PACKAGE")
            if not name:
                raise RuntimeError("You must define a package name, using either python.setup() or PACKAGE = ...")
            return name

    def get_name(self):
        return self.package_name

    def get_version_file(self):
        if "python" in self:
            return self["python"].version_file
        elif self.get_var("VERSION_FILE"):
            return self.get_var("VERSION_FILE")
        return "version.txt"

    def get_version(self):
        if "python" in self:
            try:
                return run_command("python setup.py --version")
            except RuntimeError:
                pass  # ignore and fallback to alternative version getters

        version_file = self.get_version_file()
        if os.path.splitext(version_file)[1] == ".py":
            return runpy.run_path(version_file).get("__version__")
        else:
            with open(version_file) as f:
                return f.read().strip()

    def keys(self):
        return self._configs.keys()

    def require(self, *args):
        if len(args) == 1:
            return self._require(args[0])
        elif len(args) > 1:
            return tuple(map(self._require, args))
        raise ValueError("Empty.")

    @contextmanager
    def pipeline(self, name):
        if not name in self._pipelines:
            self._pipelines[name] = Pipeline()
        yield self._pipelines[name]

    @property
    def pipelines(self):
        return self._pipelines

    def _require(self, name):
        if not name in self._features:
            raise ValueError("Unknown feature {!r}.".format(name))

        if name not in self._configs:
            self._configs[name] = self._features[name].Config()

        return self._configs[name]

    def get_resource(self, target):
        if not target in self.resources:
            raise RuntimeError(
                'Resource for "{}" is not defined, you must define it first by providing an implementation.'.format(
                    target
                )
            )
        return self.resources[target]

    def define_resource(self, ResourceType, target, *args, **kwargs):
        if target in self.resources:
            raise RuntimeError(
                'Resource for "{}" is already defined as {!r}, you can only enhance it at this point.'.format(
                    target, self.resources[target]
                )
            )
        self.resources[target] = ResourceType(*args, **kwargs)
        return self.resources[target]

    def write_resources(self, event):
        for target, resource in self.resources.items():
            exists = os.path.exists(target)
            resource.write(event, target)
            self.dispatcher.info(term.bold((term.red if exists else term.green)("W!")), target)
