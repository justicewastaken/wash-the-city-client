from setuptools import setup, find_packages

setup(
    name='website-sales-pipeline',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # No external Python deps beyond standard library
    ],
    entry_points={
        'console_scripts': [
            'website-sales-pipeline = pipeline_cli:main',
        ],
    },
    include_package_data=True,
)