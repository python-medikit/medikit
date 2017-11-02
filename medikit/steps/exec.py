import json
import os

from git import Repo

from medikit.steps import Step


class Make(Step):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.__args__ = (target, )

    def run(self, meta):
        self.exec('make ' + self.target)
        self.set_complete()


class System(Step):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.__args__ = (cmd, )

    def run(self, meta):
        os.system(self.cmd)
        self.set_complete()


class Commit(Step):
    def __init__(self, message, *, tag=False):
        super().__init__()
        self.message = message
        self.tag = bool(tag)
        self.__args__ = (message, self.tag)

    def run(self, meta):
        branch = self.exec('git rev-parse --abbrev-ref HEAD')
        version = self.exec('python setup.py --version')
        assert version == meta['version']
        os.system('git commit -m ' + json.dumps(self.message.format(**meta)))
        if self.tag:
            os.system('git tag -am {version} {version}'.format(**meta))

        repo = Repo()
        for remote in repo.remotes:
            if str(remote) in ('origin', 'upstream'):
                self.logger.info('git push {} {}...'.format(remote, branch))
                os.system('git push {} {} --tags'.format(remote, branch))

        self.set_complete()
