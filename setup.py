#!/usr/bin/env python

from setuptools import setup

import os
import re

base_path = os.path.dirname(__file__)

fp = open(os.path.join(base_path, 'pycalq', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'",
                     re.S).match(fp.read()).group(1)
fp.close()

version = VERSION


def read(fname):
    try:
        path = os.path.join(os.path.dirname(__file__), fname)
        return open(path).read()
    except IOError:
        return ""

requirements = ['six==1.7.3', 'urllib3>=1.2,<2.0']
test_requirements = ['pytest',
                     'pytest-cov']

setup(
    name='pyCalq',
    version=version,
    license='MIT',
    description="Unofficial Calq client library.",
    long_description=read('DESCRIPTION.rst'),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='',
    author='Friedrich Kauder',
    author_email='fkauder@gmail.com',
    url='https://github.com/FriedrichK/pyCalq.git',
    packages=['pycalq'],
    test_suite='pycalq.tests',
    install_requires=requirements,
    tests_require=test_requirements,
)
