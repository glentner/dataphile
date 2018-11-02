# -*- coding: utf-8 -*-
# This file is part of the Dataphile Project.
# Dataphile - A suite of software for data acquisition and analysis in Python.
# Copyright (c) 2018 Geoffrey Lentner <glentner@nd.edu>
#
# Dataphile is free software; you can redistribute it  and/or modify it under the terms of the GNU
# General Public License (v3.0) as published by the Free Software Foundation,  either version 3 of
# the License, or (at your option) any  later version. WARRANTY; without even the implied warranty
# of MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.  See the  GNU General  Public License
# (v3.0) for more details.
#
# You should have received a copy of the GNU General Public License (v3.0) along with this program.
# If not, see <http://www.gnu.org/licenses/>.

"""Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


# Execute with:
# $ python -m dataphile

import sys
import dataphile  # noqa

if __package__ is None and not hasattr(sys, 'frozen'):
    # It is a direct call to __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

if __name__ == '__main__':
    sys.exit(dataphile.main())
