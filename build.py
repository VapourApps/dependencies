#!/usr/bin/env python
import zipfile
import os
import multiprocessing
import urllib2
import StringIO
import datetime
import hashlib
import argparse
import subprocess

VERSIONS = (
    ('terraform', '0.9.11'),
    ('consul', '0.8.5')
)
PLATFORMS = ('linux_amd64', 'windows_amd64')
URL_PATTERN = 'https://releases.hashicorp.com/{tool}/{ver}/{tool}_{ver}_{platform}.zip'

def download_zip(data):
    r = urllib2.urlopen(data['link'])
    print('Downloading {link}...'.format(link=data['link']))
    bin = r.read()
    file = StringIO.StringIO(bin)
    filename = data['tool']
    if 'windows' in data['platform']: filename+= '.exe'

    with zipfile.ZipFile(file) as zip_f:
        return zip_f.open(filename).read()

def write_readme(result):
    TEMPLATE = '''# Binary dependencies
This project builds zip files with executable dependencies for the master's runtime, \
and then uploads them to PyPi.

## Update or add dependencies
Edit the `build.py` with the wanted dependencies:
```python
VERSIONS = (
    ('terraform', '0.9.11'),
    ('consul', '0.8.5')
)
```
Run `./build.py`, which will download and prepare the files. (this may take ~2
mins). Then, run `python setup.py vapour_linux_amd64:0.1 sdist upload` (or any
other `vapour_<platform>:<version>` combination) and login with the proper PyPi
credentials.


## Currently shipping
Built on: {time}

| Name | Version | SHA256 |
| ---  | ------- | -----  |
{table}
'''
    t = str(datetime.datetime.now())
    table = ''
    for d, bin in result:
        digest = hashlib.sha256(bin).hexdigest()
        name = '**{tool}** ({platform})'.format(tool=d['tool'], platform=d['platform'])
        version = d['version']
        table += '| {name} | {version} | {digest} |\n'.format(
            name=name,
            version=version,
            digest=digest
        )
    with open('README.md', 'w') as myf:
        myf.write(TEMPLATE.format(time=t, table=table))

def pypi_upload(ppath, pypi_version):
    TEMPLATE = '''from setuptools import setup
setup(
    name='{name}',
    packages=['{name}'],
    package_data={{'{name}': ['*.zip']}},
    version='{ver}',
    description='This package contains binary executable dependencies for the master.',
    author='VapourApps',
    author_email='vapour@vapour.com'
)'''
    with open('setup.py', 'w') as setupf:
        setup_content = TEMPLATE.format(
            name=ppath,
            ver=pypi_version
        )
        setupf.write(setup_content)
    subprocess.check_output(['python', 'setup.py', 'sdist', 'upload'])
def main(pypi_version):
    p = multiprocessing.Pool(4)
    data = []
    for tool, version in VERSIONS:
        for platform in PLATFORMS:
            link = URL_PATTERN.format(tool=tool, ver=version, platform=platform)
            data.append({
                'link': link,
                'tool': tool,
                'version': version,
                'platform': platform
            })
    result = p.map(download_zip, data)
    result = zip(data, result)
    print('Creating README.md...')
    write_readme(result)
    platform_results = {}
    for d, bin_data in result:
        platform_result = platform_results.get(d['platform'], None)
        if platform_result is None:
            platform_results[d['platform']] = []
            platform_result = platform_results[d['platform']]
        platform_result.append((d, bin_data))

    for platform, d_and_bins in platform_results.items():
        ppath = 'vapour_' + platform
        if not os.path.exists(ppath):
            os.makedirs(ppath)
        with open(os.path.join(ppath, '__init__.py'), 'w'):
            pass
        zip_path = '{ppath}/bindeps.zip'.format(ppath=ppath)
        print('Writing {}...'.format(zip_path))
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as myzip:
            for d, bin in d_and_bins:
                name = d['tool']
                if 'windows' in d['platform']: name+= '.exe'
                if 'linux' in d['platform']: name+= '.bin'
                myzip.writestr(name, bin)
        print('Uploading {} to PyPi...'.format(zip_path))
        pypi_upload(ppath, pypi_version)
    print('Done.')
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    args = parser.parse_args()
    main(args.version)
