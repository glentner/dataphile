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

"""Display progress bar (using stderr) for piping data.
   dataphile.bin.monitor

   Dataphile, 0.1.5
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


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
