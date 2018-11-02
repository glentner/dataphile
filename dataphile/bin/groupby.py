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

"""Group data by unique fields.
   dataphile.bin.groupby

   Dataphile, 0.1.4
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


# standard libs
import os
import sys
import itertools
from io import BytesIO
from typing import Any, Callable
from argparse import ArgumentParser

# external libs
from pandas import read_csv
import numpy as np

# internal libs
from ..io.stream import Stream
from ..io.common import compression_formats, select_compression


parser = ArgumentParser(description=__doc__.split('\n')[0].strip())

# positional arguments
parser.add_argument('source', help='paths to files', metavar='FILE', nargs='*')

# options and flags
parser.add_argument('-s', '--buffersize', help='buffer size (in MB)', type=float, default=0.256)

parser.add_argument('-f', '--field', help='label or column number to use as ID for groupby operation', default='0')
parser.add_argument('-H', '--headers', help='number of headers (lines) in input files',
                    dest='num_headers', type=int, default=0)
parser.add_argument('-d', '--delimiter', help='char used to deliminate fields in the data', type=str, default=',')
parser.add_argument('--slash', help='replacement char used for slashes ("/") in filenames', type=str, default='-')
parser.add_argument('--colon', help='replacement char used for colons (":") in filenames', type=str, default='-')

# output path specification
path_group = parser.add_mutually_exclusive_group()
path_group.add_argument('-T', '--output-directory', help='path to output directory for files',
                        dest='output_directory', type=str, default=None)  # default='.'
path_group.add_argument('-o', '--output-pattern', help='pattern for output files',
                        dest='output_pattern', type=str, default=None)  # default='%.csv'
path_group.add_argument('--to', help='specify output file format',
                        dest='output_filetype', type=str, default=None)  # default='csv'
# available output formats: csv(.gz|bz(2)?|(xz|lzma))? -'d '

# optional operations
agg_group = parser.add_mutually_exclusive_group()
agg_group.add_argument('--sum', help='apply summation to all numerical fields',
                       action='store_const', const=np.sum)
agg_group.add_argument('--mean', help='apply arithmetic mean to all fields',
                       action='store_const', const=np.mean)
agg_group.add_argument('--stdev', help='solve standard deviation (sample) to fields',
                       action='store_const', const=np.std)


def _solve_output_path(namespace: Any, **repl_chars) -> Callable[..., str]:
    """Build output file path format."""
    # solve for output file path/patterns
    if namespace.output_directory is not None:
        return os.path.join(namespace.output_directory, '{key}.csv').format
    elif namespace.output_pattern is not None:
        return os.path.join(os.getcwd(), namespace.output_pattern.replace('%', '{key}')).format
    elif namespace.output_filetype is not None:
        return os.path.join(os.getcwd(), '{key}.' + namespace.output_filetype).format
    else:
        return os.path.join(os.getcwd(), '{key}.csv').format



def main() -> int:
    """Entry point for 'groupby' command."""

    opt = parser.parse_args()
    path_fmt = _solve_output_path(opt)  # e.g., path_fmt(key=...) gives ./[key].csv
    compression = select_compression(path_fmt(key='dummy_id'))
    buffer_size = int(opt.buffersize * 1024**2)

    try:
        with Stream(*opt.source) as source:
            # extract headers if present and define column names
            if opt.num_headers != 0:
                # consume N lines off the first file or stream; assume N reps location
                header = list(itertools.islice(source.files[0], opt.num_headers))[-1].decode().strip()
                names = [field.strip() for field in header.split(opt.delimiter)]
            else:
                header, names = None, None
            # define field identifiers (enumerated if not explicitly labeled)
            try:
                key = int(opt.field)  # if this works then it was a number
                if header is not None:
                    key = names[key]  # can specify numeral even with named columns
            except ValueError:
                if header is None or opt.field not in names:
                    raise ValueError('"{}" does not name an available field'.format(key))
                else:
                    key = opt.field

            # read off in whole line increments
            for data in source.readlines(buffer_size):
                # create data frame and append to files grouped by specified field
                frame = read_csv(BytesIO(data), header=None, names=names, sep=opt.delimiter)
                for group_name, group_data in frame.groupby(key):
                    if len(group_data) < 1: continue
                    filename = path_fmt(key=group_name.replace('/', opt.slash).replace(':', opt.colon))
                    output = group_data.drop([key], axis=1)  # no need for saving the group_name
                    if not os.path.exists(filename) and header is not None:
                        output.to_csv(filename, index=False, encoding='utf-8', mode='a',
                                      compression=compression, header=True)
                    else:
                        output.to_csv(filename, index=False, encoding='utf-8', mode='a',
                                      compression=compression, header=False) # may already have header


    except (BrokenPipeError, KeyboardInterrupt):
        pass

    return 0  # sys.exit(0)
