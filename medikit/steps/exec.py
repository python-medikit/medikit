import json
import multiprocessing
import os
from queue import Empty

from git import Repo
from mondrian import term

from medikit.steps import Step
from medikit.steps.utils.process import Process


class System(Step):
    def __init__(self, cmd, *, interractive=False):
        super().__init__()
        self.cmd = cmd
        self.interractive = interractive
        self.__args__ = (
            cmd,
            interractive,
        )

    def run(self, meta):
        if self.interractive:
            os.system(self.cmd)
        else:
            child = Process(self.cmd)
            events = multiprocessing.Queue()
            parent = multiprocessing.Process(name='task', target=child.run, args=(events, True))
            parent.start()
            exit = False
            returncode = None
            while not exit:
                try:
                    msg = events.get(timeout=0.1)
                except Empty:
                    if exit:
                        break
                else:
                    if msg.type == 'line':
                        print(term.lightblack('\u2502'), msg.data.decode('utf-8'), end='')
                    elif msg.type == 'start':
                        print('$ ' + term.lightwhite(self.cmd) + term.black('  # pid=%s' % msg.data['pid']))
                    elif msg.type == 'stop':
                        returncode = msg.data['returncode']
                        if returncode:
                            print(term.lightblack('\u2514' + term.red(' failed (rc={}). '.format(returncode))))
                        else:
                            print(term.lightblack('\u2514' + term.green(' success. ')))
                        exit = True
            if returncode:
                raise RuntimeError(
                    '"{command}" exited with status {returncode}.'.format(command=self.cmd, returncode=returncode)
                )
        self.set_complete()


class Make(System):
    def __init__(self, target):
        super().__init__('make ' + target)
        self.__args__ = (target, )


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
