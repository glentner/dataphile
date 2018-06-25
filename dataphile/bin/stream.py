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

"""Stream data from files (similar to standard Unix command 'cat').
   dataphile.bin.stream

   DataPhile, 0.1.3
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

# standard libs
import os
import sys
import argparse
import platform

if platform.system() == 'Windows':
    # FIXME: how do we ignore broken pipes on windows?
    pass
else:
    from signal import signal, SIGPIPE, SIG_DFL  # ignore broken pipes
    signal(SIGPIPE, SIG_DFL)

# external libs
from tqdm import tqdm as monitor

# internal libs
from ..io.stream import Stream


parser = argparse.ArgumentParser(description=__doc__.split('\n')[0].strip())

# positional arguments
parser.add_argument('source', help='paths to data files', metavar='FILE', nargs='*')

# options and flags
parser.add_argument('-b', '--buffersize', help='buffer size (in MB)', type=float, default=0.256)
parser.add_argument('-m', '--monitor', help='display progress bar', action='store_true',
                    dest='use_progress_bar')
parser.add_argument('-l', '--live', help='maintain connection and wait for new data',
                    action='store_true', dest='live_connection')
parser.add_argument('-w', '--watch', help='accept new file locations in realtime',
                    action='store_true', dest='watch_for_files')


def main() -> int:
    """Entry point for 'stream' command."""

    try:
        opt = parser.parse_args()
        buffer_size = int(opt.buffersize * 1024**2)
        read = 'read_live' if opt.live_connection else 'read'
        if not opt.source and not opt.watch_for_files:
            # accept input sources from pipe directly
            opt.source = [path.strip() for path in sys.stdin.readlines()]
        if opt.use_progress_bar is True:
            total_bytes = None if not opt.source else sum(os.path.getsize(f) for f in opt.source)
            with Stream(*opt.source, live=opt.live_connection, watch=opt.watch_for_files) as source:
                with monitor(total=total_bytes, unit='B', unit_scale=True) as progress:
                    for data in getattr(source, read)(buffer_size):
                        progress.update(len(data))
                        sys.stdout.buffer.write(data)
        else:
            with Stream(*opt.source, live=opt.live_connection, watch=opt.watch_for_files) as source:
                for data in getattr(source, read)(buffer_size):
                    sys.stdout.buffer.write(data)

    except KeyboardInterrupt:
        pass

    return 0
