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

"""Statistical functions (e.g., polynomials, gaussians, etc.)"""

from numbers import Number
from typing import Union

import numpy as np
from astropy import units as u
from astropy.units import Quantity


def polynomial1D(x: np.ndarray, *p: Number) -> np.ndarray:
    """A one dimensional polynomial function.

       The order of the polynomial is dynamic and dependent upon the number
       of input arguments, 'p'.
    """
    return sum(p_i * x**i for i, p_i in enumerate(p))


def linear1D(x: np.ndarray, intercept: Number, slope: Number) -> np.ndarray:
    """A one dimensional line."""
    return intercept + slope * x


def uniform(x: np.ndarray, scale: Number) -> np.ndarray:
    """Uniform distribution (returns 'scale' with the shape of 'x')."""
    return np.ones_like(x) * scale


def gaussian1D(x: np.ndarray, amplitude: Number, center: Number, stdev: Number) -> np.ndarray:
    """A one dimensional gaussian distribution.
       = amplitude * exp(-0.5 (x - center)**2 / stdev**2)
    """
    return amplitude * np.exp(-0.5 * (x - center)**2 / stdev**2)


def gaussianND(X: np.ndarray,
               amplitude: Number,
               center: Union[Number, np.ndarray],
               stdev: Union[Number, np.ndarray]) -> np.ndarray:
    """N-dimensional guassian function.

       X: `numpy.ndarray`
           Shape should be (N, n) where 'n' is the dimensionality (e.g., 1 for 1D, 2 for 2D)
           and N is the number of points in the dataset.

       center, stdev: Number or `numpy.ndarray`
           If these are scalars they act as though the value is the same in each dimension.
           These can alternatively take distinct values for each dimension and should be a
           `numpy.ndarray` of length equal to the second dimension, n, of the data 'X'.
    """
    return amplitude * np.exp(-0.5 * ((X - center)**2 / stdev**2).sum(axis=1))


def blackbody(x: np.ndarray, T: Quantity) -> Quantity:
    """Planck's law of black-body radiation

       The spectral radiance (the power per unit solid angle and per unit of area normal to the propagation)
       density of frequency ν radiation per unit frequency at thermal equilibrium at temperature T.

       x: `astropy.units.Quantity`
           Array of wavelength values (should have units of length, e.g., `astropy.units.nanometer`).

       T: `astropy.units.Quantity`
           Temperature of the blackbody (e.g., 5000 * `astropy.units.Kelvin`).
    """

    # planck's, speed of light, and Boltzmann constants
    from astropy.constants import h, c, k_B

    A = 2 * h * c**2 / x**5
    B = np.exp((h * c / (x * k_B * T)).decompose()) - 1
    return (A / B).to('kW m^-2 nm-1') / u.sr


def normalized_voigt1D(x: np.ndarray, x0: Number, sigma: Number, gamma: Number) -> np.ndarray:
    """A Voigt distribution is the convolution of a Gaussian and Lorentzian."""
    from scipy.special import wofz
    return wofz(((x-x0) + 1j*gamma) / (sigma * np.sqrt(np.pi))).real / (sigma * np.sqrt(2 * np.pi))


def voigt1D(x: np.ndarray, *p: Number) -> np.ndarray:
    """A Voigt distribution is the convolution of a Gaussian and Lorentzian.
       See `normalized_voigt1D` for parameter descriptions.
    """
    return p[0] * normalized_voigt1D(x, *p[1:]) / normalized_voigt1D(0, 0, *p[2:])


def sinusoid1D(x: np.ndarray, A: float=1, freq: float=1, phase: float=0) -> np.ndarray:
    """Sinusoidal wave. y = A * sin(freq*x - phase)

       x: `numpy.ndarray`
       A: float (default=1)
       freq: float (default=1)
       phase: float (default=0)
    """
    return A * np.sin(freq * x - phase)
