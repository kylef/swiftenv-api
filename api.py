#!/usr/bin/env python

import os
import glob
import yaml
import flask
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Collection, Link

from versions import Version


app = flask.Flask(__name__)
HAL(app)


def filter_versions():
    """
    Filters versions for the current request.
    """

    snapshots = flask.request.args.get('snapshots', flask.request.args.get('snapshot'))
    platform = flask.request.args.get('platform')

    if snapshots == 'true':
        snapshots = True
    else:
        snapshots = False

    return Version.objects.filter(snapshots=snapshots, platform=platform)


@app.route('/')
def root():
    return Document(links=Collection(
        Link('versions', '/versions'),
    ))


@app.route('/versions/<name>')
def version_detail(name):
    version = Version.objects.get(version=name)
    links = [Link(rel, url) for (rel, url) in version.binaries.items()]
    return Document(data={'version': version.version}, links=Collection(*links))


@app.route('/versions')
def list_text_versions():
    versions = filter_versions().versions

    if 'text/plain' in flask.request.accept_mimetypes.values():
        names = [str(v) for v in versions]
        response = app.make_response('\n'.join(names) + '\n')
        response.headers['Content-Type'] = 'text/plain'
        return response

    def to_embedded(v):
        return Embedded(links=Collection(Link('self', '/versions/{}'.format(v.version))))

    return Document(embedded=dict([(v.version, to_embedded(v)) for v in versions]))


if __name__ == '__main__':
    app.run(debug=True)
