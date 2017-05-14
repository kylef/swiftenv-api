#!/usr/bin/env python

import sys
import os
import subprocess
from urllib.parse import urljoin, urlparse
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


def save_version(version, commit=False):
    if os.path.exists(version.path):
        existing_version = Version.fromfile(version.path)

        if version != existing_version:
            print('Mismatched Data: {}'.format(version))
    else:
        print('Add {}'.format(version))
        version.save()

        if commit:
            subprocess.check_call(['git', 'add', version.path])
            subprocess.check_call(['git', 'commit', '-m', 'chore: Add {}'.format(version.version)])

        return True

    return False


def save_versions(versions, commit=False):
    updated = False

    for version in versions:
        if save_version(version, commit=commit):
            updated = True

    return updated


if __name__ == '__main__':
    if '--help' in sys.argv:
        print('Usage: {} [--commit] [--push] [--help]'.format(sys.argv[0]))
        print('\nOptions:')
        print('    --commit - Create commits for each version change')
        print('    --push - Push master to origin after extracting versions (Implies --commit)')
        exit(0)

    push = '--push' in sys.argv
    commit = push or '--commit' in sys.argv

    saved = save_versions(determine_versions(), commit=commit)

    if saved and push:
        subprocess.check_call(['git', 'push', 'origin', 'master'])
