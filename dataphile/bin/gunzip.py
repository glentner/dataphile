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

"""Decompress zlib compressed files (gzip compatible)."""

# standard libs
import sys
import argparse
import platform

# internal libs
from ..io.stream import BinaryStream
from ..io.zlib import iterdecompress

if platform.system() == 'Windows':
    # FIXME: how do we ignore broken pipes on windows?
    pass
else:
    from signal import signal, SIGPIPE, SIG_DFL  # ignore broken pipes
    signal(SIGPIPE, SIG_DFL)


parser = argparse.ArgumentParser(description=__doc__.split('\n')[0].strip())
parser.add_argument('source', metavar='FILE', default=[], nargs='?',
                    help='path to file')
parser.add_argument('-b', '--buffersize', type=float, default=1.0,
                    help='buffer size (in MB)')
parser.add_argument('--encoding', default='utf-8',
                    help='encoding for data')

def main() -> int:
    """Entry point for 'stream' command."""

    try:
        argv = parser.parse_args()
        buffsize = int(argv.buffersize * 1024**2)

        with BinaryStream(*argv.source) as stream:
            for buff in iterdecompress(stream.iterbuffers(buffsize),
                                       encoding=argv.encoding):
                sys.stdout.write(buff)

    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.buffer.flush()

    return 0
