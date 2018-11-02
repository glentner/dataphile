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

"""Base classes for dataset objects."""



from typing import List, Tuple, Union, Callable
from numbers import Number

import numpy as np


class Dataset:
    """Generic base class for all datasets."""


class SyntheticDataset(Dataset):
    """A synthetic dataset is generated using random number generators and statistical distributions."""

    def __init__(self,
                 distribution: Callable,
                 parameters: List[Number],
                 domain: Tuple[Number, Number],
                 samples: int,
                 linspace: bool=False,
                 ordered: bool=False,
                 noise: float=0.05,
                 seed: Number=None):
        """Define the distribution."""

        # descriptions and type checking are done via 'property' definitions
        self.distribution = distribution
        self.parameters = parameters
        self.domain = domain
        self.samples = samples
        self.linspace = linspace
        self.ordered = ordered
        self.noise = noise
        self.seed = seed


    def generate(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate new synthetic data."""

        if self.linspace is True:
            xdata = np.linspace(*self.domain, self.samples)
        else:
            xdata = np.random.uniform(*self.domain, self.samples)
            if self.ordered is True:
                xdata.sort()

        ydata = self.distribution(xdata, *self.parameters)
        ydata += np.random.normal(0., self.noise * (ydata.max() - ydata.min()), self.samples)

        return xdata, ydata


    @property
    def distribution(self) -> Callable:
        """Access the statistical distrubution function for the dataset."""
        return self.__distribution

    @distribution.setter
    def distribution(self, func: Callable) -> None:
        """Set the statistical distribution function for the dataset."""
        if hasattr(func, '__call__'):
            self.__distribution = func
        else:
            raise TypeError('SyntheticDataset.distribution must be a callable function.')

    @property
    def parameters(self) -> List[Number]:
        """Parameters used to evaluate the distribution."""
        return self.__parameters

    @parameters.setter
    def parameters(self, value: List[Number]) -> None:
        """Set the parameters used to evaluate the distribution."""
        if hasattr(value, '__iter__') and all(isinstance(v, Number) for v in value):
            self.__parameters = list(value)
        else:
            raise ValueError('SyntheticDataset.parameters must be a list of numeric values.')

    @property
    def domain(self) -> Tuple[float, float]:
        """Access the domain limits (used to generate the dataset)."""
        return self.__domain

    @domain.setter
    def domain(self, value: Tuple[float, float]) -> None:
        """Set the domain limits (used to generate the dataset)."""
        if hasattr(value, '__iter__') and len(value) == 2 and all(isinstance(v, Number) for v in value):
            self.__domain = tuple(value)
        else:
            raise ValueError('SyntheticDataset.domain must be a length 2 tuple of floats.')

    @property
    def samples(self) -> int:
        """The number of samples taken from the distribution."""
        return self.__samples

    @samples.setter
    def samples(self, value: int) -> None:
        """Set the number of samples to take from the distribution."""
        if isinstance(value, int):
            self.__samples = value
        else:
            raise ValueError('SyntheticDataset.samples must be an integer value.')

    @property
    def linspace(self) -> bool:
        """Whether to create a uniform line space or randomly distributed over the domain."""
        return self.__linspace

    @linspace.setter
    def linspace(self, value: bool) -> None:
        """Set the linspace."""
        if isinstance(value, bool):
            self.__linspace = value
        else:
            raise ValueError('SyntheticDataset.linspace must be True or False.')

    @property
    def noise(self) -> float:
        """Signal to noise (normally distributed) for datasets."""
        return self.__noise

    @noise.setter
    def noise(self, value: Number) -> None:
        """Set the signal to noise value."""
        if isinstance(value, Number) and 0 <= value and value <= 1:
            self.__noise = float(value)
        else:
            raise ValueError('SyntheticDataset.noise must be a number between 0 and 1.')

    @property
    def seed(self) -> Number:
        """A numerical value to use to seed the random number generator (for reproducibility)."""
        return self.__seed

    @seed.setter
    def seed(self, value: Number) -> None:
        """Set the seed value for the random number generator."""
        if isinstance(value, Number):
            self.__seed = value
            np.random.seed(value)
        elif value is None:
            self.__seed = None
        else:
            raise ValueError('SyntheticDataset.seed must be a number.')
