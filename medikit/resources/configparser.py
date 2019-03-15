import configparser
import os


class AbstractResource:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def _set_values(c, values):
    for k, v in values.items():
        if not k in c:
            c[k] = {}
        for kk, vv in v.items():
            c[k][kk] = vv


class ConfigParserResource(AbstractResource):
    def __init__(self):
        self.initial_values = []
        self.managed_values = []

    def set_initial_values(self, values):
        self.initial_values.append(values)

    def set_managed_values(self, values):
        self.managed_values.append(values)

    def write(self, event, target):
        config = configparser.ConfigParser()
        exists = os.path.exists(target)
        if exists:
            config.read(target)
        else:
            # only apply to new files
            for initial_value in self.initial_values:
                _set_values(config, initial_value)

        for managed_value in self.managed_values:
            _set_values(config, managed_value)

        with open(target, "w+") as f:
            config.write(f)
