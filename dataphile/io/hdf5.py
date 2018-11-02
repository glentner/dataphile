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

"""Hierarchical Data Format (HDF5)
   dataphile.io.hdf5

   Dataphile, 0.1.4
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

# standard libraries
import os as _os
import re as _re
from typing import Dict as _Dict

# external libraries
import numpy as _np
import pandas as _pd
from h5py import File, Dataset, Group


# some dtypes cannot be immediately read/written from HDF5 files. These types can be dummy encoded
# with an alternative of the same bit-depth and then annotated with the real dtype.
__special_dtypes__ = {'datetime64[ns]': 'uint64',
                      '<M8[ns]': 'uint64',  # also datetime
                      '<U\d+': 'uint8'}


def _abspath(group: str, dataset: str) -> str:
    """Cross-platform join on 'group' and named dataset 'basename'."""
    return '/'.join([group.strip('/'), _os.path.basename(dataset)])


def _get(dataset: str, open_file: File) -> _np.ndarray:
    """Read values from HDF5 file, check for `dtype` attribute."""
    if 'dtype' not in open_file[dataset].attrs:
        return open_file[dataset].value
    else:
        return open_file[dataset].value.view(open_file[dataset].attrs['dtype'])


def read(filename: str, group: str='/') -> _Dict[str, _np.ndarray]:
    """Load all datasets below 'group' within HDF5 file.

       Parameters
       ----------

       Returns
       -------
       data: Dict[str, np.ndarray]
           All datasets found under 'group', indexed by the datasets' basenames.
    """
    data = dict()
    with File(filename) as infile:
        for name in infile[group].keys():
            dataset = _abspath(group, name)
            if isinstance(infile[dataset], Dataset):
                data[name] = _get(dataset, infile)

    return data


def read_table(filename: str, group: str = '/') -> _pd.DataFrame:
    """Read all datasets in HDF5 file immediately below 'group'.

       Parameters
       ----------
       filename: str
           Valid file path to HDF5 file.

       group: str (default='/')
           Group or subgroup within file containing datasets to load.

       Returns
       -------
       data: `pandas.DataFrame`
    """
    return _pd.DataFrame(read(filename, group))


def _put(array: _np.ndarray, dest: str, open_file: File) -> None:
    """Insert array into HDF5 file."""
    if dest in open_file:
        del open_file[dest]  # we have to clear this or we'll get an error
    typename = str(array.dtype)
    for pattern, replacement in __special_dtypes__.items():
        if _re.match(pattern, typename) or typename == pattern:
            open_file[dest] = _np.array(array, dtype=typename).view(replacement)
            open_file[dest].attrs['dtype'] = typename
            return
    if typename == 'object':
        # pandas replaces (e.g.) '<U12' with 'object'
        # we can try to coerce this back into '<U\d+' notation
        alt_typename = '<U{}'.format(max(map(lambda s: len(s), array)))
        open_file[dest] = _np.array(array, dtype=alt_typename).view('uint8')  # like chars
        open_file[dest].attrs['dtype'] = alt_typename
    else:
        # all numerical types
        open_file[dest] = array


def write(filename: str, group: str='/', **datasets: _np.ndarray) -> None:
    """Write out named 'datasets' to HDF5 file under specified 'group'.

       Parameters
       ----------
       filename: str
           Valid file path for HDF5 file.

       group: str (default='/')
           Group or subgroup to output datasets to within the file.

        **datasets: `numpy.ndarray`
            n-dim array data to write under 'group'.

        Returns
        -------
        None
    """
    with File(filename) as outfile:
        if group not in outfile:
            outfile.create_group(group)
        else:
            current_datasets = set(name for name in outfile[group].keys()
                                   if isinstance(outfile[_abspath(group, name)], Dataset))
            if current_datasets - set(datasets.keys()):
                raise UserWarning('"{group}" has existing datasets not included here. ({names})'
                                  .format(group=group, names=current_datasets - set(datasets.keys())))
        for name, array in datasets.items():
            _put(array, _abspath(group, name), outfile)


def write_table(df: _pd.DataFrame, filename: str, group: str='/') -> None:
    """Write each `pandas.Series` within 'df' to dataset in HDF5 file under specified 'group'.

       Parameters
       ----------
       df: `pandas.DataFrame`
           DataFrame to save.

       filename: str
           Valid file path for HDF5 file.

       group: str (default='/')
           Group or subgroup to output datasets to within the file.

        Returns
        -------
        None
    """
    datasets = {name: df[name] for name in df.columns}
    if df.index.name is not None:
        datasets[df.index.name] = df.index  # non-trivial indices are saved
    write(filename, group, **datasets)
