from setuptools import setup

setup(
    name='cos',
    version='0.1',
    py_modules=['cos'],
    install_requires=[
        'Click',
        'ipython',
    ],
    entry_points='''
        [console_scripts]
        cos=cos:cli
    ''',
)

