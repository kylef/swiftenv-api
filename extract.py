#!/usr/bin/env python

import os
from urllib.parse import urljoin, urlparse
import yaml
import requests
from bs4 import BeautifulSoup


if __name__ == '__main__':
    download_url = 'https://swift.org/download/'
    request = requests.get(download_url)
    soup = BeautifulSoup(request.text, 'html.parser')
    releases = soup.find_all('span', class_='release')

    versions = {}

    for release in releases:
        url = urljoin(download_url, release.a['href'])
        if url.endswith('.tar.gz') or url.endswith('.pkg'):
            parse = urlparse(url)
            name = parse.path.split('/')[-1]
            (software, rest) = name.split('-', 1)
            assert(software == 'swift')

            rest = rest.replace('.tar.gz', '').replace('.pkg', '')
            (rest, platform) = rest.rsplit('-', 1)
            version = rest.replace('-RELEASE', '')

            if version in versions:
                versions[version][platform] = url
            else:
                versions[version] = {platform: url}


    for version in versions:
        path = 'versions/{}.yaml'.format(version)

        if not os.path.exists(path):
            with open(path, 'w') as fp:
                content = yaml.dump({'binaries': versions[version]}, default_flow_style=False)
                fp.write(content)


