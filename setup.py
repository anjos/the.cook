#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 04:08:29 2014 CEST

from setuptools import setup, find_packages

setup(

    name='the.cook',
    version='0.1.0',
    description='Idiap lunch management utility',
    url='http://gitlab.idiap.ch/aanjos/the.cook',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
      'setuptools',
      'sqlalchemy',
      'reportlab',
    ],

    namespace_packages=[
      "the",
      ],

    entry_points={
      'console_scripts': [
        'lunch = the.cook.scripts.lunch:main',
        ],
      },

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      ],

    )
