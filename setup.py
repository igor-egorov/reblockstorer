from setuptools import setup

with open('requirements.txt') as reqs:
    requirements = reqs.read().strip().splitlines()

setup(
    name='ReBlockStorer',
    version='0.0.1',
    install_requires=requirements,
    packages=['reblockstorer', 'reblockstorer.proto'],
    entry_points={
        'console_scripts': [
            'reblockstore = reblockstorer.__main__:main'
        ]
    }
)
