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

"""Stream data from files (similar to standard Unix command 'cat')."""

# standard libs
import os
import sys
import argparse
import platform

# external libs
from tqdm import tqdm

# internal libs
from ..io.stream import BinaryStream, LiveBinaryStream


if platform.system() == 'Windows':
    # FIXME: how do we ignore broken pipes on windows?
    pass
else:
    from signal import signal, SIGPIPE, SIG_DFL  # ignore broken pipes
    signal(SIGPIPE, SIG_DFL)


parser = argparse.ArgumentParser(description=__doc__.split('\n')[0].strip())
parser.add_argument('sources', metavar='FILE', nargs='+',
                    help='paths to data files')
parser.add_argument('-b', '--buffersize', type=float, default=1.0,
                    help='buffer size (in MB)')
parser.add_argument('-m', '--monitor', dest='use_progress_bar', action='store_true',
                    help='display progress bar')
live_group = parser.add_mutually_exclusive_group()
live_group.add_argument('-l', '--live', action='store_true',
                        help='maintain connection and wait for new data')
live_group.add_argument('-L', '--latency', type=float, default=0.1,
                        help='maintain connection and wait for new data')


def main() -> int:
    """Entry point for 'stream' command."""

    monitor = None

    try:
        argv = parser.parse_args()
        Stream = LiveBinaryStream if argv.live is True else BinaryStream
        buffsize = int(argv.buffersize * 1024**2)

        options = dict()
        if argv.live is True:
            options.update({'latency': argv.latency})

        if argv.use_progress_bar is True:
            monitor = tqdm(total=sum(map(os.path.getsize, argv.sources)),
                           unit='B', unit_scale=True, unit_divisor=1024)

        with Stream(*argv.sources, **options) as stream:
            for buff in stream.iterbuffers(buffsize):
                sys.stdout.buffer.write(buff)
                if monitor is not None:
                    monitor.update(len(buff))

    except KeyboardInterrupt:
        pass

    finally:
        if monitor is not None:
            monitor.close()

    return 0
