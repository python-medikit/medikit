"""
GNU Make support.

"""

import medikit
from medikit.events import subscribe
from medikit.feature import Feature, HIGH_PRIORITY
from medikit.feature.make.config import MakeConfig
from medikit.feature.make.events import MakefileEvent
from medikit.feature.make.resources import MakefileTarget, Makefile, InstallScript, CleanScript
from medikit.feature.make.utils import which
from medikit.structs import Script

__all__ = [
    'CleanScript',
    'InstallScript',
    'MakeConfig',
    'MakeFeature',
    'Makefile',
    'MakefileEvent',
    'MakefileTarget',
    'which',
]


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

        self.makefile.add_install_target()

        for extra in event.config['make'].extras:
            self.makefile.add_install_target(extra)

        self.makefile.add_target('quick', Script('@printf ""'), phony=True, hidden=True)

        self.dispatcher.dispatch(
            MakeConfig.on_generate, MakefileEvent(event.config.package_name, self.makefile, event.config)
        )

        if event.config['make'].include_medikit_targets:
            self.add_medikit_targets(event.config['make'])

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

        # Actual rendering of the Makefile
        self.render_file_inline('Makefile', self.makefile.__str__(), override=True)

    def add_medikit_targets(self, config):
        if not 'PYTHON' in self.makefile:
            self.makefile['PYTHON'] = which('python')
        self.makefile['MEDIKIT'] = '$(PYTHON) -m medikit'
        self.makefile['MEDIKIT_UPDATE_OPTIONS'] = ''
        self.makefile['MEDIKIT_VERSION'] = medikit.__version__

        source = [
            'import medikit, sys',
            'from packaging.version import Version',
            'sys.exit(0 if Version(medikit.__version__) >= Version("$(MEDIKIT_VERSION)") else 1)',
        ]

        self.makefile.add_target(
            'medikit',
            '@$(PYTHON) -c {!r} || $(PYTHON) -m pip install -U "medikit>=$(MEDIKIT_VERSION)"'.format('; '.join(source)),
            phony=True,
            hidden=True,
            doc='Checks installed medikit version and updates it if it is outdated.'
        )

        self.makefile.add_target(
            'update',
            '$(MEDIKIT) update $(MEDIKIT_UPDATE_OPTIONS)',
            deps=('medikit', ),
            phony=True,
            doc='''Update project artifacts using medikit.'''
        )

        # TODO this should adapt to langauges included, and be removed if no language
        # For example, requirements*.txt are specific to python, using classic setuptools.
        self.makefile.add_target(
            'update-requirements',
            'MEDIKIT_UPDATE_OPTIONS="--override-requirements" $(MAKE) update',
            phony=True,
            doc='''Update project artifacts using medikit, including requirements files.'''
        )
