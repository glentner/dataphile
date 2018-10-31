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

   Dataphile, 0.1.3
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

# standard libs
import sys
import re
import inspect
from collections import defaultdict

from typing import Union, Callable, Dict, List, Any
from io import TextIOWrapper
from numbers import Number
import datetime as dt

ANSI_RESET = '\033[0m'
ANSI_COLORS = {prefix: {color: '\033[{prefix}{num}m'.format(prefix=i + 3, num=j)
                        for j, color in enumerate(['black', 'red', 'green', 'yellow', 'blue',
                                                   'magenta', 'cyan', 'white'])}
               for i, prefix in enumerate(['foreground', 'background'])}

LOG_COLORS = {'DEBUG': 'blue', 'INFO': 'green', 'WARNING': 'yellow',
              'ERROR': 'red', 'CRITICAL': 'magenta'}

LOG_LEVELS = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 4, 'CRITICAL': 5}
LOG_VALUES = dict((v, k) for k, v in LOG_LEVELS.items())


# Typing aliases
ResourceType = Union[str, TextIOWrapper, 'Connection']
CallbackType = Callable[[], Any]


class Handler:
    """
    Base handler for redirecting logging messages.
    """

    default_labels = ('message', 'level', 'LEVEL', 'num')

    def __init__(self, level: str='INFO', template: str='{message}', **callbacks: CallbackType) -> None:
        """
        Initialize attributes, resource, callbacks.
        """

        self.__resource = None  # CallbackType
        self.__counts = defaultdict(lambda: 0)

        self.callbacks = callbacks  # must come before self.template initialization
        self.template = template
        self.level = level

    @property
    def resource(self) -> ResourceType:
        """Access underlying resource (e.g., file object or database connection)."""
        return self.__resource

    @resource.setter
    def resource(self, other: ResourceType) -> None:
        """Validate and assign underlying resource."""

        if isinstance(other, str):
            self.__resource = open(other, mode='a')

        elif not all(hasattr(other, attr) for attr in ('__enter__', '__exit__', 'close')):
            raise TypeError(f'{self.__class__.__qualname__}.resource is expected to be a '
                            f'file-like or connection-like object (e.g., has \"__enter__\"), '
                            f'given, {type(other)}.')
        else:
            self.__resource = other

    @property
    def template(self) -> str:
        """Template defining the logging statement format."""
        return self.__template

    @template.setter
    def template(self, other: str) -> None:
        """Assign new value to template."""

        if not isinstance(other, str):
            raise TypeError(f'{self.__class__.__qualname__}.template should be {str}.')

        elif '{message}' not in other:
            raise ValueError(f'{self.__class__.__qualname__}.template requires that '
                             '{message} at least be present in the string.')

        else:
            for label, callback in self.callbacks.items():
                format_entry = '{' + label + '}'
                if format_entry not in other:
                    raise ValueError(f'{self.__class__.__qualname__}.template is missing '
                                     f'{format_entry} implied in keyword arguments.')

            for match in re.finditer(r'{(\w*)(:\S*}|})', other):
                label = match.groups()[0]
                format_entry = '{' + label + '}'
                if label not in self.callbacks.keys() and label not in self.default_labels:
                    raise KeyError(f'{self.__class__.__qualname__}.template contains '
                                   f'{format_entry} but \"{label}\" was provided as a callback (kwarg).')

            self.__template = other

    @property
    def callbacks(self) -> Dict[str, CallbackType]:
        """Access callbacks (usually, lambda functions)."""
        return self.__callbacks

    @callbacks.setter
    def callbacks(self, other: Dict[str, CallbackType]) -> None:
        """Validate and assign callbacks dictionary."""
        if not isinstance(other, dict):
            raise TypeError(f'{self.__class__.__qualname__}.callbacks should be {dict}, '
                            f'given {type(other)}')

        for key in other.keys():
            if not isinstance(key, str):
                raise TypeError(f'{self.__class__.__qualname__}.callbacks requires all keys to '
                                f'be string-like, found {key} -> {type(key)}')

        for label, callback in other.items():
            if not hasattr(callback, '__call__'):
                raise TypeError(f'{self.__class__.__qualname__}.callbacks requires all values be '
                                f'callable, {label} has no attribute \"__call__\".')

        for label, callback in other.items():
            if not len(inspect.signature(callback).parameters) == 0:
                raise ValueError(f'{self.__class__.__qualname__}.callbacks requires all callables/functions have '
                                 f'zero parameters, found {label}{inspect.signature(callback)}.')
        else:
            self.__callbacks = other

    @property
    def level(self) -> str:
        """Logging level for Handler."""
        return self.__level

    @level.setter
    def level(self, other: Union[str, Number]) -> None:
        """Validate and assign logging level for this Handler."""
        if isinstance(other, str):
            if other.upper() not in LOG_LEVELS.keys():
                raise ValueError(f'{self.__class__.__qualname__}.level expects one of '
                                 f'{tuple(LOG_LEVELS.keys())}')
            else:
                self.__level = other.upper()

        elif isinstance(other, Number):
            if int(other) not in LOG_LEVELS.values():
                raise ValueError(f'{self.__class__.__qualname__}.level accepts integers between 0-5'
                                 f', given {other}.')
            else:
                self.__level = LOG_VALUES[int(other)]

        else:
            raise TypeError(f'{self.__class__.__qualname__}.level requires either a string-like or '
                            f'number-like value, given {type(other)}.')

    @property
    def counts(self) -> Dict[str, int]:
        """Counter of number of times each level has been written to."""
        return self.__counts

    def __del__(self) -> None:
        """Release "resource"."""
        if hasattr(self.resource, 'close'):
            self.resource.close()

    def write(self, message: str, level: str, colorize: bool=False) -> None:
        """Filters out messages based on 'level' and sends to target resource."""

        # check valid level assignment
        if level.upper() not in LOG_LEVELS:
            raise ValueError(f'{self.__class__.__qualname__}.level expects one of '
                             f'{tuple(LOG_LEVELS.keys())}')

        # increment call count
        self.counts[level.upper()] += 1

        # only proceed if level is sufficient
        if LOG_LEVELS[level.upper()] < LOG_LEVELS[self.level]:
            return

        # initial construction has no formatting
        callback_results = {label: str(callback()) for label, callback in self.callbacks.items()}

        if '{level}' in self.template:
            callback_results['level'] = level.lower()

        if '{LEVEL}' in self.template:
            callback_results['LEVEL'] = level.upper()

        if '{num}' in self.template:
            callback_results['num'] = str(self.counts[level.upper()])

        if colorize is True:
            ANSI_CODE = ANSI_COLORS['foreground'][LOG_COLORS[level.upper()]]
            callback_results = {label: ANSI_CODE + value + ANSI_RESET
                                for label, value in callback_results.items()}

        message = self.template.format(**{'message': message, **callback_results})
        message = message.strip('\n') + '\n'
        self._write(message)

    def _write(self, message: str) -> None:
        """Flush prepared/formatted string 'message' to resource."""
        self.resource.write(message)
        self.resource.flush()

    def __str__(self) -> str:
        """String representation of Handler."""
        return (f'{self.__class__.__name__}(template=\'{self.template}\', '
                f'level=\'{self.level}\')')

    def __repr__(self) -> str:
        """String representation of Handler."""
        return str(self)


