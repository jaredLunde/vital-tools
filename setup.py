#!/usr/bin/python3 -S
import os
import uuid
from setuptools import setup
from pip.req import parse_requirements
from pkgutil import walk_packages


PKG = 'vital'
PKG_NAME = 'vital-tools'
PKG_VERSION = '0.1.4'

pathname = os.path.dirname(os.path.realpath(__file__))


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(pathname + "/requirements.txt",
                                  session=uuid.uuid1())


def find_packages(prefix=""):
    path = [prefix]
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='Vital tools for writing Python 3.5+ packages.',
    author='Jared Lunde',
    author_email='jared.lunde@gmail.com',
    url='https://github.com/jaredlunde/vital-tools',
    license="MIT",
    install_requires=[str(ir.req) for ir in install_reqs],
    packages=list(find_packages(PKG))
)
