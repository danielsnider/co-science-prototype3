from setuptools import setup

setup(
    name='cos',
    version='0.1',
    py_modules=['cos'],
    install_requires=[
        'Click',
        'ipython',
        'futures',
        'grpcio',
        'scikit-image',
        'tables',
        'pyyaml',
        'glob2',
    ],
    entry_points='''
        [console_scripts]
        cos=cos:main
    ''',
)

