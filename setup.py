#!/usr/bin/python3 -S
import os
import sys
import uuid
from setuptools import setup
from pkgutil import walk_packages


def compat(min_version):
    ''' @min_version: (#str) minimum version number formatted like |2.7|
            or |2.7.6|
        -> (#bool) |True| if the system version is at least @min_version
    '''
    return sys.version_info >= tuple(map(int, min_version.split('.')))


PKG = 'vital'
PKG_NAME = 'vital-tools'
PKG_VERSION = '0.1.13'

pathname = os.path.dirname(os.path.realpath(__file__))


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return (line for line in lineiter if line and not line.startswith("#"))

install_reqs = parse_requirements(pathname + "/requirements.txt")


def find_packages(prefix=""):
    path = [prefix]
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            if name == 'vital.cache.async_decorators' and not compat('3.4'):
                pass
            else:
                yield name


setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='Vital tools for writing Python 3.4+ packages.',
    author='Jared Lunde',
    author_email='jared.lunde@gmail.com',
    url='https://github.com/jaredlunde/vital-tools',
    license="MIT",
    install_requires=list(install_reqs),
    packages=list(find_packages(PKG))
)
