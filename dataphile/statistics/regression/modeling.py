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

"""Construct analytic models to optimize against data."""

from typing import List, Tuple, Dict, Callable, Any, Union
from numbers import Number
import itertools

import numpy as np
import pandas as pd
from astropy.units import Quantity
from scipy.optimize import curve_fit

import matplotlib as mpl
import matplotlib.figure
import matplotlib.lines
from matplotlib import widgets
from matplotlib import pyplot as plot

from ...graphics.widgets import Slider

class Model:
    """Represents a mathematical (analytical) function with associated `Parameter`s."""
    # added to allow for type checking in Parameter Implementation

class Parameter:
    """Structure for associating numerical value, uncertainty, bounds, etc.

       Attributes
       ----------
       value: float
           The numerical value of the parameter.
       uncertainty: float (default=None)
           The uncertainty (i.e., expected error) in the value of the parameter.
       bounds: Tuple[float,float] (default=None)
           The lower and upper bound for the parameter.
       model: Model (default=None)
           The associated Model for the parameter (owner of the parameter).
           This is automatically set by the Model when passing the parameter to it.
       label: str (default=None)
           The name of the parameter (used by the Model for display purposes).
    """

    def __init__(self, value: float, uncertainty: float=None, bounds: Tuple[float, float]=None,
                 model: Model=None, label: str=None):
        """Initialize attributes."""

        self.value = value
        self.uncertainty = uncertainty
        self.bounds = bounds
        self.model = model
        self.label = label

    @property
    def value(self) -> float:
        """The numerical value of the parameter."""
        return self.__value

    @value.setter
    def value(self, val: float) -> None:
        """Set the value of the parameter."""
        if not isinstance(val, Number):
            raise TypeError('{}.value expects type float, given {}.'
                            .format(self.__class__.__name__, val))
        # FIXME: propery check of bounds when assigning a value.
        # elif '_{}__bounds'.format(self.__class__.__name__) in self.__dict__:
        #     # __bounds doesn't exist at this point when first creating the Parameter
        #     if self.bounds is not None and val < self.bounds[0] or val > self.bounds[1]:
        #         raise ValueError('{0}.value (label={1}) has bounds {2} but was assigned a value'
        #                          '{3} outside that range. '
        #                          .format(self.__class__.__name__, self.label, self.bounds, val))
        else:
            self.__value = float(val)


    @property
    def uncertainty(self) -> float:
        """The uncertainty (i.e., expected error) in the value of the parameter."""
        return self.__uncertainty

    @uncertainty.setter
    def uncertainty(self, val: float) -> None:
        """Set the uncertainty of the parameter."""
        if isinstance(val, Number):
            self.__uncertainty = float(val)
        elif val is None:
            self.__uncertainty = None
        else:
            raise TypeError('{}.uncertainty expects type float, given {}.'
                            .format(self.__class__.__name__, val))

    @property
    def bounds(self) -> Tuple[float,float]:
        """The lower and upper bound for the parameter."""
        return self.__bounds

    @bounds.setter
    def bounds(self, val: Tuple[float,float]) -> None:
        """Set the bounds for the parameter."""
        if hasattr(val, '__iter__') and all(isinstance(v, Number) for v in val):
            self.__bounds = tuple(val)
        elif val is None:
            self.__bounds = None
        else:
            raise TypeError('{}.bounds expects tuple (float, float), given {}.'
                            .format(self.__class__.__name__, val))

    @property
    def model(self) -> Model:
        """The associated Model for the parameter (owner of the parameter).
           This is automatically set by the Model when passing the parameter to it.
        """
        return self.__model

    @model.setter
    def model(self, val: Model) -> None:
        """Set the associated Model for the parameter."""
        if isinstance(val, Model):
            self.__model = val
        elif val is None:
            self.__model = None
        else:
            raise TypeError('{}.model must be type Model, given {}'
                            .format(self.__class__.__name__, type(val)))

    @property
    def label(self) -> str:
        """The name of the parameter (used by the Model for display purposes)."""
        return self.__label

    @label.setter
    def label(self, val: str) -> None:
        """Set the label for the parameter."""
        if isinstance(val, str):
            self.__label = str(val)
        elif val is None:
            self.__label = None
        else:
            raise TypeError('{}.label expects a string, given {}.'
                            .format(self.__class__.__name__, type(val)))

    def __str__(self) -> str:
        """String representation of the instance."""
        return '<{} {}>'.format(self.__class__.__name__,
                                ' '.join(['{}={}'.format(attr, getattr(self, attr)) for attr in [
                                'label', 'value', 'uncertainty', 'bounds', 'model']]))

    def __repr__(self) -> str:
        """Representation for parameter."""
        return str(self)

