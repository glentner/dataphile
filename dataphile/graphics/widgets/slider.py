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

"""Contains the Slider implementation.
   dataphile.graphics.widgets.slider

   Dataphile, 0.1.4
   Copyright (c) Geoffrey Lentner 2018. All rights reserved.
   GNU General Public License v3. See LICENSE file.
"""


from typing import List, Tuple, Callable

import matplotlib as mpl
from matplotlib import widgets

class Slider:
    """Built on `matplotlib.Slider` to create modern looking slider."""

    def __init__(self,
                 figure: mpl.figure.Figure,
                 location: List[float], # length 4 (for `figure.add_axes`)
                 label: str,
                 bounds: Tuple=(0, 1),
                 init_value: float=None,
                 color=(0.2980392156862745, 0.4470588235294118, 0.6901960784313725, 1.0)  # Seaborn default blue
                 ):
        """Initialize the widget elements."""

        # attributes
        self.figure = figure
        self.location = list(location)
        self.label = label
        self.bounds = tuple(bounds)
        self.init_value = init_value
        self.color = color
        self._padding = 0.05 # gives room for 'knob'

        # create background UX axis and elements
        self._create_ux_layer()

        # create overlaying widget layer
        self._create_widget_layer()

        # basic update (override with 'on_changed')
        def update(value):
            self._update_ux(value)

        self.widget.on_changed(update)

    def _create_ux_layer(self):
        """Build the UX axis on the figure and populate the UX elements (line, knob, etc.)."""

        self._ux_axis = self.figure.add_axes(self.location)

        # hide spines but show dashed outline
        for side in 'left', 'right', 'top', 'bottom':
            self._ux_axis.spines[side].set_visible(False)
        self._ux_axis.set_xlim(0, 1)
        self._ux_axis.set_ylim(0, 1)
        self._ux_axis.set_xticks([])
        self._ux_axis.set_yticks([])
        # self._ux_axis.plot([0, 0], [0, 1], '--', color='gray') # used in prototyping
        # self._ux_axis.plot([0, 1], [1, 1], '--', color='gray')
        # self._ux_axis.plot([1, 1], [1, 0], '--', color='gray')
        # self._ux_axis.plot([1, 0], [0, 0], '--', color='gray')
        self._ux_axis.tick_params(length=0)
        self._ux_axis.patch.set_alpha(0)

        # plot underlying UX elements
        p = self._padding # shorthand
        self._ux_line_groove, = self._ux_axis.plot([p, 1-p], [0.5, 0.5], color='lightgray', linewidth=3, zorder=10)
        self._ux_line_filled, = self._ux_axis.plot([p, self._ux_from_world(self.init_value)], [0.5, 0.5],
                                                   color=self.color, linewidth=3, zorder=20)
        self._ux_knob = self._ux_axis.scatter([self._ux_from_world(self.init_value)], [0.5],
                                              marker='o', edgecolor=self.color, facecolor='white',
                                              linewidth=1, s=150, zorder=30)

    def _create_widget_layer(self):
        """Add the `matplotlib.widget.Slider` over the UX axis and make transparent."""

        # find location of start of UX elements
        ux_start, ux_end = self.pos.x0, self.pos.x0 + self.pos.width
        pad = self._padding * (ux_end - ux_start) # figure level coordinates

        # matplotlib slider widget layered overtop of UX axis
        self._widget_axis = self.figure.add_axes([self.pos.x0 + pad, self.pos.y0, self.pos.width - 2*pad, self.pos.height])
        self._widget_axis.patch.set_alpha(0)
        for side in 'left', 'right', 'top', 'bottom':
            self._widget_axis.spines[side].set_visible(False)

        # create slider
        self.widget = widgets.Slider(self._widget_axis, self.label, *self.bounds, valinit=self.init_value)

        # adjust formatting
        self.widget.vline.set_visible(False)
        self.widget.poly.set_edgecolor('none')
        self.widget.poly.fill = False
        self.widget.label.set_position([self.widget.label.get_position()[0] - pad/2, 0.5])
        self.widget.valtext.set_position([self.widget.valtext.get_position()[0] + pad/2, 0.5])

    @property
    def pos(self) -> mpl.transforms.Bbox:
        """Return the BBox object for the underlying UX axis object."""
        return self._ux_axis.get_position()

    @property
    def value(self) -> float:
        """Return the numerical value of the current slider position."""
        return self.widget.val

    @value.setter
    def value(self, value_: float) -> None:
        """Set the slider manually."""
        self.widget.set_val(value_)

    def _ux_from_world(self, value: float) -> float:
        """Convert real value into UX slider value (which is padded, not 0-1)."""

        # percent of world value
        w_min, w_max = self.bounds
        w_per = (value - w_min) / (w_max - w_min)

        # location of UX slider
        s_min, s_max = self._padding, 1 - self._padding
        s_loc = s_min + w_per * (s_max - s_min)

        return s_loc

    def _update_ux(self, value: float) -> None:

        # ux value from world value
        s_loc = self._ux_from_world(value)

        # update UX elements
        self._ux_knob.set_offsets([[s_loc, 0.5]])
        self._ux_line_filled.set_xdata([self._padding, s_loc])

        # TODO: update value text with unit
        # self.widget.valtext.set_text(self.widget.valtext.get_text() + '  [{}]'.format(self.units))

        # draw
        self.figure.canvas.draw_idle()

    def on_changed(self, user_function: Callable[[float], None]) -> None:
        """Update underlying UX along with user defined function."""

        def _wrapped(value: float) -> None:
            self._update_ux(value)
            user_function(value)

        self.widget.on_changed(_wrapped)

    def remove(self) -> None:
        """Remove both axes."""
        self._ux_axis.remove()
        self._widget_axis.remove()
