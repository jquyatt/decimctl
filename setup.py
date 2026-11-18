# Modified by the decimator-net project for its downstream build.
from setuptools import setup

setup(name='decimctl',
      version='0.4+decimatornet.1',
      description='Library for controlling products from Decimator Design',
      url='https://github.com/jquyatt/decimctl',
      author='Quentin Smith',
      author_email='quentin@mit.edu',
      license='Apache 2.0',
      packages=['decimctl'],
      scripts=[
          'bin/decimctl',
      ],
      install_requires=[
          'pylibftdi',
      ],
      zip_safe=True)
