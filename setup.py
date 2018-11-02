#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file is part of the Dataphile Project.
# Dataphile - A suite of software for data acquisition and analysis in Python.
# Copyright (c) 2018 Geoffrey Lentner <glentner@gmail.com>
#
# Dataphile is free software; you can redistribute it  and/or modify it under the terms of the GNU
# General Public License (v3.0) as published by the Free Software Foundation,  either version 3 of
# the License, or (at your option) any  later version. WARRANTY; without even the implied warranty
# of MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.  See the  GNU General  Public License
# (v3.0) for more details.
#
# You should have received a copy of the GNU General Public License (v3.0) along with this program.
# If not, see <http://www.gnu.org/licenses/>.

"""Setup and installation script for Dataphile project.
   setup.py

   Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

# standard libs
import os
from setuptools import setup, find_packages

# internal libs
from dataphile.__meta__ import (__appname__,
                                __version__,
                                __authors__,
                                __contact__,
                                __license__)


CMD_PREFIX = 'data.'  # Change this to '' to remove prefix on all commands
TOOLS = ['{prefix}{name}=dataphile{module}:main'.format(prefix=CMD_PREFIX, name=name, module=module)
         for name, module in {'phile':   '',  # TODO: 'main' application remains undecided
                              'stream':  '.bin.stream',
                              'groupby': '.bin.groupby',
                              'gunzip':  '.bin.gunzip',
                              # TODO: 'connect': '.bin.connect',
                              # TODO: 'watch':   '.bin.watch',
                              # TODO: 'monitor': '.bin.monitor',
                              # TODO: 'find':    '.bin.find',
                              # TODO: 'search':  '.bin.search',
                              # TODO: 'unique':  '.bin.unique',
                              # TODO: 'add':     '.bin.add',
                              # TODO: 'mean':    '.bin.mean',
                              # TODO: 'select':  '.bin.select',
                              # TODO: 'where':   '.bin.where',
                              # TODO: 'dropna':  '.bin.dropna',
                              }.items()]


def readme_file():
    """Use README.md as long_description."""
    with open(os.path.join(os.path.dirname(__file__), "README.md"), 'r') as readme:
        return readme.read()


setup(
    name             = __appname__,
    version          = __version__,
    author           = __authors__,
    author_email     = __contact__,
    description      = ('Data Science Tool'),
    license          = __license__,
    keywords         = 'data science tools analytics optimization',
    url              = 'https://readthedocs.com/dataphile',
    packages         = find_packages(),
    long_description = readme_file(),
    classifiers      = ['Development Status :: 3 - Alpha',
                        'Topic :: Scientific/Engineering',
                        'Programming Language :: Python :: 3.5',
                        'Programming Language :: Python :: 3.6',
                        'Programming Language :: Python :: 3.7',
                        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)', ],
    install_requires = ['numpy', 'scipy', 'matplotlib', 'seaborn', 'pandas', 'astropy', 'tqdm',
                        'h5py', 'logalpha'],
    entry_points     = {'console_scripts': TOOLS},
)