class Model:
    """Represents a mathematical (analytical) function with associated `Parameter`s."""

    def __init__(self, f: Callable, *parameters: Parameter, label: str=None,
                 optimizer: Callable=curve_fit):
        """Initialize attributes.

           Arguments
           ---------
           f: Callable
               Assummed to follow `ydata = f(xdata, *p) + eps`.
           *parameters: Parameter
               One or more Parameter objects.

           Options
           -------
           label: str (default=None)
               Name to be used for the model (for display purposes).
           optimizer: Callable (default=scipy.optimize.curve_fit)
               Function to call for optimization. If not `scipy.optimize.curve_fit` it must
               follow the same interface (f(Array, ...), Array, Array, ...) -> (Array, Array).
        """
        self.function = f
        self.parameters = parameters
        self.label = label
        self.optimizer = optimizer

        for parameter in parameters:
            parameter.model = self  # associate with parent Model
            try:
                # e.g., Model.phase : <Parameter ... label='phase'>
                setattr(self, parameter.label, parameter)
            except:
                pass # label probably had a space in the name!

    @property
    def function(self) -> Callable:
        """Analytic function for the model. Assummed to follow `ydata = f(xdata, *p) + eps`."""
        return self.__function

    @function.setter
    def function(self, val: Callable) -> None:
        """Set the function for the model."""
        if isinstance(val, Callable):
            self.__function = val
        else:
            raise TypeError('{}.function expects a callable type, given {}.'
                            .format(self.__class__.__name__, type(val)))
    @property
    def parameters(self) -> List[Parameter]:
        """Tuple of the model parameters."""
        return self.__parameters

    @parameters.setter
    def parameters(self, val: List[Parameter]) -> None:
        """Set model parameters."""
        if not hasattr(val, '__iter__') or not all(isinstance(v, Parameter) for v in val):
            raise TypeError('{}.parameters expects Tuple[Parameter, ...], given {}.'
                            .format(self.__class__.__name__, val))
        else:
            self.__parameters = list(val)

    @property
    def label(self) -> str:
        """Label (name) of model."""
        return self.__label

    @label.setter
    def label(self, val: str) -> None:
        """Set label for model."""
        if not isinstance(val, str):
            raise TypeError('{}.label expects a string, given {}.'
                            .format(self.__class__.__name__, type(val)))
        else:
            self.__label = str(val)

    @property
    def optimizer(self) -> Callable:
        """Optimizer (callable function) used to minimize 'function'."""
        return self.__optimizer

    @optimizer.setter
    def optimizer(self, val: Callable) -> None:
        """"""
        if not isinstance(val, Callable):
            raise TypeError('{}.optimizer requires a callable function, given {}.'
                            .format(self.__class__.__name__, type(val)))
        else:
            self.__optimizer = val

    @property
    def values(self) -> List[float]:
        """Values of each Parameter."""
        return [p.value for p in self.parameters]

    @values.setter
    def values(self, val: List[float]) -> None:
        """Set values for parameters, respectively."""
        if not hasattr(val, '__iter__') or len(val) != len(self.parameters):
            raise TypeError('{0}.values expects an iterable with the same shape as '
                            '{0}.parameters ({1}), given {2}'
                            .format(self.__class__.__name__, len(self.parameters), val))
        for p, v in zip(self.parameters, val):
            p.value = v

    @property
    def uncertainties(self) -> List[float]:
        """Uncertainties of parameters, respectively."""
        return [p.uncertainty for p in self.parameters]

    @uncertainties.setter
    def uncertainties(self, val: List[float]) -> None:
        """Set uncertainties for parameters, respectively."""
        if not hasattr(val, '__iter__') or len(val) != len(self.parameters):
            raise TypeError('{0}.uncertainties expects an iterable with the same shape as '
                            '{0}.parameters ({1}), given {2}'
                            .format(self.__class__.__name__, len(self.parameters), val))
        for p, v in zip(self.parameters, val):
            p.uncertainty = v

    def fit(self, xdata: np.ndarray, ydata: np.ndarray, **options) -> None:
        """Apply `scipy.optimize.curve_fit` against the provided 'xdata' and 'ydata'."""

        # currently set bounds on parameters (np.nan means _no_ bounds)
        bounds=([-np.nan if p.bounds is None else p.bounds[0] for p in self.parameters],
                [ np.nan if p.bounds is None else p.bounds[1] for p in self.parameters])

        # run optimization against current parameter values
        popt, pcov = self.optimizer(self.function, xdata, ydata, p0=self.values, **options)

        # reassign parameter values and attribute variances
        self.values = popt
        self.uncertainties = np.sqrt(pcov.diagonal())

    def solve(self, xdata: np.ndarray) -> np.ndarray:
        """Evaluate the model against a new set of 'xdata'."""
        return self.function(xdata, *self.values)

    def __call__(self, xdata: np.ndarray) -> np.ndarray:
        """Evaluate the model against a new set of 'xdata'."""
        return self.solve(xdata)

    def summary(self) -> pd.DataFrame:
        """Return a summary table of current parameters."""
        return pd.DataFrame({'parameter': [p.label for p in self.parameters],
                             'value': self.values,
                             'uncertainty': self.uncertainties,
                             'model': [p.model.label for p in self.parameters]
                             }).set_index(['model', 'parameter'])

