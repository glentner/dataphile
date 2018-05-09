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

"""Construct analytic models to optimize against data.
   dataphile.regression.modeling

   DataPhile, 0.0.2
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""

from typing import List, Tuple, Callable
from numbers import Number
import itertools

import numpy as np
from astropy.units import Quantity
from scipy.optimize import curve_fit

import matplotlib as mpl
import matplotlib.figure
import matplotlib.lines
from matplotlib import widgets


from ...graphics.widgets import Slider


class Parameter:
    """Base element of a 'Model'.

       Attributes
       ----------
       label: str
            Name for the parameter (used in creating interactive widgets).

       value: float
           Current numerical value of the parameter.

       bounds: Tuple[float, float]
           Upper and lower limits on the parameter value - used by both the optimization
           process and the interactive widgets.

       error: float
           Uncertainty in the numerical value (absolute not relative). This is automatically
           set after the optmiization (not necessarily by the user).
    """
    def __init__(self, label: str, value: Number, bounds: Tuple[Number, Number]):

        self.__label  = label
        self.__value  = value
        self.__bounds = bounds
        self.__error  = None

    def __str__(self):
        """Return string representation."""
        return 'Parameter[{0}: {1} < {2} < {3}]'.format(self.label, self.bounds[0], self.value, self.bounds[1])

    def __repr__(self):
        return str(self)

    @property
    def label(self) -> str:
        """Access the label (name) of the parameter."""
        return self.__label

    @label.setter
    def label(self, value: str) -> None:
        """Set the label (name) of the parameter."""
        if not isinstance(value, str):
            raise ValueError('Parameter.label must be a string type.')
        else:
            self.__label = str(value)

    @property
    def value(self) -> Number:
        """Access the numerical value of the parameter."""
        return self.__value

    @value.setter
    def value(self, value_: Number) -> None:
        """Set the numerical value of the parameter."""
        if not isinstance(value_, (Number, Quantity)):
            raise ValueError('Parameter.value must be a Number or Quantity.')
        else:
            self.__value = value_

    @property
    def bounds(self) -> Tuple[Number, Number]:
        """Access the bounding values of the parameter."""
        return self.__bounds

    @bounds.setter
    def bounds(self, value: Tuple[Number, Number]) -> None:
        """Set the bounding values of the parameter."""
        if hasattr(value, '__iter__') and len(value) == 2:
            self.__bounds = tuple(value)
        else:
            raise ValueError('Parameter.bounds must be a set of two numerical values.')

    @property
    def error(self) -> Number:
        """Access uncertainty of parameter."""
        return self.__error

    @error.setter
    def error(self, value: Number) -> None:
        """Set uncertainty value of parameter."""
        if isinstance(value, (Number, Quantity)):
            self.__error = value
        else:
            raise ValueError('Parameter.error must be a Number or Quantity.')


class Model:
    """Represents a mathematical (analytics) function with associated `Parameter`s.
    """

    def __init__(self, label: str, function: Callable, *parameters: Parameter):
        """Initialize the model with the underlying function and its parameters."""

        self.__label = label
        self.__function = function
        self.__parameters = parameters
        for parameter in parameters:
            parameter.model = self  # associate with parent Model
            try:
                setattr(self, parameter.label, parameter)
            except:
                pass # label probably had a space in the name

    def fit(self, xdata: np.ndarray,
                  ydata: np.ndarray,
                  weights: np.ndarray=None,
                  relative: bool=False,
                  **options) -> None:
        """Apply `scipy.optimize.curve_fit` against the provided 'xdata' and 'ydata'."""

        # solve for optimimum parameters
        popt, pcov = curve_fit(self.function, xdata, ydata, p0=self.values, sigma=weights,
                               absolute_sigma = not relative,
                               bounds=([p.bounds[0] for p in self.parameters],
                                       [p.bounds[1] for p in self.parameters]),
                               **options)

        # reassign parameter values and attribute variances
        for parameter, value, variance in zip(self.parameters, popt, pcov.diagonal()):
            parameter.value = value
            parameter.error = np.sqrt(variance)

    def solve(self, xdata: np.ndarray) -> np.ndarray:
        """Evaluate the model against a new set of 'xdata'."""
        return self.function(xdata, *self.values)

    def __call__(self, xdata: np.ndarray) -> np.ndarray:
        """Evaluate the model against a new set of 'xdata'."""
        return self.solve(xdata)

    @property
    def values(self) -> List[float]:
        """Return list of parameter values."""
        return [p.value for p in self.parameters]

    @property
    def errors(self) -> List[float]:
        """Return list of parameter errorrs."""
        return [p.error for p in self.parameters]

    @property
    def label(self) -> str:
        """Access label (name) of model."""
        return self.__label

    @label.setter
    def label(self, value: str) -> None:
        """Set the label (name) of model."""
        if isinstance(value, str):
            self.__label = str(value)
        else:
            raise ValueError('Model.label must be a string type.')

    @property
    def function(self) -> Callable[[np.ndarray], np.ndarray]:
        """Access to underlying function for the model."""
        return self.__function

    @function.setter
    def function(self, value: Callable[[np.ndarray], np.ndarray]) -> None:
        """Set the underlying function for the model."""
        if hasattr(value, '__call__'):
            self.__function = value
        else:
            raise ValueError('Model.function must be callable.')

    @property
    def parameters(self) -> List[Parameter]:
        """Access model parameters."""
        return self.__parameters

    @parameters.setter
    def parameters(self, value: List[Parameter]) -> None:
        """Set model parameters."""
        if hasattr(value, '__iter__') and all(isinstance(p, Parameter) for p in value):
            self.__parameters = list(value)
        else:
            raise ValueError('Model.parameters must be a list of Parameter objects.')


class CompositeModel(Model):
    """A model constructed of a superposition of two or more `Model`s."""

    def __init__(self, *models: Model):
        """Initialize the model."""

        # data
        self.__models = models
        for model in models:
            model.parent = self # associate with parent
            try:
                setattr(self, model.label, model)
            except:
                pass # probably a space in the name

        # helper collections
        self.__index_map = list(itertools.accumulate([0] + [len(model.parameters) for model in models]))
        self.__index_pairs = [tuple(self.__index_map[i-1:i+1]) for i in range(1, len(self.__index_map))]

    @property
    def models(self) -> List[Model]:
        """Access underlying component models."""
        return self.__models

    @models.setter
    def models(self, value: List[Model]) -> None:
        """Set underlying component models."""
        if hasattr(value, '__iter__') and all(isinstance(m, Model) for m in value):
            self.__models = list(value)
        else:
            raise ValueError('CompositeModel.models must be a list of Model objects.')

    @property
    def parameters(self) -> List[Parameter]:
        """Return a flattened list of parameters from the 'models'."""
        return [p for model in self.models for p in model.parameters]

    @property
    def values(self) -> List[float]:
        """Return list of numerical values for parameters."""
        return [p.value for p in self.parameters]

    @property
    def errors(self) -> List[float]:
        """Return list of uncertainties in fitted parameters."""
        return [p.error for p in self.parameters]

    def function(self, x: np.ndarray, *p: float) -> np.ndarray:
        """A composite function as a superposition of included models."""
        return sum([model.function(x, *p[loc[0]:loc[1]])
                    for loc, model in zip(self.__index_pairs, self.models)])

    def solve(self, xdata: np.ndarray) -> np.ndarray:
        """Evaluate the model with the given 'xdata' and the present parameter values."""
        return self.function(xdata, *self.values)

    def __call__(self, xdata: np.ndarray) -> np.ndarray:
        """Evaluate the composite model against the given 'xdata'."""
        return self.solve(xdata)

    def fit(self, xdata: np.ndarray,
                  ydata: np.ndarray,
                  weights: np.ndarray=None,
                  relative: bool=False,
                  **options) -> None:
        """Apply `scipy.optimize.curve_fit` against the provided 'xdata' and 'ydata'."""

        # solve for optimimum parameters
        popt, pcov = curve_fit(self.function, xdata, ydata, p0=self.values, sigma=weights,
                               absolute_sigma = not relative,
                               bounds=([p.bounds[0] for p in self.parameters],
                                       [p.bounds[1] for p in self.parameters]),
                               **options)

        # reassign parameter values and attribute variances
        for parameter, value, variance in zip(self.parameters, popt, pcov.diagonal()):
            parameter.value = value
            parameter.error = np.sqrt(variance)


class AutoGUI:
    """Generate a graphical interface for a given Model/CompositeModel."""

    def __init__(self, model:  Model,
                       graph:  mpl.lines.Line2D,
                       figure: mpl.figure.Figure=None, # defaults to graph.figure
                       bbox:   List[float]=[0, 0, 1, 1]):
        """Create the widget elements."""

        self.__model = model
        self.__graph = graph
        self.__bbox = bbox

        if figure is None:
            self.__figure = graph.figure
        else:
            self.__figure = figure


        # checks
        assert isinstance(self.figure, mpl.figure.Figure)
        assert isinstance(model, Model)
        assert len(bbox) == 4
        assert all(isinstance(val, (float, int)) for val in bbox)

        # access modes
        self.__models_by_label = {model.label: model for model in self.models}
        self.__models_by_index = {i: model for i, model in enumerate(self.models)}
        self.__index_by_models = {model.label: i for i, model in enumerate(self.models)}

        # a simple model doesn't require a selection widget (radio buttons)
        # the sliders will be created for the first (or only) model and if
        # needed a radio button selector will toggle through the slider sets
        self.sliders = list()
        self.__create_radio()
        self.__create_sliders(self.active_model.label)

        # TODO: Add action buttons (e.g., 'fit')
        # self.__create_fit_button()
        # self.__create_undo_button()
        # ...

    def __create_radio(self) -> None:
        """Create the radio widget."""

        # consistent height of individual buttons requires dynamic height of widget
        height = (1/4) / self.figure.get_size_inches()[1]  # 1/3 inch per button
        if height * len(self.models) > self.height:
            height = self.height / len(self.models) # squeeze

        # create new axis for radio widget
        axis = self.figure.add_axes([
            self.__abs_pos(0.05, 0)[0], # x0
            self.y0 + self.height - len(self.models)*height, # y0
            0.20,
            len(self.models) * height])

        # formatting
        axis.patch.set_facecolor('none')

        # create widget
        self.__radio = widgets.RadioButtons(axis, tuple(model.label for model in self.models),
                                            activecolor='steelblue')
        # update function
        self.__radio.on_clicked(self.__radio_on_clicked)

    def __create_sliders(self, label: str) -> None:
        """Create all necessary sliders for each (if multiple) models."""

        # currently selected model
        model = self.__models_by_label[label]

        # best height is about 1/3 inches
        height = (1/3) / self.figure.get_size_inches()[1] # associated percent value
        if len(model.parameters)*height > self.height:
            height = self.height / len(model.parameters) # divide evenly

        self.__remove_sliders() # remove old sliders
        for count, parameter in enumerate(model.parameters):
            slider = Slider(
                figure=self.figure,
                location=[
                    self.__abs_pos(0.35, 0)[0], # x0=35% right of bbox
                    self.y0 + self.height - height - height*count, # vertical position
                    self.__abs_pos(0.40, 0)[0], # width of slider in absolute units
                    height
                ],
                label=parameter.label,
                bounds=parameter.bounds,
                init_value=parameter.value
            )
            slider.on_changed(self.__slider_update_function)
            self.sliders.append(slider)

    def __remove_sliders(self) -> None:
        """Remove sliders from view."""
        for slider in self.sliders:
            slider.remove()
        self.sliders.clear()

    def __radio_on_clicked(self, label: str) -> None:
        """Action to take in the event that a button is selected on the radio widget."""
        # recreate the sliders for the currently selected model
        self.__create_sliders(label)
        self.figure.canvas.draw_idle()

    def __slider_update_function(self, value: float) -> None:
        """Redraw graph based on current values."""

        # update parameter values of currently selected component
        for slider, parameter in zip(self.sliders, self.active_model.parameters):
            parameter.value = slider.value

        # update graph
        self.ydata = self.model.solve(self.xdata)
        self.figure.canvas.draw_idle()

    def __abs_pos(self, x: float, y: float) -> List[float]:
        """Return absolute x and/or y values (percent) given relative values."""
        assert x >= 0 and x <= 1 and y >= 0 and y <= 1
        return (self.x0 + x * self.width, self.y0 + y * self.height)

    @property
    def figure(self) -> mpl.figure.Figure:
        """Access parent figure object."""
        return self.__figure

    @property
    def model(self) -> Model:
        """Access to associated Model."""
        return self.__model

    @property
    def models(self) -> List[Model]:
        """Return list of models (length one if not CompositeModel)."""
        if isinstance(self.model, CompositeModel):
            return list(self.model.models)
        else:
            return [self.model]

    @property
    def active_model(self) -> Model:
        """Access which model is currently selected"""
        if isinstance(self.model, CompositeModel):
            return self.__models_by_label[self.radio.value_selected]
        else:
            return self.model

    @active_model.setter
    def active_model(self, label: str) -> None:
        """Programmatically select a model."""
        if isinstance(self.model, CompositeModel):
            self.radio.set_active(self.__index_by_models[label])
        else:
            if label != self.model.label:
                raise ValueError('"{}" is the only model in use.'.format(self.model.label))

    @property
    def bbox(self) -> List[float]:
        """Access to 'bbox' location (percent of canvas) for GUI."""
        return self.__bbox

    @property
    def x0(self) -> float:
        """Location of lower left 'x' value (percent of canvas) for GUI."""
        return self.bbox[0]

    @property
    def y0(self) -> float:
        """Location of lower left 'y' value (percent of canvas) for GUI."""
        return self.bbox[1]

    @property
    def width(self) -> float:
        """Width (percent of canvas) for GUI."""
        return self.bbox[2]

    @property
    def height(self) -> float:
        """Height (percent of canvas) for GUI."""
        return self.bbox[3]

    @property
    def xdata(self) -> np.ndarray:
        """Access to underlying x-data within 'graph'."""
        return self.__graph.get_xdata()

    @xdata.setter
    def xdata(self, values: np.ndarray) -> None:
        """Assign new values to 'xdata'."""
        self.__graph.set_xdata(values)

    @property
    def ydata(self) -> np.ndarray:
        """Access to underlying y-data within 'graph'."""
        return self.__graph.get_ydata()

    @ydata.setter
    def ydata(self, values: np.ndarray) -> None:
        """Assign new values to 'ydata'."""
        self.__graph.set_ydata(values)

    @property
    def data(self) -> np.ndarray:
        """Access to underlying data within 'graph'."""
        return self.__graph.get_data()

    @data.setter
    def data(self, *values: np.ndarray) -> None:
        """Assign new values to 'data'."""
        self.__graph.set_data(*values)

    @property
    def radio(self) -> mpl.widgets.RadioButtons:
        """Access to the radio buttons widget."""
        return self.__radio
