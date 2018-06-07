# -*- coding: utf-8 -*-
# This file is part of the DataPhile Project.
# DataPhile - A suite of software for data acquisition and analysis in Python.
# Copyright (c) 2018 Geoffrey Lentner <glentner@gmail.com>
#
# DataPhile is free software; you can redistribute it  and/or modify it under the terms of the GNU
# General Public License (v3.0) as  published by the Free Software Foundation,  either version 3 of
# the License, or (at your option) any  later version. WARRANTY; without even the implied warranty
# of MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.  See the  GNU General  Public License
# (v3.0) for more details.
#
# You should have received a copy of the GNU General Public License (v3.0) along with this program.
# If not, see <http://www.gnu.org/licenses/>.

"""Demonstration of `dataphile.statistics.regression.modeling.AutoGUI`.
   dataphile.demos.auto_gui

   DataPhile, 0.0.2
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


from typing import List, Dict, Tuple
import itertools

import numpy as np
import pandas as pd

import matplotlib as mpl
from matplotlib import pyplot as plot
from matplotlib import widgets


from ..graphics.widgets import Slider
from ..statistics.regression.modeling import Parameter, Model, CompositeModel, AutoGUI
from ..statistics.distributions import linear1D, voigt1D
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
        plot.scatter(self.xdata, self.ydata, label='data')
        plot.xlabel('x', labelpad=15)
        plot.ylabel('y', labelpad=15)
        plot.legend()
        plot.tight_layout()

    def create_model(self) -> None:
        """Create the Model."""

        self.model = Model(linear1D,
                           Parameter(value=1.5, bounds=(-1, 2), label='intercept'),
                           Parameter(value=1.0, bounds=(-3, 3), label='slope'),
                           label='linear')

        self.xsample = np.linspace(-1, 2, 150)
        self.model_curve, = plot.plot(self.xsample, self.model(self.xsample), 'k--',
                                      label=self.model.label, lw=2, zorder=20)

    def create_gui(self) -> None:
        """Create AutoGUI for model."""
        self.gui = AutoGUI(self.model, [self.model_curve], bbox=[0.45, 0.15, 0.50, 0.20],
                           background='white', border=True)

# plot.legend();
#
#
# # In[47]:
#
#
# model = Model('linear', linear, Parameter('intercept', 0, (-1, 1)),
#                                 Parameter('slope', 1, (0, 2)))
#
#
# # In[48]:
#
#
# gui = AutoGUI(model, model_curve, bbox=[0.35, 0.12, 0.30, 0.15])
#
#
# # In[49]:
#
#
# model.fit(xdata, ydata)
# model_curve.set_ydata(model(xdata))
#
#
# # In[50]:
#
#
# model.parameters
#
#
# # In[51]:
#
#
# for parameter, slider in zip(model.parameters, gui.sliders):
#     slider.value = parameter.value
#
#
# # <br><br><br>
# #
# # ---
#
# # <br><br><br>
# #
# # ---
#
# # In[60]:
#
#
# from astropy import units as u
# from astropy.constants import h, c, k_B
#
#
# # In[61]:
#
#
# def plancks_law(wavelength, temperature):
#     """Planck's law of black-body radiation.
#
#        The spectral radiance (the power per unit solid angle and per unit of area normal to the propagation)
#        density of frequency ν radiation per unit frequency at thermal equilibrium at temperature T.
#     """
#
#     # planck's, speed of light, and Boltzmann constants
#     from astropy.constants import h, c, k_B
#
#     A = 2 * h * c**2 / wavelength**5
#     B = np.exp((h * c / (wavelength * k_B * temperature)).decompose()) - 1
#     return (A / B).to('kW m^-2 nm-1') / u.sr
#
#
# # In[62]:
#
#
# plot.figure('Black-body Radiation', figsize=(8, 5))
#
# xdata = np.linspace(0.01, 3, 1000) * u.micrometer
#
# for T in np.array([3000, 4000, 5000]) * u.Kelvin:
#     plot.plot(xdata, plancks_law(xdata, T), label=str(T))
#
# plot.xlabel(r'wavelength ($\lambda$)')
# plot.ylabel(r'$B_{\lambda}(T)$')
# plot.legend()
# plot.tight_layout()
#
#
# # Build a synthetic data set of black-body radiation at the Sun's surface temperature with injected noise and Voigt profiles subtracted from the *continuum*.
#
# # In[63]:
#
#
# wavelength_domain = np.linspace(300, 800, 500*100+1) * u.nanometer
#
#
# # In[64]:
#
#
# continuum = plancks_law(wavelength_domain, temperature=5000*u.Kelvin)
#
#
# # In[65]:
#
#
# noise = np.random.normal(0, 0.05, 500*100+1) * u.Unit('kW sr^-1 m^-2 nm^-1')
#
#
# # In[66]:
#
#
# def normalized_voigt(x, x0, sigma, gamma):
#     from scipy.special import wofz
#     return wofz(((x-x0) + 1j*gamma) / (sigma * np.sqrt(np.pi))).real / (sigma * np.sqrt(2 * np.pi))
#
#
# # In[67]:
#
#
# def voigt(x, *p):
#     return p[0] * normalized_voigt(x, *p[1:]) / normalized_voigt(0, 0, *p[2:])
#
#
# # In[68]:
#
#
# np.random.seed(42) # fixed for reproducibility
# n_profiles = 300
#
# A_all      = np.random.uniform(0.25, 4.0, n_profiles)
# x0_all     = np.random.uniform(300, 800, n_profiles)
# sigma_all  = np.ones(n_profiles) / 10.0
# gamma_all  = np.ones(n_profiles) / 50.0
#
# profiles = [voigt(wavelength_domain.value, A, x0, sigma, gamma) * u.Unit('kW sr^-1 m^-2 nm^-1')
#             for A, x0, sigma, gamma in zip(A_all, x0_all, sigma_all, gamma_all)]
#
#
# # In[69]:
#
#
# spectrum = continuum + noise - sum(profiles)
#
#
# # In[70]:
#
#
# figure = plot.figure('Spectral Energy Distribution', figsize=(10, 6))
# axis = figure.add_subplot(111)
#
# # plot.plot(wavelength_domain, continuum, label='continuum', zorder=20, lw=1, linestyle='--', color='red')
# data_curve, = plot.step(wavelength_domain, spectrum, label='data', zorder=10, lw=1)
#
# plot.xlabel(r'wavelength ($\lambda$)')
# plot.ylabel(r'Spectral Radiance ($kW sr^{-1} m^{-2} nm^{-1}$)')
#
# plot.ylim(bottom=0)
# plot.legend(loc='lower right')
# plot.tight_layout()
#
#
# # In[71]:
#
#
# class AutoGUIExample:
#     """Generate a graphical interface for a given Model/CompositeModel."""
#
#     def __init__(self, model:  Model,
#                        graph:  mpl.lines.Line2D,
#                        figure: mpl.figure.Figure=None, # defaults to graph.figure
#                        bbox:   List[float]=[0, 0, 1, 1]):
#         """Create the widget elements."""
#
#         self.__model = model
#         self.__graph = graph
#         self.__bbox = bbox
#
#         if figure is None:
#             self.__figure = graph.figure
#         else:
#             self.__figure = figure
#
#
#         # checks
#         assert isinstance(self.figure, mpl.figure.Figure)
#         assert isinstance(model, Model)
#         assert len(bbox) == 4
#         assert all(isinstance(val, (float, int)) for val in bbox)
#
#         # access modes
#         self.__models_by_label = {model.label: model for model in self.models}
#         self.__models_by_index = {i: model for i, model in enumerate(self.models)}
#         self.__index_by_models = {model.label: i for i, model in enumerate(self.models)}
#
#         # a simple model doesn't require a selection widget (radio buttons)
#         # the sliders will be created for the first (or only) model and if
#         # needed a radio button selector will toggle through the slider sets
#         self.sliders = list()
#         self.__create_radio()
#         self.__create_sliders(self.active_model.label)
#
#     def __create_radio(self) -> None:
#         """Create the radio widget."""
#
#         # consistent height of individual buttons requires dynamic height of widget
#         height = (1/4) / self.figure.get_size_inches()[1]  # 1/3 inch per button
#         if height * len(self.models) > self.height:
#             height = self.height / len(self.models) # squeeze
#
#         # create new axis for radio widget
#         axis = self.figure.add_axes([
#             self.__abs_pos(0.05, 0)[0], # x0
#             self.y0 + self.height - len(self.models)*height, # y0
#             0.20,
#             len(self.models) * height])
#
#         # formatting
#         axis.patch.set_facecolor('none')
#
#         # create widget
#         self.__radio = widgets.RadioButtons(axis, tuple(model.label for model in self.models),
#                                             activecolor='steelblue')
#         # update function
#         self.__radio.on_clicked(self.__radio_on_clicked)
#
#     def __create_sliders(self, label: str) -> None:
#         """Create all necessary sliders for each (if multiple) models."""
#
#         # currently selected model
#         model = self.__models_by_label[label]
#
#         # best height is about 1/3 inches
#         height = (1/3) / self.figure.get_size_inches()[1] # associated percent value
#         if len(model.parameters)*height > self.height:
#             height = self.height / len(model.parameters) # divide evenly
#
#         self.__remove_sliders() # remove old sliders
#         for count, parameter in enumerate(model.parameters):
#             slider = Slider(
#                 figure=self.figure,
#                 location=[
#                     self.__abs_pos(0.35, 0)[0], # x0=35% right of bbox
#                     self.y0 + self.height - height - height*count, # vertical position
#                     self.__abs_pos(0.40, 0)[0], # width of slider in absolute units
#                     height
#                 ],
#                 label=parameter.label,
#                 bounds=parameter.bounds,
#                 init_value=parameter.value
#             )
#             slider.on_changed(self.__slider_update_function)
#             self.sliders.append(slider)
#
#     def __remove_sliders(self) -> None:
#         """Remove sliders from view."""
#         for slider in self.sliders:
#             slider.remove()
#         self.sliders.clear()
#
#     def __radio_on_clicked(self, label: str) -> None:
#         """Action to take in the event that a button is selected on the radio widget."""
#         # recreate the sliders for the currently selected model
#         self.__create_sliders(label)
#         self.figure.canvas.draw_idle()
#
#     def __slider_update_function(self, value: float) -> None:
#         """Redraw graph based on current values."""
#
#         # update parameter values of currently selected component
#         for slider, parameter in zip(self.sliders, self.active_model.parameters):
#             parameter.value = slider.value
#
#         # update graph
#         self.ydata = self.model.solve(self.xdata)
#         self.figure.canvas.draw_idle()
#
#     def __abs_pos(self, x: float, y: float) -> List[float]:
#         """Return absolute x and/or y values (percent) given relative values."""
#         assert x >= 0 and x <= 1 and y >= 0 and y <= 1
#         return (self.x0 + x * self.width, self.y0 + y * self.height)
#
#     @property
#     def figure(self) -> mpl.figure.Figure:
#         """Access parent figure object."""
#         return self.__figure
#
#     @property
#     def model(self) -> Model:
#         """Access to associated Model."""
#         return self.__model
#
#     @property
#     def models(self) -> List[Model]:
#         """Return list of models (length one if not CompositeModel)."""
#         if isinstance(self.model, CompositeModel):
#             return list(self.model.models)
#         else:
#             return [self.model]
#
#     @property
#     def active_model(self) -> Model:
#         """Access which model is currently selected"""
#         if isinstance(self.model, CompositeModel):
#             return self.__models_by_label[self.radio.value_selected]
#         else:
#             return self.model
#
#     @active_model.setter
#     def active_model(self, label: str) -> None:
#         """Programmatically select a model."""
#         if isinstance(self.model, CompositeModel):
#             self.radio.set_active(self.__index_by_models[label])
#         else:
#             if label != self.model.label:
#                 raise ValueError('"{}" is the only model in use.'.format(self.model.label))
#
#     @property
#     def bbox(self) -> List[float]:
#         """Access to 'bbox' location (percent of canvas) for GUI."""
#         return self.__bbox
#
#     @property
#     def x0(self) -> float:
#         """Location of lower left 'x' value (percent of canvas) for GUI."""
#         return self.bbox[0]
#
#     @property
#     def y0(self) -> float:
#         """Location of lower left 'y' value (percent of canvas) for GUI."""
#         return self.bbox[1]
#
#     @property
#     def width(self) -> float:
#         """Width (percent of canvas) for GUI."""
#         return self.bbox[2]
#
#     @property
#     def height(self) -> float:
#         """Height (percent of canvas) for GUI."""
#         return self.bbox[3]
#
#     @property
#     def xdata(self) -> np.ndarray:
#         """Access to underlying x-data within 'graph'."""
#         return self.__graph.get_xdata()
#
#     @xdata.setter
#     def xdata(self, values: np.ndarray) -> None:
#         """Assign new values to 'xdata'."""
#         self.__graph.set_xdata(values)
#
#     @property
#     def ydata(self) -> np.ndarray:
#         """Access to underlying y-data within 'graph'."""
#         return self.__graph.get_ydata()
#
#     @ydata.setter
#     def ydata(self, values: np.ndarray) -> None:
#         """Assign new values to 'ydata'."""
#         self.__graph.set_ydata(values)
#
#     @property
#     def data(self) -> np.ndarray:
#         """Access to underlying data within 'graph'."""
#         return self.__graph.get_data()
#
#     @data.setter
#     def data(self, *values: np.ndarray) -> None:
#         """Assign new values to 'data'."""
#         self.__graph.set_data(*values)
#
#     @property
#     def radio(self) -> mpl.widgets.RadioButtons:
#         """Access to the radio buttons widget."""
#         return self.__radio
#
#
# # In[72]:
#
#
# figure = plot.figure('AutoGUI for CompositeModel', figsize=(10, 6))
# axis = figure.add_subplot(111)
#
# # plot.plot(wavelength_domain, continuum, label='continuum', zorder=20, lw=1, linestyle='--', color='red')
# data_curve, = plot.step(wavelength_domain, spectrum, label='data', zorder=10, lw=1)
#
# plot.xlabel(r'wavelength ($\lambda$)')
# plot.ylabel(r'Spectral Radiance ($kW sr^{-1} m^{-2} nm^{-1}$)')
#
# plot.ylim(bottom=0)
# plot.legend(loc='lower right')
# plot.tight_layout()
#
#
# # In[73]:
#
#
# # adjust the graph up to make room for a fitting GUI
# bbox = axis.get_position()
# axis.set_position([bbox.x0, bbox.y0 + 0.30, bbox.width, bbox.height - 0.30])
#
#
# # In[74]:
#
#
# # zoom on region of interest
# plot.xlim(355, 361)
# plot.ylim(2, 7);
#
#
# # In[75]:
#
#
# # select the data in the region of interest
# local = (wavelength_domain.value > axis.get_xlim()[0]) & (wavelength_domain.value < axis.get_xlim()[1])
# xdata = wavelength_domain[local].value
# ydata = spectrum[local].value
# data_curve.set_data(xdata, ydata)
#
#
# # In[76]:
#
#
# def linear(x, *p):
#     return p[0] + p[1] * x
#
#
# # In[77]:
#
#
# def voigt_(x, *p):
#     return -voigt(x, *p)
#
#
# # In[78]:
#
#
# model = CompositeModel(
#     Model('continuum', linear, Parameter('background',  6.5 , (  5,    7.  )),
#                                Parameter('slope',       0.0 , ( -0.02, 0.02))),
#     Model('feature_1', voigt_, Parameter('amplitude',   3.0 , (  0,    4.  )),
#                                Parameter('position',  358.0 , (357,  360.  )),
#                                Parameter('width',       0.1 , (  0,    0.50)),
#                                Parameter('gamma',       0.05, (  0,    0.20))),
#     Model('feature_2', voigt_, Parameter('amplitude',   3.0 , (  0,    4.  )),
#                                Parameter('position',  358.5 , (357,  360.  )),
#                                Parameter('width',       0.1 , (  0,    0.50)),
#                                Parameter('gamma',       0.05, (  0,    0.20))),
#     Model('feature_3', voigt_, Parameter('amplitude',   3.0 , (  0,    4.  )),
#                                Parameter('position',  359.0 , (357,  360.  )),
#                                Parameter('width',       0.1 , (  0,    0.50)),
#                                Parameter('gamma',       0.05, (  0,    0.20))),
#     Model('feature_4', voigt_, Parameter('amplitude',   3.0 , (  0,    4.  )),
#                                Parameter('position',  359.5 , (357,  360.  )),
#                                Parameter('width',       0.1 , (  0,    0.50)),
#                                Parameter('gamma',       0.05, (  0,    0.20))))
#
#
# # In[79]:
#
#
# model.graph, = axis.plot(xdata, model.solve(xdata), label='model', color='gold', lw=1.2);
#
#
# # In[80]:
#
#
# gui = AutoGUI(model, model.graph, bbox=[0.03, 0.03, 0.95, 0.25])
#
#
# # <br><br><br><br><br><br>
# # <br><br><br><br><br><br>
# # <br><br><br><br><br><br>
#
# # <br><br><br><br><br><br>
# # <br><br><br><br><br><br>
# # <br><br><br><br><br><br>
#
# # <br><br><br><br><br><br>
# # <br><br><br><br><br><br>
# # <br><br><br><br><br><br>
