from setuptools import setup, find_packages
import sys

import fastentrypoints

packages = find_packages('.')
print(packages)

setup(
    name='cos',
    version='0.1',
    py_modules=['cos'],
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points='''
        [console_scripts]
        cos=coscli:main
    ''',
    packages=['coscli', 'coscli.launch', 'coslib'],
    package_dir = {'coslib': 'coslib/coslib'},

)

