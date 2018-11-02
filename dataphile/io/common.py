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

"""Common methods for I/O tasks."""

# standard libs
import re
from typing import Union, Callable, IO
from io import TextIOWrapper, BufferedReader
import gzip, bz2, lzma, zipfile, tarfile


# IO for annotation, FileTypes for instance checking
FileTypes = TextIOWrapper, BufferedReader


compression_formats = {
    'gzip': {
        'pattern': '(?i)\.gz$',
        'reader': gzip.open},
    'bz2': {
        'pattern': '(?i)\.bz(2)?$',
        'reader': bz2.open},
    'xz': {
        'pattern': '(?i)\.(xz|lzma)$',
        'reader': lzma.open},
}
# aliases
compression_formats['lzma'] = compression_formats['xz']
compression_formats['bzip'] = compression_formats['bz2']


archive_formats = {
    'zip': {
        'pattern': '(?i)\.zip$',
        'reader': zipfile.ZipFile},
    'tar': {
        'pattern': '(?i)\.tar$',
        'reader': tarfile.open},
}


def select_reader(filepath: str) -> Callable[..., IO]:
    """Infer proper file opener based on filename extension.

       Parameters
       ----------
       filepath: str
           The path to a file.

       Returns
       -------
       reader: Callable[..., IO]
    """
    patterns = {x['pattern']: x['reader'] for x in compression_formats.values()}
    for pattern, reader in patterns.items():
        if re.search(pattern, filepath) is not None:
            return reader
    else:
        return open  # default


def select_compression(filepath: str) -> str:
    """Infer proper file compression based on filename extension.
       (e.g., for `pandas.DataFrame.to_csv(..., compression=???)`).

       Parameters
       ----------
       filepath: str
           The path to a file.

       Returns
       -------
       compression: str
           The propery compression format.
    """
    patterns = {spec['pattern']: x for x, spec in compression_formats.items()}
    for pattern, name in patterns.items():
        if re.search(pattern, filepath) is not None:
            return name
    else:
        return None  # default

