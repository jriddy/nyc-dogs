import setuptools


setuptools.setup(
    name='tornado-ex',
    version='0.1.0',
    install_requires=[
        'attrs',
        'tornado',
    ],
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    extras_require={
        'tests': [
            'flake8',
            'pytest',
            'requests',
        ],
    },
    include_package_data=True,
)
