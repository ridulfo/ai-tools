from setuptools import setup
from pathlib import Path

def get_install_requires():
    """Returns requirements.txt parsed to a list"""
    fname = Path(__file__).parent / 'requirements.txt'
    targets = []
    if fname.exists():
        with open(fname, 'r') as f:
            targets = f.read().splitlines()
    return targets 

setup(
    name='ai',
    version='0.1',
    description='A local LLM in the command line',
    author='ridulfo',
    packages=['ai'],
    install_requires=get_install_requires(),
    entry_points={
        'console_scripts': [
            'ai = ai:main'
        ]
    }
)
