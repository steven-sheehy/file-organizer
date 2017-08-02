# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='organizer',
    version='0.0.1',
    description='Normalizes files within a target directory by renaming them to a canonical form',
    long_description=readme,
    author='Steven Sheehy',
    author_email='',
    url='https://github.com/stevensheehy/file-organizer',
    license=license,
    packages=find_packages(exclude=('test', 'docs')),
    entry_points={'console_scripts': ['organizer = organizer.main:main']},
    test_suite='TestCleaner'
)

