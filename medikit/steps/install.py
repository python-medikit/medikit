from medikit.steps import Step


def _pip_install(*reqs):
    """Install requirements given a path to requirem."""
    import importlib
    import pip

    pip.main(['install', '--upgrade', *reqs])

    # Some shenanigans to be sure everything is importable after this, especially .egg-link files which
    # are referenced in *.pth files and apparently loaded by site.py at some magic bootstrap moment of the
    # python interpreter.
    pip.utils.pkg_resources = importlib.reload(pip.utils.pkg_resources)
    import site
    importlib.reload(site)


class Install(Step):
    def run(self, meta):
        _pip_install('pip', 'wheel', 'twine')
        self.set_complete()
