"""scripts.gunzip
   Reverse 'gzip' compression (inplace or in flight).
   With no FILE, or when FILE is -, read standard input.

   Copyright (c) New York Power Authority 2018. All rights reserved.
   Digital Analytics Team. Geoffrey Lentner <geoffrey.lentner@nypa.gov>
"""

# standard libs
import os, sys, gzip, argparse, shutil
from typing import Generator

parser = argparse.ArgumentParser(prog=__doc__.split('\n')[0].split('.')[-1].strip(),  # gunzip
                                 description='\n'.join(__doc__.split('\n')[1:]))
parser.add_argument('input_files', help='paths to gzip compressed files',
                    metavar='FILES', nargs='?', type=str, default=[])

parser.add_argument('-c', '--stdout', help='write on standard output, keep original files unchanged',
                    dest='use_stdout', action='store_true')
parser.add_argument('-k', '--keep', help='keep (do not delete) input files',
                    dest='keep_original_files', action='store_false')


def read(*paths: str) -> Generator[bytes, None, None]:
    """Yield back decompressed data from file 'paths'."""
    if not paths:
        yield from map(gzip.decompress, sys.stdin.buffer)
    else:
        for path in paths:
            with gzip.open(path, 'rb') as infile:
                yield from infile


def main() -> int:
    """Entry point."""
    try:
        opt = parser.parse_args()
        if opt.use_stdout is True or not opt.input_files:
            for data in read(*opt.input_files):
                sys.stdout.buffer.write(data)
        else:
            for path in opt.input_files:
                with gzip.open(path, 'rb') as infile, open(path.strip('.gz'), 'wb') as outfile:
                    shutil.copyfileobj(infile, outfile)
                if opt.keep_original_files is False:
                    os.remove(path)
    except BrokenPipeError:
        pass
    return 0
