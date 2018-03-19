import itertools
import textwrap
from collections import deque, namedtuple

from medikit.structs import Script
from medikit.utils import get_override_warning_banner

MakefileTarget = namedtuple('MakefileTarget', ['deps', 'rule', 'doc'])


class Makefile(object):
    @property
    def targets(self):
        for key in self._target_order:
            yield key, self._target_values[key]

    @property
    def environ(self):
        return self._env_values

    def __init__(self):
        self._env_order, self._env_values, self._env_assignment_operators = deque(), {}, {}
        self._target_order, self._target_values = deque(), {}
        self.hidden = set()
        self.phony = set()

    def __delitem__(self, key):
        self._env_order.remove(key)
        del self._env_values[key]

    def __getitem__(self, item):
        return self._env_values[item]

    def __setitem__(self, key, value):
        self._env_values[key] = value
        if not key in self._env_order:
            self._env_order.append(key)

    def __iter__(self):
        for key in self._env_order:
            yield key, self._env_values[key]

    def __len__(self):
        return len(self._env_order)

    def __str__(self):
        content = [
            get_override_warning_banner(),
            '',
        ]

        if len(self):
            for k, v in self:
                v = textwrap.dedent(str(v)).strip()
                v = v.replace('\n', ' \\\n' + ' ' * (len(k) + 4))
                content.append('{} {} {}'.format(k, self._env_assignment_operators.get(k, '?='), v))
            content.append('')

        if len(self.phony):
            content.append('.PHONY: ' + ' '.join(sorted(self.phony)))
            content.append('')

        for target, details in self.targets:
            deps, rule, doc = details

            if hasattr(rule, 'render'):
                content += list(rule.render(target, deps, doc))
            else:
                content.append(
                    '{}: {}  {} {}'.format(
                        target, ' '.join(deps), '#' if target in self.hidden else '##',
                        doc.replace('\n', ' ') if doc else ''
                    ).strip()
                )

                script = textwrap.dedent(str(rule)).strip()

                for line in script.split('\n'):
                    content.append('\t' + line)

            content.append('')

        return '\n'.join(content)

    def keys(self):
        return list(self._env_order)

    def add_target(self, target, rule, *, deps=None, phony=False, first=False, doc=None, hidden=False):
        if target in self._target_order:
            raise RuntimeError('Duplicate definition for make target «{}».'.format(target))

        if isinstance(rule, str):
            rule = Script(rule)

        self._target_values[target] = MakefileTarget(
            deps=tuple(deps) if deps else tuple(),
            rule=rule,
            doc=textwrap.dedent(doc or '').strip(),
        )

        self._target_order.appendleft(target) if first else self._target_order.append(target)

        if phony:
            self.phony.add(target)

        if hidden:
            self.hidden.add(target)

    def get_clean_target(self):
        if not self.has_target('clean'):
            self.add_target('clean', CleanScript(), phony=True, doc='''Cleans up the working copy.''')
        return self.get_target('clean')

    def add_install_target(self, extra=None):
        if extra:
            target = 'install-' + extra
            doc = 'Installs the project (with ' + extra + ' dependencies).'
        else:
            target = 'install'
            doc = 'Installs the project.'

        if not self.has_target(target):
            self.add_target(target, InstallScript(), phony=True, doc=doc)

        clean_target = self.get_clean_target()
        marker = '.medikit/' + target
        if not marker in clean_target.remove:
            clean_target.remove.append(marker)
        return self.get_target(target)

    def get_target(self, target):
        return self._target_values[target][1]

    def has_target(self, target):
        return target in self._target_values

    def set_deps(self, target, deps=None):
        self._target_values[target] = (
            deps or list(),
            self._target_values[target][1],
            self._target_values[target][2],
        )

    def set_assignment_operator(self, key, value):
        assert value in ('?=', '=', '+=', ':=', '::=', '!='), 'Invalid operator'
        self._env_assignment_operators[key] = value

    def setleft(self, key, value):
        self._env_values[key] = value
        if key in self._env_order:
            self._env_order.remove(key)
        self._env_order.appendleft(key)

    def updateleft(self, *lst):
        for key, value in reversed(lst):
            self.setleft(key, value)


class InstallScript(Script):
    def __init__(self, script=None):
        super(InstallScript, self).__init__(script)

        self.before_install = []
        self.install = self.script
        self.after_install = []

        self.deps = []

    def __iter__(self):
        yield '@if [ -z "$(QUICK)" ]; then \\'
        for line in map(
            lambda x: '    {} ; \\'.format(x), itertools.chain(self.before_install, self.install, self.after_install)
        ):
            yield line
        yield 'fi'

    def render(self, name, deps, doc):
        tab = '\t'
        yield '{name}: .medikit/{name} {deps}  ## {doc}'.format(name=name, deps=' '.join(deps), doc=doc)
        yield '.medikit/{name}: {deps}'.format(name=name, deps=' '.join(sorted(set(self.deps))))
        yield tab + '$(eval target := $(shell echo $@ | rev | cut -d/ -f1 | rev))'
        yield 'ifeq ($(filter quick,$(MAKECMDGOALS)),quick)'
        yield tab + r'@printf "Skipping \033[36m%s\033[0m because of \033[36mquick\033[0m target.\n" $(target)'
        yield 'else ifneq ($(QUICK),)'
        yield tab + r'@printf "Skipping \033[36m%s\033[0m because \033[36m$$QUICK\033[0m is not empty.\n" $(target)'
        yield 'else'
        yield tab + r'@printf "Applying \033[36m%s\033[0m target...\n" $(target)'
        for line in itertools.chain(self.before_install, self.install, self.after_install):
            yield tab + line
        yield tab + '@mkdir -p .medikit; touch $@'
        yield 'endif'


class CleanScript(Script):
    # We should not clean .medikit subdirectories here, as it will deny releases.
    # TODO: move into python feature
    remove = [
        'build',
        'dist',
        '*.egg-info',
    ]

    def __iter__(self):
        # cleanup build directories
        yield 'rm -rf {}'.format(' '.join(self.remove))
        # cleanup python bytecode -
        yield 'find . -name __pycache__ -type d | xargs rm -rf'
