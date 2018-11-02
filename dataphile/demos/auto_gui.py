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

"""Demonstration of `dataphile.statistics.regression.modeling.AutoGUI`."""


from typing import List, Dict, Tuple
import itertools

import numpy as np
import pandas as pd
from astropy import units as u

import matplotlib as mpl
from matplotlib import pyplot as plot
from matplotlib import widgets, patches


from ..graphics.widgets import Slider
from ..statistics.regression.modeling import Parameter, Model, CompositeModel, AutoGUI
from ..statistics.distributions import linear1D, polynomial1D, sinusoid1D, gaussian1D
from ..datasets import SyntheticDataset


class Demo:
    """Base class for Demo classes."""

    def __init__(self, *args, **kwargs):
        """Generate SyntheticDataset(*args, **kwargs)."""
        self.dataset = SyntheticDataset(*args, **kwargs)
        self.xdata, self.ydata = self.dataset.generate()


class Linear(Demo):
    """Linear Regression Demonstration of AutoGUI."""

    def __init__(self, parameters: Tuple[float,float]=(1.5, 1.0),
                 bounds: Tuple[float,float]=(-1.0, 2.0), samples: int=250, linspace: bool=False,
                 ordered: bool=False, noise: float=0.05, seed: float=None):
        """Initialize demonstration and attributions."""

        # create synthetic dataset
        super().__init__(linear1D, parameters, bounds, samples, linspace=linspace,
                         ordered=ordered, noise=noise, seed=seed)

        self.create_figure()
        self.create_model()
        self.create_gui()

    def create_figure(self) -> None:
        """Initialize the figure."""

        self.figure = plot.figure('Simple Linear Regression', figsize=(10, 6))
        self.data_scatter = plot.scatter(self.xdata, self.ydata, label='data')
        plot.xlabel('x', labelpad=15)
        plot.ylabel('y', labelpad=15)
        plot.legend(loc='upper left')
        plot.tight_layout()

    def create_model(self) -> None:
        """Create the Model."""

        self.model = Model(linear1D,
                           Parameter(value=1.5, bounds=(-1, 2), label='intercept'),
                           Parameter(value=1.0, bounds=(-3, 3), label='slope'),
                           label='linear')

        self.xsample = np.linspace(-1, 2, 150)
        self.model_curve, = plot.plot(self.xsample, self.model(self.xsample), 'k--',
                                      label=self.model.label + ' model', lw=2, zorder=20)
        plot.legend(loc='upper left')

    def create_gui(self) -> None:
        """Create AutoGUI for model."""
        color, = self.data_scatter.get_facecolors()
        self.gui = AutoGUI(self.model, [self.model_curve], bbox=[0.20, 0.20, 0.75, 0.12],
                           slider_options={'color': list(color)},
                           data=(self.xdata, self.ydata))


class Sinusoidal(Demo):
    """Sinusoid over Uniform Background Demonstration with AutoGUI."""

    def __init__(self):
        """Initialize dataset and build AutoGUI."""

        # construct model
        self.model = CompositeModel(
            Model(uniform,
                  Parameter(value=1.0, bounds=(0, 2), label='scale'),
                  label='background'),
            Model(sinusoid1D,
                  Parameter(value=1.0, bounds=(0.5, 2.0), label='amplitude'),
                  Parameter(value=1.5, bounds=(1.0, 2.0), label='frequency'),
                  Parameter(value=2.0, bounds=(1.0, 3.0), label='phase'),
                  label='sinusoid'),
            label='sinusoid_over_uniform_background')

        # create synthetic dataset
        super().__init__(self.model.function, self.model.values,
                         domain=(-2, 6), samples=80, ordered=True, noise=0.15,
                         seed=314159)

        # create figure
        self.figure = plot.figure('Sinusoid over Uniform Background', figsize=(9, 6))
        self.ax = self.figure.add_axes([0.10, 0.32, 0.88, 0.66])
        self.data_scatter = self.ax.scatter(self.xdata, self.ydata, label='data',
                                            marker='o', edgecolor='steelblue',
                                            facecolor='white', lw=1, s=100)

        self.ax.set_ylim(-1, 3)
        self.ax.set_xlabel(r'$x$ (sample locations)', labelpad=15)
        self.ax.set_ylabel(r'$y = A + B \sin\left(\phi x - \rho \right)$', labelpad=15)

        # create AutoGUI
        self.xsample = np.linspace(-2, 6, 2000)
        self.model_curve, = plot.plot(self.xsample, self.model(self.xsample), 'k--',
                                      label='model', lw=2, zorder=20)

        plot.legend(loc='upper right', fancybox=True, facecolor='white')
        self.gui = AutoGUI(self.model, [self.model_curve], bbox=[0.20, 0.06, 0.75, 0.12],
                           slider_options={'color': 'steelblue'},
                           data=(self.xdata, self.ydata))


