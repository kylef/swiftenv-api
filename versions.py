import os
import glob
from pathlib import Path

import flask
import yaml


class VersionManager(object):
    def __init__(self, versions=None):
        self._versions = versions

    @property
    def versions(self):
        if not self._versions:
            version_paths = Path('versions').glob('**/*.yaml')
            version_files = map(str, version_paths)
            versions = map(Version.fromfile, version_files)
            versions = sorted(versions, key=lambda v: v.version)
            self._versions = list(versions)
        return self._versions

    def all(self):
        return self

    def filter(self, version=None, snapshots=None, platform=None):
        versions = self.versions

        if version:
            versions = [v for v in versions if v.version == version]

        if snapshots is True:
            versions = [v for v in versions if v.is_snapshot]

        if snapshots is False:
            versions = [v for v in versions if not v.is_snapshot]

        if platform:
            versions = [v for v in versions if v.supports_platform(platform)]

        return VersionManager(versions)

    def get(self, **kwargs):
        if kwargs:
            versions = self.filter(**kwargs)
            return versions.get()

        if len(self.versions) == 1:
            return self.versions[0]

        raise flask.abort(404)


class Version(object):
    objects = VersionManager()

    @classmethod
    def fromfile(cls, path):
        version = os.path.splitext(os.path.basename(path))[0]

        with open(path) as fp:
            content = yaml.load(fp.read())
            binaries = content['binaries']

        if 'version' in content:
            version = content['version']

        return cls(version, binaries)

    def __init__(self, version, binaries):
        self.version = version
        self.binaries = binaries

    def __str__(self):
        return self.version

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.version == other.version and self.binaries == other.binaries

        return False

    @property
    def is_snapshot(self):
        return 'SNAPSHOT' in self.version

    def supports_platform(self, platform):
        """
        Returns if the version has a binary release for the given platform.
        """
        return platform in self.binaries

    @property
    def path(self):
        if self.version.startswith('DEVELOPMENT-SNAPSHOT-'):
            version = self.version[len('DEVELOPMENT-SNAPSHOT-'):]
            (year, month, rest) = version.split('-', 2)
            return os.path.join('versions', 'DEVELOPMENT-SNAPSHOT', year, month, '{}.yaml'.format(rest))

        if '-' in self.version:
            version, rest = self.version.split('-', 1)
        else:
            version = self.version
            rest = None

        major = version.split('.', 1)[0]

        if rest:
            if rest.startswith('DEVELOPMENT-SNAPSHOT-'):
                rest = rest[len('DEVELOPMENT-SNAPSHOT-'):]
                return os.path.join('versions', major, '{}-DEVELOPMENT-SNAPSHOT'.format(version), '{}.yaml'.format(rest))

        return os.path.join('versions', major, '{}.yaml'.format(self.version))

    def save(self):
        path = Path(os.path.split(self.path)[0])
        path.mkdir(parents=True, exist_ok=True)

        with open(self.path, 'w') as fp:
            yaml.dump({'version': self.version, 'binaries': self.binaries}, fp, default_flow_style=False)
