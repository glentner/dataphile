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

"""Package initialization for Dataphile project.
   dataphile.__init__

   Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

# standard libs
import platform
import sys

# internal libs
from .core.logging import log

from .__meta__ import __appname__, __version__ , __authors__ , __license__

if sys.version_info < (3, 5):
    print('dataphile requires at least Python 3.5 to run.')
    sys.exit(1)


def main():
    """Main entry point for dataphile."""

    try:
        log.info("Starting Dataphile {}".format(__version__))
        log.info("{} {} detected".format(platform.python_implementation(),
                                            platform.python_version()))

        # app = DataphileApp(appname = __appname__,
                           # version = __version__,
                           # authors = __authors__,
                           # license = __license__)

        # app.start()

    except KeyboardInterrupt:
        log.error("Stopping dataphile with KeyboardInterrupt")
        return 0

    except SystemExit:
        log.info("Stopping dataphile with SystemExit")
        return 0
