#!/usr/bin/env python

import os
from urllib.parse import urljoin, urlparse
import yaml
import requests
from bs4 import BeautifulSoup

from versions import Version


download_url = 'https://swift.org/download/'


def parse_url(url):
    """
    Parse a URL into a version and platform tuple.

    >>> parse_url('https://swift.org/builds/swift-3.0.1-release/ubuntu1604/swift-3.0.1-RELEASE/swift-3.0.1-RELEASE-ubuntu16.04.tar.gz')
    ('3.0.1', 'ubuntu16.04')
    """

    if url.endswith('.tar.gz') or url.endswith('.pkg'):
        parse = urlparse(url)
        name = parse.path.split('/')[-1]
        (software, rest) = name.split('-', 1)
        assert(software == 'swift')

        rest = rest.replace('.tar.gz', '').replace('.pkg', '')
        (rest, platform) = rest.rsplit('-', 1)
        version = rest.replace('-RELEASE', '').replace('-osx', '')

        if platform == 'symbols':
            # macOS Debugging Symbol link
            return (None, None)

        return (version, platform)

    return (None, None)


def determine_versions():
    """
    Scrape the Swift website to find all available versions.

    >>> determine_versions()
    [Version(3.0.1), Version(3.0), ...]
    """

    request = requests.get(download_url)
    soup = BeautifulSoup(request.text, 'html.parser')
    releases = soup.find_all('a')

    versions = {}

    for a in releases:
        url = urljoin(download_url, a['href'])
        version, platform = parse_url(url)

        if version and platform:
            if version in versions:
                versions[version].binaries[platform] = url
            else:
                versions[version] = Version(version, {platform: url})

    return [version for (name, version) in versions.items()]


def save_versions(versions):
    for version in versions:
        path = 'versions/{}.yaml'.format(version.version)

        if os.path.exists(path):
            existing_version = Version.fromfile(path)

            if version != existing_version:
                print('Mismatched Data: {}'.format(version))
        else:
            print('Add {}'.format(version))
            version.save()


if __name__ == '__main__':
    save_versions(determine_versions())