class CompositeModel(Model):
    """A model constructed of a superposition of two or more `Model`s."""

    def __init__(self, *models: Model, label: str=None, optimizer: Callable=curve_fit):
        """Initialize the model."""

        self.models = models
        self.label = label
        self.optimizer = optimizer
        for model in models:
            model.parent = self # associate with parent
            try:
                setattr(self, model.label, model)
            except:
                # probably a space in the name or label not given
                pass

        # helper collections for 'function' superposition
        self.__index_map = list(itertools.accumulate([0] + [len(model.parameters) for model in models]))
        self.__index_pairs = [tuple(self.__index_map[i-1:i+1]) for i in range(1, len(self.__index_map))]

    @property
    def models(self) -> Tuple[Model, ...]:
        """Component models."""
        return self.__models

    @models.setter
    def models(self, val: Tuple[Model, ...]) -> None:
        """Set component models, respectively."""
        if not hasattr(val, '__iter__') or not all(isinstance(v, Model) for v in val):
            raise TypeError('{0}.models expects Tuple[Model, ...], given {1}'
                            .format(self.__class__.__name__, val))
        else:
            self.__models = tuple(val)

    @property
    def parameters(self) -> List[Parameter]:
        """Return a flattened list of parameters from the 'models'."""
        return [p for model in self.models for p in model.parameters]

    @property
    def values(self) -> List[float]:
        """Return list of numerical values for parameters."""
        return [p.value for p in self.parameters]

    @values.setter
    def values(self, val: List[float]) -> None:
        """Set values of parameters of each model, respectively."""
        if not hasattr(val, '__iter__') or not all(isinstance(v, float) for v in val):
            raise TypeError('{0}.values expects List[float], given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            for p, v in zip(self.parameters, val):
                p.value = v

    @property
    def uncertainties(self) -> List[float]:
        """Return list of uncertainties for parameters, respectively."""
        return [p.uncertainty for p in self.parameters]

    @uncertainties.setter
    def uncertainties(self, val: List[float]) -> None:
        """Set uncertainties of parameters of each model, respectively."""
        if not hasattr(val, '__iter__') or not all(isinstance(v, float) for v in val):
            raise TypeError('{0}.uncertainties expects List[float], given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            for p, v in zip(self.parameters, val):
                p.uncertainty = v

    def function(self, x: np.ndarray, *p: float) -> np.ndarray:
        """A composite function as a superposition of included model functions."""
        return sum([model.function(x, *p[loc[0]:loc[1]])
                    for loc, model in zip(self.__index_pairs, self.models)])


class AutoGUI:
    """Automatically generate a graphical interface for manipulating model parameters."""
    # TODO: simple example in __doc__ string.

    def __init__(self, model: Model, graphs: List[mpl.lines.Line2D]=None, figure: mpl.figure.Figure=None,
                 bbox: List[float]=[0, 0, 1, 1], background: Union[bool,str]=None, border: bool=False,
                 radio_options: Dict[str, Any]=None, slider_options: Dict[str, Any]=None,
                 data: Tuple[np.ndarray, np.ndarray]=None):
        """Initialize elements of the GUI.

           Arguments
           ---------
           model: Model
               Model or CompositeModel for the GUI. This specifies what sliders are
               to be created and how to label and switch between them.
           graphs: List[mpl.lines.Line2D] (default=None)
               If not provided, AutoGUI will plot a smooth curve over the current axis,
               i.e., graph, = plot.gca().plot(x_samples, model(x_samples), 'k--'). Otherwise,
               one or more of these can be provided and all will be updated to changing parameters.
           figure: mpl.figure.Figure (default=None)
               The figure onto which the widget elements will be created. This can be the same as
               the graphs, or could be a separate figure (i.e., window).
           bbox: List[float] (default=[0, 0, 1, 1])
               The subregion within the figure to build the widget elements. When sharing the figure
               with the graphs, this defines where on the canvas to draw.
           border: bool (default=False)
               If True, this actually puts a rectangular border around the bbox region.
           background: str (default=None)
               Use a solid background color behind widgets (e.g., 'white').
           radio_options: Dict[str, Any] (default=None)
               Named parameters (a.k.a., "kwargs") passed to mpl.widgets.RadioButtons.
           slider_options: Dict[str, Any] (default=None)
               Named parameters (a.k.a., "kwargs") passed to mpl.widters.Slider.
           data: Tuple[np.ndarray, np.ndarray] (default=None)
               If provided with (xdata, ydata), create a 'Fit' button and optimize the provided
               data with the current model parameter values as initial guess.
        """

        # initialize attributes
        self.model = model
        self.graphs = graphs
        self.figure = figure
        self.bbox = bbox
        self.border = border
        self.background = background
        self.radio_options = radio_options
        self.slider_options = slider_options
        self.data = data

        # access modes
        self.__models_by_label = {model.label: model for model in self.models}
        self.__models_by_index = {i: model for i, model in enumerate(self.models)}
        self.__index_by_models = {model.label: i for i, model in enumerate(self.models)}

        # create axis if border is requested
        if self.border is True:
            self.__create_background()

        # a simple model doesn't require a selection widget (radio buttons)
        # the sliders will be created for the first (or only) model and if
        # needed a radio button selector will toggle through the slider sets
        if isinstance(self.model, CompositeModel):
            self.__create_radio()
        self.__sliders = list()
        self.__create_sliders(self.active_model.label)

        # TODO: Add action buttons (e.g., 'fit')
        if self.data is not None:
            self.__create_fit_button()
        # self.__create_undo_button()
        # ...

    @property
    def model(self) -> Model:
        """The underlying model for the GUI."""
        return self.__model

    @model.setter
    def model(self, val: Model) -> None:
        """Set the model for the GUI."""
        if not isinstance(val, Model):
            raise TypeError('{0}.model expects a Model (or CompositeModel), given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            self.__model = val
            # changing the model changes the necessary GUI.
            # TODO: allow for dynamic changes to the GUI.
            # re-initialize access modes
            self.__models_by_label = {model.label: model for model in self.models}
            self.__models_by_index = {i: model for i, model in enumerate(self.models)}
            self.__index_by_models = {model.label: i for i, model in enumerate(self.models)}

    @property
    def models(self) -> List[Model]:
        """If CompositeModel return list of components, else [model]."""
        if not isinstance(self.model, CompositeModel):
            return [self.model]
        else:
            return list(self.model.models)

    @property
    def graphs(self) -> List[mpl.lines.Line2D]:
        """Curves to be updated when interacting with widgets."""
        return self.__graphs

    @graphs.setter
    def graphs(self, val: List[mpl.lines.Line2D]) -> None:
        """Assign curves to update when interacting with widgets."""
        if val is None:
            self.__graphs = self.__create_default_graphs()
        elif not hasattr(val, '__iter__') or not all(isinstance(v, mpl.lines.Line2D) for v in val):
            raise TypeError('{0}.graphs expects all to Line2D, given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            self.__graphs = list(val)

    def __create_default_graphs(self) -> List[mpl.lines.Line2D]:
        """Create default graph for widget elements to manipulate."""
        if '_{}__graph'.format(self.__class__.__name__) in self.__dict__:
            raise AttributeError('{0}.__graph alread exists!'.format(self.__class__.__name__))
        else:
            xmin, xmax = plot.gca().get_xlim()
            xsamples = np.linspace(xmin, xmax, 10000) # TODO: better choice of xsamples
            graph, = plot.gca().plot(xsamples, self.model(xsamples), 'k--',
                                     label='{} model'.format(self.model.label))
            return graph

    @property
    def figure(self) -> mpl.figure.Figure:
        """Figure (mpl.figure.Figure) used for widget elements."""
        return self.__figure

    @figure.setter
    def figure(self, val: mpl.figure.Figure) -> None:
        """Assign the figure (mpl.figure.Figure) to use for widget elements."""
        if not isinstance(val, (mpl.figure.Figure, type(None))):
            raise TypeError('{0}.figure expects mpl.figure.Figure, given {1}.'
                            .format(self.__class__.__name__, val))
        elif val is None:
            self.__figure = plot.gca().figure # default figure
        else:
            self.__figure = val

    @property
    def bbox(self) -> List[float]:
        """The subregion (bounding box) within which to create the widget elements."""
        return self.__bbox

    @bbox.setter
    def bbox(self, val: List[float]) -> None:
        """Assign subregion (bounding box) within which to create the widget elements."""
        if val is None:
            self.__bbox = [0, 0, 1, 1]
        elif not hasattr(val, '__iter__') or not all(isinstance(v, Number) for v in val):
            raise TypeError('{0}.bbox expects List[float], given {1}.'
                            .format(self.__class__.__name__, val))
        elif len(val) != 4:
            raise ValueError('{0}.bbox expects a list of exactly four values, given {1}.'
                             .format(self.__class__.__name__, val))
        else:
            self.__bbox = val

    @property
    def border(self) -> bool:
        """True/False - use border around widget elements."""
        return self.__border

    @border.setter
    def border(self, val: bool) -> None:
        """Assign True/False - use border around widget elements."""
        if not isinstance(val, bool):
            raise TypeError('{0}.border expects True or False, given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            self.__border = val

    @property
    def background(self) -> str:
        """Whether to use filled background behind widget elements.
           Either None, or a str with name of color (e.g., 'white').
        """
        return self.__background

    @background.setter
    def background(self, val: str) -> None:
        """Assign background color."""
        if val is None:
            self.__background = None
        elif not isinstance(val, str):
            raise ValueError('{0}.background expects str, given {1}.'
                             .format(self.__class__.__name__, val))
        else:
            self.__background = val

    @property
    def radio_options(self) -> Dict[str, Any]:
        """Parameters (a.k.a., "kwargs") for mpl.widgets.RadioButtons."""
        return self.__radio_options

    @radio_options.setter
    def radio_options(self, val: Dict[str, Any]) -> None:
        """Assign parameters (a.k.a., "kwargs") for mpl.widgets.RadioButtons."""
        if val is None:
            self.__radio_options = dict()
        elif not isinstance(val, dict) or not all(isinstance(k, str) for k in val.keys()):
            raise TypeError('{0}.radio_options expects Dict[str, Any], given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            self.__radio_options = val

    @property
    def slider_options(self) -> Dict[str, Any]:
        """Parameters (a.k.a., "kwargs") for dataphile.graphics.widgets.Slider."""
        return self.__slider_options

    @slider_options.setter
    def slider_options(self, val: Dict[str, Any]) -> None:
        """Assign parameters (a.k.a., "kwargs") for dataphile.graphics.widgets.Slider."""
        if val is None:
            self.__slider_options = dict()
        elif not isinstance(val, dict) or not all(isinstance(k, str) for k in val.keys()):
            raise TypeError('{0}.slider_options expects Dict[str, Any], given {1}.'
                            .format(self.__class__.__name__, val))
        else:
            self.__slider_options = val

    @property
    def sliders(self) -> List[Slider]:
        """Currently active sliders for GUI."""
        return self.__sliders

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
    def radio(self) -> mpl.widgets.RadioButtons:
        """Access to the radio buttons widget."""
        return self.__radio

    @property
    def sliders(self) -> List[Slider]:
        """Access to list of current available sliders."""
        return self.__sliders

    @property
    def data(self) -> Tuple[np.ndarray, np.ndarray]:
        """The x and y data to optimize the model against."""
        return self.__data

    @data.setter
    def data(self, val: Tuple[np.ndarray, np.ndarray]) -> None:
        """Assign x and y data to optimize the model against."""
        if val is None:
            self.__data = None  # don't create a Fit button
        elif not hasattr(val, '__iter__') or len(val) != 2 or not val[0].shape == val[1].shape:
            raise ValueError('{0}.data expects Tuple[np.ndarray, np.ndarray] with equal lengths.'
                             .format(self.__class__.__name__))
        else:
            self.__data = tuple(val)

    def __create_radio(self) -> None:
        """Build the radio widget."""

        # create new axis for radio widget
        x0 = self.bbox[0]
        y0 = self.bbox[1]
        width = self.bbox[2] / 3
        height = self.bbox[3]
        axis = self.figure.add_axes([x0, y0, width, height])

        # formatting
        axis.patch.set_facecolor('none')
        axis.patch.set_edgecolor('none')
        for edge in 'left', 'right', 'top', 'bottom':
            axis.spines[edge].set_visible(False)
        self.__radio_axis = axis

        # create widget
        options = {'activecolor': 'steelblue'}
        options.update(self.radio_options)
        self.__radio = widgets.RadioButtons(axis, tuple(model.label for model in self.models),
                                            **options)
        # update function
        self.__radio.on_clicked(self.__radio_on_clicked)

    def __radio_on_clicked(self, label: str) -> None:
        """Action to take in the event that a button is selected on the radio widget."""
        self.__create_sliders(label) # recreate the sliders for the currently selected model
        self.figure.canvas.draw_idle()

    def __create_sliders(self, label: str) -> None:
        """Create all necessary sliders for currently selected models."""

        # currently selected model
        model = self.__models_by_label[label]

        # fixed height
        maxN = max(len(model.parameters) for model in self.models)
        width = 0.90 * (2/3) * self.bbox[2]
        height = self.bbox[3] / maxN  # percent of bbox height
        padding = height / 2
        x0, y0 = self.__abs_pos(1/3, 0) # 2/3 into bbox

        options = dict()
        options.update(self.slider_options)
        self.__remove_sliders() # remove old sliders
        for count, parameter in enumerate(model.parameters):

            slider = Slider(figure=self.figure,
                            location=[x0, y0 + self.bbox[3] - (1 + count)*height, width, height],
                            label=parameter.label, bounds=parameter.bounds, init_value=parameter.value,
                            **options)
            slider.on_changed(self.__slider_update_function)
            self.sliders.append(slider)

    def __remove_sliders(self) -> None:
        """Remove sliders from view."""
        for slider in self.sliders:
            slider.remove()
        self.sliders.clear()

    def __slider_update_function(self, value: float) -> None:
        """Redraw graph based on current values."""

        # update parameter values of currently selected component
        for slider, parameter in zip(self.sliders, self.active_model.parameters):
            parameter.value = slider.value

        self.__update_graph()

    def __update_graph(self) -> None:
        """Re-draw curves based on current slider values."""
        for graph in self.graphs:
            graph.set_ydata(self.model(graph.get_xdata()))
            graph.figure.canvas.draw_idle()

    def __abs_pos(self, x: float, y: float) -> List[float]:
        """Helper function returns absolute x and/or y values (percent) given relative values."""
        assert x >= 0 and x <= 1 and y >= 0 and y <= 1
        x0, y0, width, height = self.bbox
        return (x0 + x * width, y0 + y * height)

    def __create_background(self) -> None:
        """Create a bare axis for background (with/without border)."""
        if self.background is None:
            raise ValueError('No background color specified.')

        # create axis
        self.__background_axis = self.figure.add_axes(self.bbox)

        # facecolor, ticks and grid
        self.__background_axis.set_facecolor('white')
        self.__background_axis.grid(False)
        self.__background_axis.set_xticks([])
        self.__background_axis.set_yticks([])

        if self.border is False:
            for edge in 'left', 'right', 'top', 'bottom':
                self.__background_axis.spines[edge].set_visible(False)

    def __create_fit_button(self) -> None:
        """Create a button widget to calls the 'model.fit' function."""

        # geometry
        width = 0.08  # of figure
        height = 0.05  # of figure
        x0 = self.bbox[0] + self.bbox[2] - width - 0.03
        y0 = self.bbox[1] - height  # under the bbox
        self.__fit_button_ax = self.figure.add_axes([x0, y0, width, height])
        self.__fit_button = widgets.Button(self.__fit_button_ax, label='Fit',
                                           color='steelblue', hovercolor='lightgray')

        self.__fit_button.on_clicked(self.__fit_button_on_clicked)

    def __fit_button_on_clicked(self, event):
        """Action to take when the 'Fit' button is pressed."""
        # call the model.fit with data
        self.model.fit(*self.data)
        self.__update_graph()
        self.__create_sliders(self.active_model.label)
