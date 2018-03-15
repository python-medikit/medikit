"""
GNU Make support.

"""

import itertools
import textwrap
from collections import deque

from whistle import Event

from medikit.events import subscribe
from medikit.feature import Feature, HIGH_PRIORITY
from medikit.structs import Script
from medikit.utils import get_override_warning_banner


def which(cmd):
    return '$(shell which {cmd} || echo {cmd})'.format(cmd=cmd)

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
            content.append(
                '{}: {}  ## {}'.format(target, ' '.join(deps),
                                       doc.replace('\n', ' ') if doc else '').strip()
            )

            script = textwrap.dedent(str(rule)).strip()

            for line in script.split('\n'):
                content.append('\t' + line)

            content.append('')

        return '\n'.join(content)

    def add_target(self, target, rule, deps=None, phony=False, first=False, doc=None):
        if target in self._target_order:
            raise RuntimeError('Duplicate definition for make target «{}».'.format(target))

        if isinstance(rule, str):
            rule = Script(rule)

        self._target_values[target] = (
            deps or list(),
            rule,
            textwrap.dedent(doc or '').strip(),
        )
        self._target_order.appendleft(target) if first else self._target_order.append(target)

        if phony:
            self.phony.add(target)

    def get_target(self, target):
        return self._target_values[target][1]

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
        if not key in self._env_order:
            self._env_order.appendleft(key)

    def updateleft(self, *lst):
        for key, value in reversed(lst):
            self.setleft(key, value)


class MakefileEvent(Event):
    def __init__(self, package_name, makefile, config):
        self.package_name = package_name
        self.makefile = makefile
        self.config = config
        super(MakefileEvent, self).__init__()


class InstallScript(Script):
    def __init__(self, script=None):
        super(InstallScript, self).__init__(script)

        self.before_install = []
        self.install = self.script
        self.after_install = []

    def __iter__(self):
        yield 'if [ -z "$(QUICK)" ]; then \\'
        for line in map(
                lambda x: '    {} ; \\'.format(x),
                itertools.chain(self.before_install, self.install, self.after_install)
        ):
            yield line
        yield 'fi'


class CleanScript(Script):
    remove = [
        'build',
        'dist',
        '*.egg-info',
    ]

    def __iter__(self):
        yield 'rm -rf {}'.format(' '.join(self.remove))


