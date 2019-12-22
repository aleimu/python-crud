# -*- coding:utf-8 -*-


import io
from setuptools import setup, find_packages

with io.open('tools_readme.md', 'rt', encoding='utf8') as f:
    readme = f.read()

version = '1.0.0'

requires = [
    'SQLAlchemy==1.3.3',
    'Flask==1.1.1',
    'Flask-SQLAlchemy==2.3.2',
    'MySQL-python==1.2.3',
    'requests==2.21.0',
    'redis==3.2.1',
    'celery==4.3.0',
    'xlrd==1.2.0',
    'xlwt==1.3.0',
]

setup(
    name='tools',
    version=version,
    description='tools models+func',
    long_description=readme,
    packages=find_packages(),
    package_data={
        '': ['*.md'],
    },
    platforms='any',
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,

    classifiers=[
        'Development Status :: 1 - Beta',
        'Framework :: python-curd',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
