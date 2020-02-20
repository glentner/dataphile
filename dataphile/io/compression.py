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

"""Zlib compression routines."""

# standard libs
import zlib
import functools
from typing import Iterable, Generator


def iterdecompress(buffers: Iterable[bytes], encoding: str='utf-8',
                   **kwargs) -> Generator[None, str, None]:
    """
    Yields back buffers that have been decompressed and decoded.

    Arguments
    ---------
    buffers: Iterable[bytes]
        Blocks of raw bytes data read from a gzipped file.

    encoding: str='utf-8'
        Used to decode the data from bytes to str.

    **kwargs:
        All additional named parameters are forwarded to `zlib.decompressobj`.

    Yields
    ------
    buffer: str
        A decompressed and decoded str block.

    See Also
    --------
    zlib - Compression compatible with gzip
    """
    decomp = zlib.decompressobj(16 + zlib.MAX_WBITS, **kwargs)
    yield from map(functools.partial(bytes.decode, encoding=encoding),
                   map(decomp.decompress, buffers))


def itercompress(buffers: Iterable[str], encoding: str='utf-8',
                 **kwargs) -> Generator[None, bytes, None]:
    """
    Yields back buffers that have been encoded and compressed.

    Arguments
    ---------
    buffers: Iterable[str]
        Blocks of raw bytes data read from a gzipped file.

    encoding: str='utf-8'
        Used to encode the data from str to bytes.

    **kwargs:
        All additional named parameters are forwarded to `zlib.compressobj`.

    Yields
    ------
    buffer: str
        A decompressed and decoded str block.

    See Also
    --------
    zlib - Compression compatible with gzip
    """
    comp = zlib.compressobj(level=zlib.Z_DEFAULT_COMPRESSION, **kwargs)
    yield from map(comp.decompress,
                   map(functools.partial(str.encode, encoding=encoding), buffers))
