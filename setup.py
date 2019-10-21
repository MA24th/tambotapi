#!/usr/bin/env python
from setuptools import setup
from io import open


def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()


setup(name='tambotapi',
      version='0.1.0',
      description='TamTam Bot API Framework',
      long_description=read('README.rst'),
      long_description_content_type="text/x-rst",
      author='Mustafa Asaad',
      author_email='ma24th@yahoo.com',
      url='https://github.com/MA24th/tambotapi',
      packages=['tambotapi'],
      license='GPLv2',
      keywords='tamtam bot api framework',
      install_requires=['requests', 'six'],
      extras_require={
          'json': 'ujson',
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ]
      )
