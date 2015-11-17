#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='cygnet_network_manager',
    version='0.1.0',
    license='Apache License, Version 2.0',
    description='The network interface management tools that run on a docker host machine.',
    long_description='%s\n%s' % (
        read('README.rst'),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))),
    author='Cygnus',
    author_email='sam@cygnus.email',
    url='https://github.com/Cygnus-Inc/cygnet-network-adapter',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: Apache Software License 2.0',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System',
        'Topic :: System :: Clustering',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords=[
        'Docker', 'Networking',
    ],
    # setup_requires=[
    #     'sphinx',
    #     'sphinxcontrib-napoleon',
    # ],
    install_requires=[
        'click',
        'sarge',
        'python-etcd',
        'netifaces',
        'twisted',
        'autobahn',
        'cygnet-common',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
        'documentation': ['sphinx', 'sphinxcontrib-napoleon'],
    },
    entry_points={
        'console_scripts': [
            'cygnet_network_manager = cygnet_network_manager.__main__:main',
        ]
    },
)
