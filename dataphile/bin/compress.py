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

"""Apply compression/decompression to data."""

# standard libs
import sys
import argparse
import platform

# internal libs
from ..io.stream import BinaryStream
from ..io.compression import compress, decompress

if platform.system() == 'Windows':
    # FIXME: how do we ignore broken pipes on windows?
    pass
else:
    from signal import signal, SIGPIPE, SIG_DFL  # ignore broken pipes
    signal(SIGPIPE, SIG_DFL)


parser = argparse.ArgumentParser(description=__doc__.split('\n')[0].strip())

parser.add_argument('sources', metavar='FILE', default=[], nargs='?',
                    help='path to file')

parser.add_argument('-b', '--buffersize', type=float, default=1.0,
                    help='buffer size (in MB)')
parser.add_argument('--encoding', type=str, default=None,
                    help='specification (e.g., "utf-8")')
parser.add_argument('-l', '--level', type=int, default=6,
                    help='compression level to use')

action_group = parser.add_mutually_exclusive_group()
action_group.add_argument('-z', '--compress', action='store_true',
                          help='compress data')
action_group.add_argument('-d', '--decompress', action='store_true',
                          help='decompress data')

SCHEMES = 'gzip', 'bzip', 'lzma'
spec_group = parser.add_mutually_exclusive_group()
spec_group.add_argument('--gzip', action='store_true',
                        help='use gzip/zlib compression algorithm')
spec_group.add_argument('--bzip', action='store_true',
                        help='use bzip2 compression algorithm')
spec_group.add_argument('--lzma', action='store_true',
                        help='use lzma compression algorithm')


def main() -> int:
    """Entry point for 'compress'."""

    try:
        argv = parser.parse_args()
        buffersize = int(argv.buffersize * 1024**2)

        action = compress if argv.decompress is False else decompress
        schemes = {getattr(argv, scheme): scheme for scheme in SCHEMES}
        if True not in schemes:
            kind = 'gzip'
        else:
            kind = schemes[True]

        options = {'kind': kind, 'encoding': argv.encoding}
        if argv.compress:
            options['level'] = argv.level

        writer = sys.stdout if argv.encoding is not None else sys.stdout.buffer
        with BinaryStream(*argv.sources) as stream:
            for buff in action(stream.iterbuffers(buffersize), **options):
                writer.write(buff)

    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.buffer.flush()

    return 0
