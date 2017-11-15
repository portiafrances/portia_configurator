import os
del os.link

from setuptools import setup

setup(name='configurator',
      version='0.8.4',
      description='Include in projects which need configuration from commandline and config files',
      url='https://github.com/tomanizer/configurator',
      author='Thomas Haederle',
      author_email='thomas.haederle@gmail.com',
      license='MIT',
      packages=['configurator'],
      install_requires=['argparseui', 'ConfigParser', 'argparse', 'PyQt4',],
      zip_safe=False)