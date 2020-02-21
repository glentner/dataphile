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

"""Incremental compression and decompression of data."""

# standard libs
import zlib
import lzma
import bz2
from typing import Iterable, Generator, Union, Dict, Any


COMPRESSORS = {
    'gzip': {
        'init': zlib.compressobj,
        'args': [],
        'kwargs': {'method': zlib.DEFLATED, 'wbits': zlib.MAX_WBITS | 16, },
        'translation': {}},
    'lzma': {
        'init': lzma.LZMACompressor,
        'args': [],
        'kwargs': {},
        'translation': {'level': 'preset'}},
    'bzip': {
        'init': bz2.BZ2Compressor,
        'args': [],
        'kwargs': {},
        'translation': {'level': 'compresslevel'}}
}


DECOMPRESSORS = {
    'gzip': {
        'init': zlib.decompressobj,
        'args': [zlib.MAX_WBITS | 32, ],
        'kwargs': {},
        'translation': {}},
    'lzma': {
        'init': lzma.LZMADecompressor,
        'args': [],
        'kwargs': {},
        'translation': {}},
    'bzip': {
        'init': bz2.BZ2Decompressor,
        'args': [],
        'kwargs': {},
        'translation': {}}
}


# typing information
SpecType = Dict[str, Any]
BuffType = Union[bytes, str]
CompressorType = Union[type(zlib.compressobj()), lzma.LZMACompressor, bz2.BZ2Compressor,
                       type(zlib.decompressobj()), lzma.LZMADecompressor, bz2.BZ2Decompressor]


def _init_compressor(spec: SpecType, **kwargs) -> CompressorType:
    """
    Helper function to prepare compressors/decompressors.

    Arguments
    ---------
    spec: SpecType
        Dictionary of compression/decompression method and parameters.

    **kwargs:
        Additional named parameters to pass to compressor/decompressor.
        Keys are remapped using the spec['translation'] dictionary.

    Returns
    -------
    compressor: CompressorType
        The instantiated compressor/decompressor (e.g., `lzma.LZMACompressor`).
    """
    # NOTE: the "translation" mechanism was used for the "level" parameter.
    # the level parameter is now actually passes as a first position argument.
    level = kwargs.pop('level', None)
    options = spec['kwargs']
    for key, value in kwargs.items():
        if key in spec['translation']:
            options[spec['translation'][key]] = value
        else:
            options[key] = value

    args = [] if level is None else [level, ]
    return spec['init'](*spec['args'], *args, **options)


def decompress(buffers: Iterable[BuffType], kind: str='gzip',
               encoding: str=None) -> Generator[None, BuffType, None]:
    """
    Decompress a stream of raw buffers using a given compression.

    Arguments
    ---------
    buffers: Iterable[bytes]
        Raw bytes of compressed data.

    kind: str (default='gzip')
        Which decompression (e.g., 'gzip', 'lzma', 'bzip').

    encoding: str (default=None)
        Specification to use for decoding the decompressed buffers.

    Yields
    ------
    data: str
        A decompressed and decoded string for every input buffer.
    """
    def decode(data: bytes) -> str:
        return data.decode(encoding)
    try:
        decompressor = _init_compressor(DECOMPRESSORS[kind])
        if encoding is not None:
            yield from map(decode, map(decompressor.decompress, buffers))
            if hasattr(decompressor, 'flush'):
                yield decompressor.flush()
        else:
            yield from map(decompressor.decompress, buffers)
            if hasattr(decompressor, 'flush'):
                yield decompressor.flush()
    except KeyError:
        raise KeyError(f'"{kind}" is not a valid compression scheme. '
                       f'Must be one of {COMPRESSORS.keys()}')


def compress(buffers: Iterable[str], kind: str='gzip', encoding: str=None,
             level: int=6) -> Generator[None, bytes, None]:
    """
    Compress a stream of strings using a given compression.

    Arguments
    ---------
    buffers: Iterable[str]
        String buffers to be compressed.

    kind: str (default='gzip')
        Which scheme (e.g., 'gzip', 'lzma', 'bzip').

    encoding: str (default='utf-8')
        Specification to use for encoding the strings to bytes objects.

    level: int (default=6)
        Compression level to use on data.

    Yields
    ------
    data: bytes
        An encoded and compressed bytes object for every input string.
    """
    def encode(data: str) -> bytes:
        return data.encode(encoding)
    try:
        compressor = _init_compressor(COMPRESSORS[kind])
        if encoding is None:
            yield from map(compressor.compress, buffers)
            yield compressor.flush()
        else:
            yield from map(compressor.compress, map(encode, buffers))
            yield compressor.flush()
    except KeyError:
        raise KeyError(f'"{kind}" is not a valid compression scheme. '
                       f'Must be one of {COMPRESSORS.keys()}')
