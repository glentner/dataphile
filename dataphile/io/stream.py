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

"""Stream data from files.
   dataphile.io.stream

   DataPhile, 0.1.3
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


# standard libs
import os
import re
import sys
import time
from typing import Any, Union, List, Dict, Tuple, IO, Callable, Generator, Iterator

# internal libs
from .common import select_reader, FileTypes
from ..core.logging import log
from ..core.wrappers import timeout


class Stream:
    """File I/O manager."""

    def __init__(self, *files: Union[str,IO], live: bool=False, watch: bool=False, **options: Any):
        """Create a new 'Stream'.

        Parameters
        ----------
        *files: [str,IO]
            File paths or file-like objects to read from.
        live: bool (default=False)
            Persist existing file handles and wait for new data.
        watch: bool (default=False)
            Accept new file paths from <stdin> to read from.
        **options: Any
            Further keyword arguments passed to the file *.open(...) methods.
        """
        # Assignments are transacted by *.setter property methods
        self.live = live
        self.watch = watch
        self.options = options
        if watch is True and not files:
            self.files = []
        elif not files:
            self.files = [sys.stdin.buffer]
        else:
            self.files = list(files)

    @property
    def live(self) -> bool:
        """Create 'live' connection to files (i.e., wait for more data to arrive)."""
        return self.__live

    @live.setter
    def live(self, value: bool) -> None:
        """Set live mode."""
        if value not in (True, False):
            raise TypeError('`Stream.live` setting is either True or False.')
        else:
            self.__live = value

    @property
    def watch(self) -> bool:
        """Accept new file locations from <stdin>."""
        return self.__watch

    @watch.setter
    def watch(self, value: bool) -> None:
        """Set 'watch' mode."""
        if value not in (True, False):
            raise TypeError('`Stream.watch` setting is either True or False.')
        else:
            self.__watch = value

    @property
    def options(self) -> Dict[str,Any]:
        """Key-word arguments to pass to file opener calls (e.g., encoding='utf-8')."""
        return self.__options

    @options.setter
    def options(self, value: Dict[str,Any]) -> None:
        """Set options dictionary for file opening."""
        if not isinstance(value, dict) or not all(isinstance(key, str) for key in value.keys()):
            raise ValueError('`Stream.options` must be type Dict[str,Any].')
        else:
            self.__options = value.copy()

    @property
    def files(self) -> List[IO]:
        return list(self.__files.values())

    @files.setter
    def files(self, name_or_buffers: List[Union[str, IO]]) -> None:
        """Assign/open file objects."""
        __files = dict()  # Dict[str,IO]
        for i, item in enumerate(name_or_buffers):
            if isinstance(item, str):
                __files[item] = open(item, mode='rb', **self.options)
            elif isinstance(item, FileTypes):
                __files[item.name] = item
            else:
                raise TypeError(('Item {} in `Stream.files` assignment is not a valid type. '
                                 '`io.TextIOWrapper` or `io.BufferedReader` accepted. '
                                 'Received {}').format(i+1, type(item)))

        # make assignment only after successful construction
        self.__files = __files

    def __enter__(self):
        """Used by context manager to open files."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Used by context manager to safely exit."""
        self.close_all()

    def remove(self, name: str) -> None:
        """Attempt to remove file by 'name' from dictionary."""
        self.close(name)
        del self.__files[name]

    def remove_all(self) -> None:
        """Attempt to remove all files from dictionary."""
        for name in self.__files.keys():
            self.remove(name)

    def close_all(self) -> None:
        """Close all opened files."""
        for name in self.__files.keys():
            self.close(name)

    def close(self, name: str) -> None:
        """Attempt to close the file by 'name'."""
        try:
            self.__files[name].close()
        except ValueError as err:
            pass  # std{out,in} don't close

    def __iter__(self) -> Iterator[Union[str, bytes]]:
        """Iterate over all files (as if from a single file)."""
        yield from self.readlines()

    def read(self, buffersize: int=1024) -> Generator[Union[str, bytes], None, None]:
        """Read all data from each open file."""
        for fp in self.files:
            data = True
            while data:
                data = fp.read(buffersize)
                yield data

    def readlines(self, buffersize: int=1024) -> Generator[Union[str,bytes], None, None]:
        """Read all data from each open file in whole line increments."""
        for fp in self.files:
            data = True
            while data:
                data = fp.read(buffersize) + fp.readline()
                yield data

    def read_live(self, buffersize: int=1024, latency: float=0.1) -> Generator[Union[str, bytes], None, None]:
        """Yield back chunks of data of size 'buffersize' and await new data.

           Parameters
           ----------
           buffersize: int (default=1024)
               Number of bytes to read at a time.

           latency: float (default=0.1)
               Number of seconds to wait before attempting to read data again.

           Yields
           ------
           buffer: bytes
               Data from open files.
        """
        try:
            while True:
                yield from self.read(buffersize)
                time.sleep(latency)
                if self.watch is True:
                    self.__update_files()
        except KeyboardInterrupt:
            pass

    def readlines_live(self, buffersize: int=1024, latency: float=0.1) -> Generator[Union[str, bytes], None, None]:
        """Yield back chunks of data of size 'buffersize' in whole line increments and await new data.

           Parameters
           ----------
           buffersize: int (default=1024)
               Number of bytes to read at a time.
           latency: float (default=0.1)
               Number of seconds to wait before attempting to read data again.
               Only relavent when live==True.

           Yields
           ------
           buffer: bytes
               Data from open files.
        """
        try:
            while True:
                yield from self.readlines(buffersize)
                time.sleep(latency)
                if self.watch is True:
                    self.__update_files()
        except KeyboardInterrupt:
            pass

    def __remove_old_files(self) -> None:
        """Check existing file handles and remove any that no longer exist."""
        for path in self.__files.keys():
            if path not in ('<stdin>',) and not os.path.isfile(path):
                log.warning('removing "{}" because it does not exist.'.format(path))
                self.remove(path)

    @timeout(1, action=None)
    def __check_new_file(self) -> None:
        """Check for new files from <stdin>. A timeout of 1-sec prevents blocking."""
        return sys.stdin.readline().strip()

    def __update_files(self) -> None:
        """Remove non-existent files and check <stdin> for file paths."""
        # continue to read file paths off <stdin> until None is returned (after 1-sec delay)
        newfiles = list()  # List[str]
        while True:
            path = self.__check_new_file()
            if path is not None:
                newfiles.append(path)
            else:
                break
        for path in newfiles:
            if not os.path.isfile(path):
                if path in self.__files:
                    log.warning('removing "{}" from sources as file no longer exists.'.format(path))
                    self.remove(path)
                else:
                    log.warning('ignoring "{}" because it is not a file.'.format(path))
            else:
                if path in self.__files:
                    log.debug('ignoring "{}" because it is already a source.'.format(path))
                else:
                    self.__files[path] = open(path, mode='rb', **self.options)
        # remove missing/deleted files _after_ checking
        # if the file was sent through <stdin> _because_ it was deleted, let it
        # go through the above mechanism (with a single notification) instead of
        # being removed here _and_ then being echoed through.
        self.__remove_old_files()