class MakeConfig(Feature.Config):
    __usage__ = """
    
    Currently, **this feature is required for medikit to work**.
    
    Makefile generation and management is quite central to medikit, and it's one of the strongest opinionated choices
    made by the tool.
    
    .. note:: `Makefile` will be overriden on each `medikit update` run! See below how to customize it.
    
    Everything out of the project's world is managed by a single, central Makefile, that contains all the external
    entrypoints to your package.
    
    By default, it only contains the following targets (a.k.a "tasks"):
    
    * install
    * install-dev
    * update
    * update-requirements
    
    This is highly extendable, and about all other features will add their own targets using listeners to the
    :obj:`MakeConfig.on_generate` event.
    
    Default targets
    ---------------
    
    Install
    .......
    
    The `make install` command will try its best to install your package in your current system environment. For python
    projects, it work with the system python, but you're highly encouraged to use a virtual environment (using
    :mod:`virtualenv` or :mod:`venv` module).
    
    .. code-block:: shel-session
    
        $ make install
        
    Install Dev
    ...........
    
    The `make install-dev` command works like `make install`, but adds the `dev` extra.
    
    The `dev` extra is a convention medikit takes to group all dependencies that are only required to actual hack on
    your project, and that won't be necessary in production / runtime environments.
    
    For python projects, it maps to an "extra", as defined by setuptools. For Node.js projects, it will use the
    "devDependencies".
    
    .. code-block:: shell-session
    
        $ make install-dev
        
    Update
    ......
    
    This is a shortcut to `medikit update`, with a preliminary dependency check on `medikit`.
    
    As you may have noticed, `medikit` is never added as a dependency to your project, so this task will ensure it's
    installed before running.
    
    .. code-block:: shell-session
    
        $ make update
        
    Update Requirements
    ...................
    
    The `make update-requirements` command works like `make update`, but forces the regeneration of `requirements*.txt`
    files.
    
    For security reasons, `medikit` never updates your requirements if they are already frozen in requirements files
    (you would not want a requirement to increment version without notice).
    
    This task is here so you can explicitely update your requirements frozen versions, according to the constraints
    you defined in the `Projectfile`.
    
    .. code-block:: shell-session
    
        $ make update-requirements
        
    Customize your Makefile
    -----------------------
    
    To customize the generated `Makefile`, you can use the same event mechanism that is used by `medikit` features,
    directly from within your `Projectfile`.
    
    Add a target
    ............
    
    .. code-block:: python
    
        from medikit import listen
        
        @listen(make.on_generate)
        def on_make_generate(event):
            event.makefile.add_target('foo', '''
                    echo "Foo!"
                ''', deps=('install', ), phony=True, doc='So foo...'
            )
            
        This is pretty self-explanatory, but let's detail:
        
        * "foo" is the target name (you'll be able to run `make foo`)
        * This target will run `echo "Foo!"`
        * It depends on the `install` target, that needs to be satisfied (install being "phony", it will be run
          every time).
        * This task is "phony", meaning that there will be no `foo` file or directory generated as the output, and thus
          that `make` should consider it's never outdated.
        * If you create non phony targets, they must result in a matching file or directory created.
        * Read more about GNU Make: https://www.gnu.org/software/make/
    
    Change the dependencies of an existing target
    .............................................
    
    .. code-block:: python
    
        from medikit import listen
        
        @listen(make.on_generate)
        def on_make_generate(event):
            event.makefile.set_seps('foo', ('install-dev', ))

    Add (or override) a variable
    ............................
    
    .. code-block:: python
    
        from medikit import listen
        
        @listen(make.on_generate)
        def on_make_generate(event):
            event.makefile['FOO'] = 'Bar'
            
    The user can override `Makefile` variables using your system environment:
    
    .. code-block:: shell-session
    
        $ FOO=loremipsum make foo
        
    To avoid this default behaviour (which is more than ok most of the time), you can change the assignment operator
    used in the makefile.
        
    .. code-block:: python
    
        from medikit import listen
        
        @listen(make.on_generate)
        def on_make_generate(event):
            event.makefile.set_assignment_operator('FOO', ':=')
            
    This is an advanced feature you'll probably never need. You can `read the make variables reference
    <https://www.gnu.org/software/make/manual/html_node/Using-Variables.html#Using-Variables>`_.
    
    """

    on_generate = __name__ + '.on_generate'
    """Happens during the makefile generation."""

    def __init__(self):
        self.include_medikit_targets = True

    def disable_medikit_targets(self):
        self.include_medikit_targets = False


class MakeFeature(Feature):
    Config = MakeConfig

    def configure(self):
        self.makefile = Makefile()

    @subscribe('medikit.on_start', priority=HIGH_PRIORITY)
    def on_start(self, event):
        """
        :param ProjectEvent event:
        """
        for k in event.variables:
            self.makefile[k.upper()] = event.variables[k]

        self.makefile.updateleft((
            'QUICK',
            '',
        ), )

        self.makefile.add_target(
            'install', InstallScript(), phony=True, doc='''Installs the local project dependencies.'''
        )
        self.makefile.add_target(
            'install-dev',
            InstallScript(),
            phony=True,
            doc='''Installs the local project dependencies, including development-only libraries.'''
        )
        self.makefile.add_target('clean', CleanScript(), phony=True, doc='''Cleans up the local mess.''')

        if event.config['make'].include_medikit_targets:
            self.makefile.add_target(
                'update',
                '''
                python -c 'import medikit; print(medikit.__version__)' || pip install medikit;
                $(PYTHON) -m medikit update
            ''',
                phony=True,
                doc='''Update project artifacts using medikit, after installing it eventually.'''
            )

            self.makefile.add_target(
                'update-requirements',
                '''
                rm -rf requirements*.txt
                $(MAKE) update
            ''',
                phony=True,
                doc=
                '''Remove requirements files and update project artifacts using medikit, after installing it eventually.'''
            )

        self.dispatcher.dispatch(
            MakeConfig.on_generate, MakefileEvent(event.config['python'].get('name'), self.makefile, event.config)
        )
        # Recipe courtesy of https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
        self.makefile.add_target(
            'help',
            r"""
            @echo "Available commands:"
            @echo
            @grep -E '^[a-zA-Z_-]+:.*?##[\s]?.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"}; {printf "    make \033[36m%-30s\033[0m %s\n", $$1, $$2}'
            @echo
            """,
            phony=True,
            doc='Shows available commands.'
        )
        self.render_file_inline('Makefile', self.makefile.__str__(), override=True)


__feature__ = MakeFeature
