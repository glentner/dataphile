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

"""Dynamic/colorized logging facility.
   dataphile.core.logging

   Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

# standard libs
import datetime as dt

# external libs
from logalpha import ConsoleHandler, BaseLogger

# simple console logger
_basic_console_handler = ConsoleHandler(level='info',
                                        template='{level} {timestamp} {message}',
                                        timestamp=lambda: dt.datetime.now().strftime('%H:%M:%S'))

# _basic_file_handler = FileHandler(template='{LEVEL}:num {timestamp} {name}: {message}',
#                                   timestamp=lambda: dt.datetime.now().strftime('%H:%M:%S'))

log = BaseLogger([_basic_console_handler])
