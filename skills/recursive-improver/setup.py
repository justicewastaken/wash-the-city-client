from setuptools import setup

setup(
    name='recursive-improver',
    version='0.1.0',
    py_modules=['improver_cli'],
    entry_points={
        'console_scripts': [
            'recursive-improver = improver_cli:main',
        ],
    },
)