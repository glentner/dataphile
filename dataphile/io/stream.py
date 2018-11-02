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

"""Stream data from files.
   dataphile.io.stream

   Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


# standard libs
import os
import sys
import time
import functools
import itertools
from typing import Any, List, IO, Union, Generator, Iterable

# internal libs
from abc import ABC as AbstractBase, abstractproperty


# used to represent both buffer types.
BuffType = Union[bytes, str]

class BaseStream(AbstractBase):
    """
    Generic Stream base class.

    This holds common functionality and enforces inheritance
    requirements, such is a derived `read` method.
    """

    def __init__(self, *sources: str, **options: Any) -> None:
        """
        Initialize with input file 'sources'.

        Arguments
        ---------
        *sources: str
            Valid file paths to initialize input files with.

        **options: Any
            Named parameters are forwarded to the initializer.
            For example, encoding='latin-1'.
        """

        self._active = None  # must be before self.sources assignment
        self.options = options  # must before self.sources assignment
        self.sources = sources

        self._active_id = 0
        if not self.sources:
            self._active = self._default_source
        else:
            for source in self.sources:
                if not os.path.exists(source):
                    raise ValueError(f'{self.__class__.__qualname__}.__init__: '
                                     f'{source} is not a file.')
            self.active = self.sources[0]

    @abstractproperty
    def _mode(self) -> str:
        """Passed to `open` command."""
        raise NotImplementedError()

    @abstractproperty
    def _sentinel(self) -> None:
        """Sentinel value for `iter`."""
        raise NotImplementedError()

    @abstractproperty
    def _default_source(self) -> IO:
        """Either `sys.stdin` or `sys.stdin.buffer`."""
        raise NotImplementedError()

    @property
    def sources(self) -> List[str]:
        """List of file paths used for stream."""
        return self._sources

    @sources.setter
    def sources(self, other: List[str]) -> None:
        """Validate and assign sources."""
        if len(other) < 1:
            self._sources = list()
            self._active = self._default_source
        else:
            for i, value in enumerate(other):
                if not isinstance(value, str):
                    raise ValueError(f'{self.__class__.__qualname__}.sources expects List[str], '
                                     f'given {type(value)} at position {i}.')
            self._sources = list(other)
            self.active = self._sources[0]

    @property
    def active(self) -> IO:
        """The currently active IO."""
        return self._active

    @active.setter
    def active(self, other: str) -> None:
        """Validate and initialize next active IO."""
        if not isinstance(other, str):
            raise ValueError(f'{self.__class__.__qualname__}.active expects a <str> (file path), '
                             f'given {other}({type(other)}).')
        next_active = open(other, mode=self._mode, **self.options)
        if self._active is not None and self._active is not self._default_source:
            self._active.close()
        self._active = next_active

    def _next_active(self) -> None:
        """Cycle the active source."""
        self._active_id += 1
        self.active = self.sources[self._active_id]

    def read(self, buffsize: int=1024**2) -> BuffType:
        """Read bytes from currently active IO."""
        buff = self.active.read(buffsize)
        if buff == self._sentinel:
            try:
                self._next_active()
                return self.read(buffsize)
            except IndexError:
                return self._sentinel
        else:
            return buff

    def iterbuffers(self, buffsize: int) -> Generator[str, BuffType, None]:
        """Yield buffers of size 'buffsize'."""
        yield from iter(functools.partial(self.read, buffsize),
                        self._sentinel)

    def __del__(self) -> None:
        """Ensure the active IO is closed."""
        if self.active is not self._default_source:
            self._active.close()

    def __exit__(self, *errs) -> None:
        """Context manager exit."""
        self.__del__()

    def __enter__(self) -> 'BaseStream':
        """Context manager enter."""
        return self

    def __str__(self) -> str:
        """String representation."""
        sources = ', '.join(self.sources)
        options = ', '.join([f'{key}={value}' for key, value in self.options.items()])
        clsname = f'{self.__class__.__name__}'
        return f'<{clsname}({sources}, {options})>'

    def __repr__(self) -> str:
        """Representation."""
        return str(self)


class BinaryStream(BaseStream):
    """An Stream that returns `binary` buffers."""

    _mode = 'rb'
    _sentinel = b''
    _default_source = sys.stdin.buffer


class TextStream(BaseStream):
    """An Stream that returns `str` buffers."""

    _mode = 'r'
    _sentinel = ''
    _default_source = sys.stdin

    def readline(self) -> str:
        """Return the next line."""
        line = self.active.readline()
        if line == self._sentinel:
            try:
                self._next_active()
                return self.readline()
            except IndexError:
                return self._sentinel
        else:
            return line

    def iterlines(self) -> Generator[int, str, None]:
        """Yields back whole lines."""
        yield from iter(self.readline, self._sentinel)

    def readlines(self) -> List[str]:
        """Return all lines from file."""
        return list(self.iterlines())


class LiveStream(BaseStream):
    """
    Similar to a normal Stream, but all files remain open and will
    be cycled through indefinitely waiting for new data.
    See Also:
        BaseStream
    """
    _latency = 0.1

    def __init__(self, *sources, latency: float=0.1, **options) -> None:
        """Opens all files at start."""

        self.latency = latency
        self.options = options
        self.sources = sources

        if not sources:
            self._handles = itertools.cycle([self._default_source])
        else:
            self._handles = itertools.cycle([open(source, mode=self._mode, **options)
                                             for source in sources])
        self._active = next(self.handles)

    @property
    def latency(self) -> float:
        """Seconds to wait between active sources."""
        return self._latency

    @latency.setter
    def latency(self, value: float) -> None:
        """Coerse and assign value."""
        self._latency = float(value)

    @property
    def active(self) -> IO:
        """Currently active handle."""
        return self._active

    @active.setter
    def active(self, other: str) -> None:
        raise NotImplementedError('Cannot set the active handle for a LiveStream.')

    @property
    def sources(self) -> List[str]:
        """List of file paths used for stream."""
        return self._sources

    @sources.setter
    def sources(self, other: List[str]) -> None:
        """Validate and assign sources."""
        for i, value in enumerate(other):
            if not isinstance(value, str):
                raise ValueError(f'{self.__class__.__qualname__}.sources expects List[str], '
                                 f'given {type(value)} at position {i}.')
        self._sources = list(other)
        # the self.active assignment is removed from a LiveStream

    @property
    def handles(self) -> Iterable[IO]:
        """Cycler of open IO handles."""
        return self._handles

    def read(self, buffsize: int=1024**2) -> BuffType:
        """Read buffer of size 'buffsize' from active handle."""
        buff = self.active.read(buffsize)
        if buff == self._sentinel:
            self._active = next(self.handles)
            time.sleep(self.latency)
            return self.read(buffsize)
        else:
            return buff

    def __del__(self) -> None:
        """Close all file handles."""
        if self.sources:
            for i, handle in enumerate(self.handles):
                handle.close()
                if i > len(self.sources):
                    break  # would never exit otherwise


class LiveBinaryStream(LiveStream):
    """
    Reads binary data from a LiveStream.
    See Also:
        LiveStream
    """
    _mode = 'rb'
    _sentinel = b''
    _default_source = sys.stdin.buffer


class LiveTextStream(LiveStream):
    """
    Reads text from a LiveStream.
    See Also:
        LiveStream
    """

    _mode = 'r'
    _sentinel = ''
    _default_source = sys.stdin

    def readline(self) -> str:
        """Return the next line."""
        line = self.active.readline()
        if line == self._sentinel:
            self._active = next(self.handles)
            time.sleep(self.latency)
            return self.readline()
        else:
            return line

    def iterlines(self) -> Generator[int, str, None]:
        """Yields back whole lines."""
        yield from iter(self.readline, self._sentinel)
