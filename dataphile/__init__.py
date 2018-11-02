# This file is part of the Dataphile package.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Package initialization for Dataphile package."""

# standard libs
import platform
import sys

# internal libs
from .core.logging import log

from .__meta__ import __version__

if sys.version_info < (3, 5):
    print('dataphile requires at least Python 3.5 to run.')
    sys.exit(1)


def main():
    """Main entry point for dataphile."""

    try:
        log.info("Starting Dataphile {}".format(__version__))
        log.info("{} {} detected".format(platform.python_implementation(),
                                            platform.python_version()))

    except KeyboardInterrupt:
        log.error("Stopping dataphile with KeyboardInterrupt")
        return 0

    except SystemExit:
        log.info("Stopping dataphile with SystemExit")
        return 0
