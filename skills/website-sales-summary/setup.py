from setuptools import setup

setup(
    name='website-sales-summary',
    version='0.1.0',
    py_modules=['summary_cli'],
    entry_points={
        'console_scripts': [
            'website-sales-summary = summary_cli:write_summary',
        ],
    },
)