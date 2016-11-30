#!/usr/bin/env python

import os
from urllib.parse import urljoin, urlparse
import yaml
import requests
from bs4 import BeautifulSoup


download_url = 'https://swift.org/download/'


def parse_url(url):
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


def save(path, binaries):
    with open(path, 'w') as fp:
        content = yaml.dump({'binaries': binaries}, default_flow_style=False)
        fp.write(content)


def load(path):
    with open(path, 'r') as fp:
        return yaml.load(fp)['binaries']


if __name__ == '__main__':
    request = requests.get(download_url)
    soup = BeautifulSoup(request.text, 'html.parser')
    releases = soup.find_all('a')

    versions = {}

    for a in releases:
        url = urljoin(download_url, a['href'])
        version, platform = parse_url(url)

        if version and platform:
            if version in versions:
                versions[version][platform] = url
            else:
                versions[version] = {platform: url}


    for version in versions:
        path = 'versions/{}.yaml'.format(version)
        binaries = versions[version]

        if os.path.exists(path):
            existing_binaries = load(path)

            if binaries != existing_binaries:
                print('Mismatched Data: {}'.format(version))
        else:
            print('Add {}'.format(version))
            save(path, binaries)

