# toolkit.statistics.distributions
"""Statistical functions (e.g., polynomials, gaussians, etc.)

   Copyright (c) Geoffrey Lentner 2017. All Rights Reserved.
   MIT, see LICENSE file.
"""

from numbers import Number

import numpy as np
from astropy import units as u


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


def blackbody(x: np.ndarray, T: Quantity)
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

    A = 2 * h * c**2 / wavelength**5
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
    return p[0] * normalized_voigt(x, *p[1:]) / normalized_voigt(0, 0, *p[2:])
