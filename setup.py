#coding=utf-8

import sys
from setuptools import setup

setup(
    name='xcmdparser',        
    version='0.1.0',        
    description='A function to parse command lines in wide-spread simple form with optional fields.',
    author='Sergey Zakharov',
    author_email='sergzach@gmail.com',
    packages=['xcmdparser'],
    package_dir={'xcmdparser': 'xcmdparser'},
    python_requires='>=2.7',
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
