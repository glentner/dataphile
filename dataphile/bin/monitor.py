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

"""Display progress bar (using stderr) for piping data."""


# standard libs
import sys
import argparse

# external libs
from tqdm import tqdm

parser = argparse.ArgumentParser(prog=__doc__.split('\n')[0].split('.')[-1].strip(),  # gunzip
                                 description='\n'.join(__doc__.split('\n')[1:]))
parser.add_argument('-t', '--total-bytes', help='use total bytes to display ETC', type=int, default=None, dest='total_bytes')


def main() -> int:
    """Entry point for 'monitor' script."""
    opt = parser.parse_args()
    with tqdm(total=opt.total_bytes, unit='B', unit_scale=True) as monitor:
        for data in sys.stdin.buffer:
            monitor.update(len(data))
            sys.stdout.buffer.write(data)
    return 0
