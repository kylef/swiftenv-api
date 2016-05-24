#!/usr/bin/env python

import os
import glob
import yaml
import flask


class Version(object):
    @classmethod
    def versions(cls):
        version_files = glob.glob('versions/*.yaml')
        return list(map(Version.fromfile, version_files))

    @classmethod
    def fromfile(cls, path):
        version = os.path.splitext(os.path.basename(path))[0]

        with open(path) as fp:
            content = yaml.load(fp.read())
            binaries = content['binaries']

        return cls(version, binaries)

    def __init__(self, version, binaries):
        self.version = version
        self.binaries = binaries

    def __str__(self):
        return self.version

    @property
    def is_snapshot(self):
        return 'SNAPSHOT' in self.version

    def supports_platform(self, platform):
        """
        Returns if the version has a binary release for the given platform.
        """
        return platform in self.binaries


VERSIONS = Version.versions()
app = flask.Flask(__name__)


@app.route('/versions')
def list_versions():
    versions = VERSIONS

    snapshots = flask.request.args.get('snapshot')
    if snapshots == 'true':
        versions = [v for v in versions if v.is_snapshot]
    elif snapshots == 'false':
        versions = [v for v in versions if not v.is_snapshot]

    platform = flask.request.args.get('platform')
    if platform:
        versions = [v for v in versions if v.supports_platform(platform)]

    names = sorted([version.version for version in versions])
    response = app.make_response('\n'.join(names) + '\n')
    response.headers['Content-Type'] = 'text/plain'
    return response


if __name__ == '__main__':
    app.run(debug=True)
