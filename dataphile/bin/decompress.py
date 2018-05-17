"""scripts.gunzip
   Reverse 'gzip' compression (inplace or in flight).
   With no FILE, or when FILE is -, read standard input.

   Copyright (c) New York Power Authority 2018. All rights reserved.
   Digital Analytics Team. Geoffrey Lentner <geoffrey.lentner@nypa.gov>
"""

# standard libs
import os
import sys
import gzip
import argparse
from typing import Generator

# internal libs
from ..io.stream import Stream
from ..io.common import select_compression, compression_formats

parser = argparse.ArgumentParser(description='\n'.join(__doc__.split('\n')[1:]))
parser.add_argument('source', help='paths to gzip compressed files',
                    metavar='FILE', nargs='*', default=[sys.stdin.buffer])
parser.add_argument('-b', '--buffersize', help='size of buffer (in kB)',
                    type=int, default=256)

compression_type = parser.add_mutually_exclusive_group()
compression_type.add_argument('--gzip', help='use GZIP algorithm', action='store_true')
compression_type.add_argument('--lzma', help='use LZMA algorithm', action='store_true')
compression_type.add_argument('--bzip', help='use BZ2 algorithm', action='store_true')

def check_compression_option(opt: argparse.Namespace):
    """
    """
    default = None
    for name in 'gzip', 'lzma', 'bzip':
        if getattr(opt, name) is True:
            default = name
    if default is None:
        if not opt.source:
            raise ValueError('must specify compression algorithm when reading from <stdin>.')
        else:
            handles = list()  # List[BufferedReader]
            for i, path in enumerate(opt.source):
                reader = select_compression(path)
                if reader is None:
                    raise ValueError('No recognized file extension for {}'.format(path))
                else:
                    handles.append(reader(path, mode='rb'))
    else:
        reader = compression_formats[default]['reader']
        if not opt.source:
            raise NotImplementedError('decompress is not finished')


def main() -> int:
    """Entry point for 'decompress' command."""

    try:
        opt = parser.parse_args()
        buffersize = opt.buffersize * 1024
        if opt.source is None:

        with

        for path in opt.input_files:
            with gzip.open(path, 'rb') as infile, open(path.strip('.gz'), 'wb') as outfile:
                shutil.copyfileobj(infile, outfile)
            if opt.keep_original_files is False:
                os.remove(path)

    except BrokenPipeError:
        pass
    return 0
