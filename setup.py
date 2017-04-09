'''data_manager for AccessMap: fetch, clean, and stage pedestrian geodata'''

import re
from setuptools import setup, find_packages

# Get version from package __init__.py
with open('data_manager/__init__.py', 'r') as f:
    __version__ = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            f.read(), re.MULTILINE).group(1)
if not __version__:
    raise RuntimeError('Cannot find version information')


doclines = __doc__.split('\n')

config = {
    'name': 'data_manager',
    'version': __version__,
    'description': doclines[0],
    'long_description': '\n'.join(doclines[2:]),
    'author': '',
    'author_email': '',
    'maintainer': '',
    'maintainer_email': '',
    'url': 'https://github.com/accessmap/accessmap-database-bootup',
    'license': 'BSD',
    'download_url': 'https://github.com/accessmap/accessmap-database-bootup.git',
    'install_requires': ['click',
                         'geopandas',
                         'numpy',
                         'requests',
                         'rtree',
                         'Shapely'],
    'packages': find_packages(),
    'include_package_data': True,
    'classifiers': ['Programming Language :: Python',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 2 :: Only'],
    'zip_safe': False,
    'entry_points': '''
        [console_scripts]
        data_manager=data_manager.__main__:cli
    '''
}

setup(test_suite='nose.collector',
      **config)
