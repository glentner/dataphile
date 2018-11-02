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

"""Module contains tools for doing kernel regression/smoothing."""

from typing import Tuple as _Tuple, Iterable as _Iterable, Union as _Union

import numpy as _np


class Kernel:
    """Callable which returns numerical weights given distance inputs.
       This is an abstract base class. The derived Kernels should pass some kind
       of weighting or bandwidth parameters to the init method and accept distance
       matrices from __call__.
    """
    def __call__(self, X: _np.ndarray) -> _np.ndarray:
        raise NotImplementedError('Must be implemented in derived Kernel.')


class GaussianKernel(Kernel):
    """A Gaussian kernel function. (supports N-dimensions)"""

    def __init__(self, *bw):
        """Initialize with 'bw' (bandwidths). These will be the sigma values for
           the gaussian function.
        """
        if not bw:
            raise ValueError('GaussianKernel must be at least 1D.')
        else:
            self.__bw = _np.array(bw)

    def __call__(self, X: _np.ndarray) -> _np.ndarray:
        """Evaluate kernel given distances, 'X'.

           X: `numpy.ndarray`
               Shape should be (N, n) where 'n' is the dimensionality (e.g., 1 for 1D, 2 for 2D)
               and N is the number of points in the dataset.
        """
        return _np.exp(-0.5 * (X**2 / self.__bw**2).sum(axis=1))

    @property
    def bandwidth(self) -> _Union[float,_Tuple[float]]:
        """Access to protected bandwidth parameter(s)."""
        if len(self.__bw) == 1:
            return self.__bw[0]
        else:
            return tuple(self.__bw)

    @bandwidth.setter
    def bandwidth(self, value: _Union[float,_Iterable[float]]) -> None:
        """Set bandwidth parameters safely."""
        if not hasattr(value, '__iter__'):
            if len(self.bandwidth) == 1:  # float
                self.__bw = _np.array(value)
            else:
                raise ValueError('Attempting to set bandwidth with single value, Kernel has shape {0}'
                                 .format(self.__bw.shape))
        else:
            if len(value) == len(self.__bw):
                self.__bw = _np.array(value)
            else:
                raise ValueError('Kernel has shape {0} - attempted to set bandwidths with shape {1}'
                                 .format(self.__bw.shape, _np.array(value).shape))

    def __str__(self):
        return '<GaussianKernel {1}>'.format(len(self.__bw), self.__bw)

    def __repr__(self):
        return str(self)


class KernelRegressor:
    """Generalized implementation of n-dimensional kernel regressor/smoother"""

    def __init__(self, kernel: Kernel):
        """Initialize with 'kernel' function.

           kernel: `Kernel`
               Instance of Kernel type initialized with necessary parameters.
               Example: GaussianKernel(1.5, 30) for 2D gaussian regression.
        """
        self.__kernel = kernel

    def fit(self, X: _np.ndarray, x: _np.ndarray) -> _np.ndarray:
        """Fit (smooth) curve (surface, etc.) through data, 'X', at sample points, 'x'.

           X: `numpy.ndarray`
               Shape should be (N, n) where 'n' is the dimensionality (e.g., 1 for 1D, 2 for 2D)
               and N is the number of points in the dataset.

           x: `numpy.ndarray`
               The shape should be (M, n-1) where 'n' corresponds to the dimensionality of
               the original data, 'X', and 'M' is the number of sample points. In the 1D
               case, 'x' can be just the 1D array of sample points.
        """
        x = x if len(x.shape) > 1 else _np.atleast_2d(x).T
        y = _np.zeros(len(x))
        for i, _x in enumerate(x):
            W = self.kernel(X[:, :-1] - _x)
            y[i] = (W * X[:, -1]).sum() / W.sum()
        return y

    @property
    def kernel(self) -> Kernel:
        """Access only."""
        return self.__kernel

    def __str__(self):
        return '<KernelRegressor({0})>'.format(self.kernel)

    def __repr__(self):
        return str(self)
