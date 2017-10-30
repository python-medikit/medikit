import os
import runpy

from git import Repo
from semantic_version import Version

from git_semver import get_current_version
from medikit.steps import Step


class PythonVersion(Version):
    def __str__(self):
        version = '%d' % self.major
        if self.minor is not None:
            version = '%s.%d' % (version, self.minor)
        if self.patch is not None:
            version = '%s.%d' % (version, self.patch)

        if self.prerelease or (self.partial and self.prerelease == () and self.build is None):
            version = '%s%s' % (version, '.'.join(self.prerelease))
        if self.build or (self.partial and self.build == ()):
            version = '%s+%s' % (version, '.'.join(self.build))
        return version


class BumpVersion(Step):
    def run(self, meta):
        '''
        git add $VERSION_FILE
        '''
        name = self.exec('python setup.py --name')
        version_file = os.path.join(name.replace('.', '/'), '_version.py')

        if not os.path.exists(version_file):
            raise FileNotFoundError('Cannot find version file for {} (searched in {!r}).'.format(name, version_file))

        repo = Repo()
        for remote in repo.remotes:
            self.logger.info('git fetch {}...'.format(remote))
            remote.fetch(tags=True)

        git_version = get_current_version(repo, Version=PythonVersion)
        if git_version:
            git_version.partial = False
        current_version = PythonVersion.coerce(runpy.run_path(version_file).get('__version__'), partial=True)
        current_version.partial = False

        next_version = None
        while not next_version:
            try:
                print('Current version:', current_version, 'Git version:', git_version)
                next_version = input('Next version? ')
                # todo next patch, etc.
                next_version = PythonVersion.coerce(next_version, partial=True)
                next_version.partial = False
            except ValueError as exc:
                self.logger.error(exc)
                next_version = None

        with open(version_file, 'w+') as f:
            f.write("__version__ = '{}'\n".format(str(next_version)))

        self.exec('git add {}'.format(version_file))

        meta['version'] = str(next_version)

        self.set_complete()