class GaussianPeaks(Demo):
    """Multiple Gaussian Features over a Polynomial Background."""

    def __init__(self):
        """Create synthetic dataset, plots, and AutoGUI."""
        # polynomial background (bias distribution across detector)
        super().__init__(polynomial1D, [100, -0.01, -1e-5], (0, 2400), linspace=True,
                         noise=0, samples=2400)

        # randomly generate gaussian peaks
        np.random.seed(33)
        N     = 24
        A_s   = np.random.uniform(50, 150, N)
        x0_s  = np.random.uniform(100, 2300, N)
        sig_s = np.random.uniform(10, 20, N)
        peaks = [SyntheticDataset(gaussian1D, [A, x0, sig], (0, 2400), linspace=True,
                                  noise=0.015, samples=2400).generate()[1]
                 for A, x0, sig in zip(A_s, x0_s, sig_s)]

        # superimpose gaussian features over background
        bias = self.ydata
        self.ydata += sum(peaks)

        figure = plot.figure('Guassian Peaks Demonstration with AutoGUI', figsize=(9, 7))
        self.figure = figure

        # select region of dataset for fitting
        xdata_i = self.xdata[self.xdata < 400]
        ydata_i = self.ydata[self.xdata < 400]

        # create main plot
        ax_2 = figure.add_axes([0.15, 0.30, 0.84, 0.56])
        fit_graph, = ax_2.step(xdata_i, ydata_i, color='black', lw=1, label='data')

        # labels
        ax_2.set_ylabel('Counts', labelpad=15)
        ax_2.set_xlabel('Channel', labelpad=15)

        # whole dataset graph
        ax_1 = figure.add_axes([0.05, 0.73, 0.45, 0.24])
        graph, = ax_1.step(self.xdata, self.ydata, color='black', lw=1)
        xloc, yloc = x0_s, [(bias + peak).max() + 50 for peak in peaks]
        markers = ax_1.scatter(xloc, yloc, marker='v', color='steelblue')
        rectangle = patches.Rectangle((0, 50), 400, 250, color='gray', alpha=0.50)
        ax_1.add_patch(rectangle)

        # model
        model = CompositeModel(
            Model(polynomial1D,
                  Parameter(value=100, bounds=(0, 200),      label='scale'),
                  Parameter(value=0,   bounds=(-0.1, 0.1),   label='slope'),
                  Parameter(value=0,   bounds=(5e-5, -5e-5), label='gradient'),
                  label='background'),
            Model(gaussian1D,
                  Parameter(value=100, bounds=(10, 300), label='amplitude'),
                  Parameter(value=170, bounds=(100, 300), label='center'),
                  Parameter(value=10, bounds=(5, 20), label='width'),
                  label='feature_1'),
            Model(gaussian1D,
                  Parameter(value=100, bounds=(10, 300), label='amplitude'),
                  Parameter(value=220, bounds=(100, 300), label='center'),
                  Parameter(value=10, bounds=(5, 20), label='width'),
                  label='feature_2'),
            Model(gaussian1D,
                  Parameter(value=100, bounds=(10, 300), label='amplitude'),
                  Parameter(value=280, bounds=(100, 300), label='center'),
                  Parameter(value=10, bounds=(5, 20), label='width'),
                  label='feature_3'),
            label='gaussian_peaks')

        xsample = np.linspace(0, 400, 1500)
        model_curve, = ax_2.plot(xsample, model(xsample), color='steelblue', label='model')
        ax_2.legend()

        gui = AutoGUI(model, [model_curve], bbox=[0.20, 0.07, 0.75, 0.12],
                      slider_options={'color': 'steelblue'}, data=(xdata_i, ydata_i))

        # assign members
        self.model = model
        self.gui = gui
