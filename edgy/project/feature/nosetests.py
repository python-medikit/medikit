from . import Feature


class NosetestsFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.feature.make.on_generate', self.on_make_generate)
        self.dispatcher.add_listener('edgy.project.feature.python.on_generate', self.on_python_generate)

    def on_make_generate(self, event):
        makefile = event.makefile
        makefile.add_target('test', '''
            nosetests -q --with-doctest --with-coverage --cover-package=edgy.project
        ''', deps=('install', ), phony=True)

    def on_python_generate(self, event):
        event.files['requirements'] = '\n'.join((event.files['requirements'], 'nose >=1.3,<1.4', 'coverage >=3.7,<3.8' ))


__feature__ = NosetestsFeature
