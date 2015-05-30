import textwrap

from collections import OrderedDict
from UserDict import UserDict

from edgy.event import Event
from edgy.project.file import File

from . import Feature

class Makefile(UserDict):
    def __init__(self):
        UserDict.__init__(self)
        self.targets = OrderedDict()
        self.phony = set()

    def add_target(self, target, rule, deps=None, phony=False):
        self.targets[target] = (
            deps or list(),
            textwrap.dedent(rule).strip(),
        )
        if phony:
            self.phony.add(target)

    def __str__(self):
        content = []

        if len(self):
            for k, v in self.items():
                content.append('{} ?= {}'.format(k, v))
            content.append('')

        if len(self.phony):
            content.append('.PHONY: '+' '.join(self.phony))
            content.append('')

        for target, details in self.targets.items():
            deps, rule = details
            content.append('{}: {}'.format(target, ' '.join(deps)).strip())
            for line in rule.split('\n'):
                content.append('	'+line)
            content.append('')

        return '\n'.join(content)

class MakefileEvent(Event):
    def __init__(self, makefile):
        self.makefile = makefile
        super(MakefileEvent, self).__init__()

class MakeFeature(Feature):
    def configure(self):
        self.makefile = Makefile()
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start)

    def on_start(self, event):
        for k in sorted(event.variables):
            self.makefile[k.upper()] = event.variables[k]

        self.makefile['PYTHON'] = '$(VIRTUALENV_PATH)/bin/python'
        self.makefile['PYTHON_PIP'] = '$(VIRTUALENV_PATH)/bin/pip --cache-dir=$(PIPCACHE_PATH)'

        self.makefile.add_target('install', '''
            $(PYTHON_PIP) wheel -w $(WHEELHOUSE_PATH) -f $(WHEELHOUSE_PATH) -r requirements.txt
            $(PYTHON_PIP) install -f $(WHEELHOUSE_PATH) -U -r requirements.txt
        ''', deps=('$(VIRTUALENV_PATH)', ), phony=True)

        self.makefile.add_target('$(VIRTUALENV_PATH)', '''
            virtualenv $(VIRTUALENV_PATH)
            $(PYTHON_PIP) install -U pip\>=7.0,\<8.0 wheel\>=0.24,\<1.0
        ''')

        self.dispatcher.dispatch(__name__+'.on_generate', MakefileEvent(self.makefile))

        self.render_file_inline('Makefile', unicode(self.makefile), override=True)

__feature__ = MakeFeature
