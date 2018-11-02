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

"""Dynamic/colorized logging facility."""

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
