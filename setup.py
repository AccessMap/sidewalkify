'''`sidewalkify` is a Python library and command line application for drawing
sidewalk lines from street centerline data.

See project information at https://github.com/AccessMap/sidewalkify'''

import re
from setuptools import setup, find_packages

# Get version from package __init__.py
with open('sidewalkify/__init__.py', 'r') as f:
    __version__ = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            f.read(), re.MULTILINE).group(1)
if not __version__:
    raise RuntimeError('Cannot find version information')


doclines = __doc__.split('\n')

config = {
    'name': 'sidewalkify',
    'version': __version__,
    'description': ' '.join(doclines[:2]),
    'long_description': '\n'.join(doclines[2:]),
    'author': '',
    'author_email': '',
    'maintainer': '',
    'maintainer_email': '',
    'url': 'https://github.com/accessmap/sidewalkify',
    'license': 'MIT / Apache 2.0',
    'download_url': 'https://github.com/accessmap/sidewalkify.git',
    'install_requires': ['click',
                         'geopandas',
                         'networkx',
                         'numpy',
                         'Shapely'],
    'packages': find_packages(),
    'include_package_data': True,
    'classifiers': ['Programming Language :: Python',
                    'Programming Language :: Python :: 3.5',
                    'Programming Language :: Python :: 3 :: Only'],
    'zip_safe': False,
    'entry_points': '''
        [console_scripts]
        sidewalkify=sidewalkify.__main__:sidewalkify
    '''
}

setup(test_suite='nose.collector',
      **config)
