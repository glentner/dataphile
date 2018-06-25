# -*- coding: utf-8 -*-
# This file is part of the DataPhile Project.
# DataPhile - A suite of software for data acquisition and analysis in Python.
# Copyright (c) 2018 Geoffrey Lentner <glentner@gmail.com>
#
# DataPhile is free software; you can redistribute it  and/or modify it under the terms of the GNU
# General Public License (v3.0) as  published by the Free Software Foundation,  either version 3 of
# the License, or (at your option) any  later version. WARRANTY; without even the implied warranty
# of MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.  See the  GNU General  Public License
# (v3.0) for more details.
#
# You should have received a copy of the GNU General Public License (v3.0) along with this program.
# If not, see <http://www.gnu.org/licenses/>.

"""Dynamic/colorized logging facility for DataPhile project.
   dataphile.core.logging

   DataPhile, 0.1.3
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


# standard lib
import io
import os
import sys
import platform
from typing import List, Union, Iterator
from datetime import datetime


ANSI_RESET = '\033[0m'
ANSI_COLORS = {prefix: {color: '\033[{prefix}{num}m'.format(prefix=i + 3, num=j)
                        for j, color in enumerate(['black', 'red', 'green', 'yellow', 'blue',
                                                   'magenta', 'cyan', 'white'])}
               for i, prefix in enumerate(['foreground', 'background'])}

LOG_COLORS = {'INFO':     'green',
              'DEBUG':    'blue',
              'WARNING':  'yellow',
              'CRITICAL': 'magenta',
              'ERROR':    'red'}


class Handler:
    """Encapsulates a message format and output vector (stdout/stderr or a file)."""

    def __init__(self, template: str='{msg}', file: str=None, background: str=None, foreground: str=None, **lambdas):
        """Initialize the Handler.

           Parameters
           ----------
           template: str, default='{msg}'
               Message template to be formatted. I.e., '...'.format(**lambdas).
               "msg" is a reserved keyword for the contents to be printed.

           file: str, default=None
               If provided this is a path to write to a file. Every message will be
               appended to this file.

           background: str, default=None
               Color for the text in the message when printed to stdout (e.g., 'red'). If None,
               the system handles this.

           foreground: str, default=None
               Color for the text in the message when printed to stdout (e.g., 'white'). If None,
               the system handles this.

           **lambdas:
               Lambda functions or other callable object. No arguments will be passed. If the object
               is not callable it is assumed to be static and will be formatted (e.g., `str(x)`).
               E.g., `timestamp=datetime.datetime.now`.
        """

        # members are protected, accessed/set with parameter syntax
        self.__template   = template
        self.__file       = file
        self.__background = background
        self.__foreground = foreground
        self.__lambdas    = lambdas

        if foreground is not None and foreground not in ANSI_COLORS['foreground']:
            raise ValueError('"{color}" is not a recognized foreground color. Options are {options}.'
                             .format(color=foreground,
                                     options=', '.join(ANSI_COLORS['foreground'].keys())))
        if background is not None and background not in ANSI_COLORS['background']:
            raise ValueError('"{color}" is not a recognized background color. Options are {options}.'
                             .format(color=background,
                                     options=', '.join(ANSI_COLORS['background'].keys())))

        for name, lambda_func in lambdas.items():
            if '{' + name + '}' not in template:
                raise ValueError('"{name}" is not in "template"'.format(name=name))

    @property
    def template(self) -> str:
        return self.__template

    @property
    def file(self) -> str:
        return self.__file

    @property
    def background(self) -> str:
        return self.__background

    @property
    def foreground(self) -> str:
        return self.__foreground

    @property
    def lambdas(self) -> dict:
        return self.__lambdas

    def write_to_file(self, msg: str, **options) -> None:
        """Write a message to `file`."""

        # gather and/or execute lambdas
        lambdas = {name: str(lambda_func) if not hasattr(lambda_func, '__call__') else str(lambda_func())
                   for name, lambda_func in self.lambdas.items()}

        with open(self.file, 'a') as file_object:
            print(self.template.format(msg=msg, **lambdas), file=file_object, **options)

    def write_to_console(self, msg: str, file=sys.stdout, **options) -> None:
        """Write a message to stdout/stderr using the print() function."""

        # initial lambda construction has no ansi formatting
        lambdas = {name: str(lambda_func) if not hasattr(lambda_func, '__call__') else str(lambda_func())
                   for name, lambda_func in self.lambdas.items()}

        # now apply formatting
        level = self.current_call_loglevel
        lambdas = {name: ANSI_COLORS['foreground'][LOG_COLORS[level]] + value + ANSI_RESET
                   for name, value in lambdas.items()}

        if self.foreground is None:
            message = msg
        else:
            message = ANSI_COLORS['foreground'][self.foreground] + msg + ANSI_RESET

        output = self.template.format(msg=message, **lambdas)
        if self.background is not None:
            output = ANSI_COLORS['background'][self.background] + output + ANSI_RESET

        print(output, flush=True, file=file, **options)

    def write(self, msg: str, level: str, file=sys.stdout, **options) -> None:
        """Generic function which writes the `msg` to the appropriate stream."""

        # set member so we can call on it
        self.current_call_loglevel = level.upper()

        if self.file is not None:
            self.write_to_file(msg, **options)
        else:
            self.write_to_console(msg, file=file, **options)


class LoggerBase:
    """Mixin class to implement logging functionality.

       This class does not implement an __init__ method so the setup of the logging
       features can be done in the derived classes __init__ method.
    """

    __defaultlevel__ = 'INFO'
    __loglevels__ = {'DEBUG': 1, 'INFO': 2, 'WARNING': 3, 'CRITICAL': 4, 'ERROR': 5}

    __level = __defaultlevel__
    # handlers = list()  # this creates duplicate handlers!

    def log(self, msg: str, level: str='INFO', **options) -> None:
        """Write `msg` to all :`handlers`."""

        if level.upper() not in self.__loglevels__:
            raise ValueError('"{level}" is not an available level. Options are {options}'
                             .format(level=level, options=', '.join(self.__loglevels__.keys())))

        elif self.__loglevels__[self.level] > self.__loglevels__[level]:
            # only print messages as/more severe as the current level
            return
        else:
            for handler in self.handlers:
                handler.write(msg, level, **options)

    def debug(self, msg: str, **options) -> None:
        """Write a message with level='DEBUG'."""
        self.log(msg, level='DEBUG', file=sys.stdout, **options)

    def info(self, msg: str, **options) -> None:
        """Write a message with level='INFO'."""
        self.log(msg, level='INFO', file=sys.stdout, **options)

    def warning(self, msg: str, **options) -> None:
        """Write a message with level='WARNING'."""
        self.log(msg, level='WARNING', file=sys.stderr, **options)

    def critical(self, msg: str, **options) -> None:
        """Write a message with level='CRITICAL'."""
        self.log(msg, level='CRITICAL', file=sys.stderr, **options)

    def error(self, msg: str, **options) -> None:
        """Write a message with level='ERROR'."""
        self.log(msg, level='ERROR', file=sys.stderr, **options)

    def add_handler(self, handler: Handler) -> None:
        """Add a 'handler' (of type `Handler`) to the list of used handlers."""
        if not isinstance(handler, Handler):
            raise TypeError('Logger.add_handler requires `Handler` type.')
        if not hasattr(self, 'handlers'):
            self.handlers = list()
        self.handlers.append(handler)

    @property
    def level(self) -> str:
        """Retrieve the logging `level` (e.g., INFO, DEBUG, ...)."""
        return self.__level

    @level.setter
    def level(self, value: Union[int, str]) -> None:
        """Set the logging level."""
        if isinstance(value, int):
            if value not in self.__loglevels__.values():
                raise ValueError('Available loglevels: {}'.format(self.__loglevels__))
            else:
                self.__level = {v: k for v, k in self.__loglevels__.items()}[value]
        elif isinstance(value, str):
            if value.upper() not in self.__loglevels__:
                raise ValueError('Can only set log level to one of {}'.format(list(self.__loglevels__)))
            else:
                self.__level = value.upper()

    @property
    def files(self) -> List[str]:
        """Return a list of file names where logging statements are being printed."""
        return [h.file for h in self.handlers if h.file is not None]

    @property
    def file_handles(self) -> List[io.TextIOWrapper]:
        """Returns a generator yielding open file handlers to all the files in use."""
        for filepath in self.files:
            with open(filepath, mode='a') as file_handle:
                yield file_handle


class Logger(LoggerBase):
    """Dedicated Logging object."""

    def __init__(self, loglevel: str='INFO', files: List[str]=None, folder: str=None, app: str='',
                 console: bool=True, template: str='{level} {time} {app} {msg}'):
        """Initialize the handlers."""

        # default level
        self.level = loglevel

        if platform.system() == 'Windows':
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')  # Windows compatible filename
        else:
            timestamp = datetime.now().strftime('%Y%m%d-%H:%M:%S')

        # send log messages to stdout
        if console is True:
            self.add_handler(Handler(template = template,
                                     level    = lambda: self.handlers[0].current_call_loglevel,
                                     time     = datetime.now,
                                     app      = app))

        # file output
        if files:
            for path in files:
                if not os.path.isdir(os.path.dirname(path)):
                    raise IOError('{} does not exist'.format(os.path.dirname(path)))
                else:
                    self.add_handler(Handler(template   = template,
                                            file       = path,
                                            level      = lambda: self.handlers[0].current_call_loglevel,
                                            time       = datetime.now,
                                            app        = app))

        if folder:
            if not os.path.isdir(os.path.dirname(folder)):
                raise IOError('{} is not a directory'.format(os.path.dirname(folder)))
            elif not os.path.isdir(folder):
                os.makedirs(folder)
            filename = '{}{}.log'.format(app + '-' if app else '', timestamp)
            self.add_handler(Handler(template   = template,
                                     file       = filename,
                                     level      = lambda: self.handlers[0].current_call_loglevel,
                                     app        = app,
                                     time       = datetime.now))


# shared instance across whole package
log = Logger()