class FileHandler(Handler):
    """
    Handles logging messages targeting a file-like object.
    """

    def __init__(self, *args, file: Union[str, TextIOWrapper], **kwargs) -> None:
        """
        See Also:
        Handler.__init__()
            For full signature and descriptions.
        """
        super().__init__(*args, **kwargs)
        self.resource = file


class ConsoleHandler(Handler):
    """
    Handles logging messages targeting <stdout/stderr>.
    """

    default_stream = {'DEBUG':    sys.stdout,
                      'INFO':     sys.stdout,
                      'WARNING':  sys.stderr,
                      'ERROR':    sys.stderr,
                      'CRITICAL': sys.stderr}

    def __init__(self, *args, colorize: bool=True,
                 stderr_only: bool=False, **kwargs) -> None:
        """
        See Also:
        Handler.__init__()
            For full signature and descriptions.
        """
        super().__init__(*args, **kwargs)
        self.colorize = colorize
        if stderr_only is True:
            self.default_stream.update({'DEBUG': sys.stderr,
                                        'INFO': sys.stderr})

    def write(self, *args, level: str, **kwargs) -> None:
        """Writes to <stdout> for DEBUG/INFO, <stderr> otherwise."""
        self.resource = self.default_stream[level.upper()]
        super().write(*args, level=level, colorize=self.colorize, **kwargs)


# TODO: implement DBHandler
class DBHandler(Handler):
    """
    Handles logging messages targeting a database-like object.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize database connection."""
        raise NotImplementedError()

    def _write(self, message: str) -> None:
        """Reimplementation of _write sends 'message' to database."""
        raise NotImplementedError()


class BasicLogger:
    """
    Relays logging messages to all member handlers.
    """

    def __init__(self, handlers: List[Handler]) -> None:
        """
        Initialize list of member handlers.
        """
        self.__handlers = list()
        for handler in handlers:
            self.add_handler(handler)

    @property
    def handlers(self) -> List[Handler]:
        """Access to member handlers."""
        return self.__handlers

    def add_handler(self, handler: Handler) -> None:
        """Add a Handler to list of members."""
        if not isinstance(handler, Handler):
            raise TypeError(f'{self.__class__.__qualname__}.add_handler expects {Handler}, '
                            f'given {type(handler)}.')
        else:
            self.__handlers.append(handler)

    def write(self, *args, **kwargs) -> None:
        """Relays call to all handlers."""
        for handler in self.handlers:
            handler.write(*args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Calls write() with level='debug'."""
        self.write(message, *args, level='DEBUG', **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Calls write() with level='info'."""
        self.write(message, *args, level='INFO', **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Calls write() with level='warning'."""
        self.write(message, *args, level='WARNING', **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Calls write() with level='error'."""
        self.write(message, *args, level='ERROR', **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Calls write() with level='critical'."""
        self.write(message, *args, level='CRITICAL', **kwargs)

    def __str__(self) -> str:
        """String representation of Logger."""
        class_name = self.__class__.__name__
        left_spacing = ' ' * (len(class_name) + 2)
        handler_reprs = f',\n{left_spacing}'.join([str(handler) for handler in self.handlers])
        return f'{class_name}([{handler_reprs}])'

    def __repr__(self) -> str:
        """String representation of Logger."""
        return str(self)


# registry of loggers
LOGGERS = dict()  # Dict[str, BasicLogger]


_basic_console_handler = ConsoleHandler(template='{level} {timestamp} {message}',
                                        timestamp=lambda: dt.datetime.now().strftime('%H:%M:%S'))

# _basic_file_handler = FileHandler(template='{LEVEL}:num {timestamp} {name}: {message}',
#                                   timestamp=lambda: dt.datetime.now().strftime('%H:%M:%S'))

log = BasicLogger([_basic_console_handler])
