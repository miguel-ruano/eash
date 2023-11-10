#!/usr/bin/env python

import codecs
import os.path

from setuptools import setup

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")
        
def get_subfolders_as_modules(directory):
    directory = os.path.join(os.getcwd(),directory)
    dirs = [x[0] for x in os.walk(directory)]
    dirs = list(
        map(
            lambda d : d[1:len(d)],
            map(lambda d : d.replace(os.getcwd(), '').replace('/', '.').replace('\\','.'), dirs)
        )
    )
    return dirs

setup(
    name='eash-cli',
    version=get_version('cli/_version.py'),
    description='Eash Command line interface',
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    author='Jose Miguel Ruano',
    author_email='miguel199308@gmail.com',
    url='https://miguelruano.dev',
    install_requires=open("requirements.txt", "r").readlines(),
    packages=[
        'cli',
        'cli.core',
        'cli.utils',
        'cli.modules',
        *get_subfolders_as_modules('cli/assets')
    ],
    package_data={'': ['*.anbr','*.yml','*.txt']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['eash-cli=cli.main:cli'],
    },
    extras_require={
        'dev': open('requirements-dev.txt', 'r').readlines()
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6'
)
