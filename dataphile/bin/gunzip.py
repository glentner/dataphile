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

"""Decompress zlib compressed files (gzip compatible).
   dataphile.bin.gunzip

   Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

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
