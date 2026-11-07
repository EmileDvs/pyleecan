# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/RequestedAxis.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

import numpy as np

from ..Functions.SciDataTool import AxisError
from ..Functions.SciDataTool.symmetries import rebuild_symmetries_axis
from ._pyleecan_class import PyleecanClass
from .data_pattern import DataPattern


@dataclass(eq=False)
class RequestedAxis(PyleecanClass):
    """Class to handle requested axes during get_along methods

    Attributes
    ----------
    name : str or None
        Name requested in get_along command
        Default: None
    corr_name : str or None
        Corresponding axis if a transform is required
        Default: None
    unit : str or None
        Unit requested in get_along command
        Default: None
    corr_unit : str or None
        Corresponding unit if a transform is required
        Default: None
    extension : str or None
        Extension of the requested axis (single or interval)
        Default: None
    values : ndarray or None
        Values of the axis
        Default: None
    indices : list or None
        Indices of the axis
        Default: []
    input_data : ndarray or None
        Input data to interpolate on
        Default: None
    operation : str or None
        Operation to perform on the axis (coordinate change, etc)
        Default: None
    index : int or None
        Index of the axis in the axes list
        Default: None
    transform : str or None
        Transform to perform on the axis (fft, ifft)
        Default: None
    is_pattern : bool
        To indicate if the axis is a DataPattern
        Default: False
    rebuild_indices : ndarray or None
        Indices to rebuild pattern
        Default: None
    is_step : bool
        To indicate if the pattern axis is step (for interpolation)
        Default: False
    noct : int or None
        To store 1/nth octave band
        Default: None
    corr_values : ndarray or None
        To store original axis values (useful in case of non uniform fft)
        Default: None
    is_components : bool
        To indicate if the values are strings
        Default: False
    """

    name: str | None = None
    """Name requested in get_along command"""
    corr_name: str | None = None
    """Corresponding axis if a transform is required"""
    unit: str | None = None
    """Unit requested in get_along command"""
    corr_unit: str | None = None
    """Corresponding unit if a transform is required"""
    extension: str | None = None
    """Extension of the requested axis (single or interval)"""
    values: np.ndarray | None = None
    """Values of the axis"""
    indices: list[Any] | None = field(default_factory=list)
    """Indices of the axis"""
    input_data: np.ndarray | None = None
    """Input data to interpolate on"""
    operation: str | None = None
    """Operation to perform on the axis (coordinate change, etc)"""
    index: int | None = None
    """Index of the axis in the axes list"""
    transform: str | None = None
    """Transform to perform on the axis (fft, ifft)"""
    is_pattern: bool = False
    """To indicate if the axis is a DataPattern"""
    rebuild_indices: np.ndarray | None = None
    """Indices to rebuild pattern"""
    is_step: bool = False
    """To indicate if the pattern axis is step (for interpolation)"""
    noct: int | None = None
    """To store 1/nth octave band"""
    corr_values: np.ndarray | None = None
    """To store original axis values (useful in case of non uniform fft)"""
    is_components: bool = False
    """To indicate if the values are strings"""

    def __post_init__(self):
        super().__post_init__()

    # Inlined from Methods.SciDataTool.RequestedAxis.get_axis
    def get_axis(
        self,
        axis,
        is_real,
        *,
        operation_list=[
            "max",
            "min",
            "sum",
            "rss",
            "mean",
            "rms",
            "integrate",
            "integrate_local",
            "derivate",
            "antiderivate",
        ],
    ):
        """Computes the vector 'axis' in the unit required, using conversions and symmetries if needed.
        Parameters
        ----------
        self: RequestedAxis
            a RequestedAxis object
        axis: Axis
            an Axis object
        """

        if self.operation is not None:
            module = import_module("pyleecan.Functions.SciDataTool.conversions")
            func = getattr(module, self.operation)  # Conversion function
        if isinstance(axis, DataPattern):
            self.is_pattern = True
            self.rebuild_indices = axis.rebuild_indices
            self.is_step = axis.is_step
        is_components = getattr(axis, "is_components", False)
        if (
            is_components and axis.is_overlay and self.extension == "whole"
        ):  # To overlay curves in plots
            self.extension = "list"
            self.indices = [":"]
        if is_components:
            values = axis.get_values(unit=self.unit)
            if self.indices is not None:
                if self.indices[0] == ":":
                    self.values = values
                    self.indices = list(range(len(values)))
                elif isinstance(self.indices[0], str):  # N largest
                    self.extension = "list"
                    N = int(self.indices[0])
                    # Sort values
                    if hasattr(axis, "sort_indices") and axis.sort_indices is not None:
                        self.indices = axis.sort_indices[:N]
                        self.values = values[self.indices]
                    else:
                        self.indices = np.argsort(values)[::-1][:N].tolist()
                        self.values = values[self.indices]
                else:
                    self.values = values[self.indices]
                    self.extension = "list"
            elif self.extension not in operation_list and self.extension != "list":
                self.values = values
                self.extension = "whole"
            else:
                self.values = values

        else:
            if self.extension == "pattern":
                if not self.is_pattern:
                    raise AxisError(
                        "[pattern] cannot be called with non DataPattern axis"
                    )
                else:
                    is_smallestperiod = True
                    is_oneperiod = False
                    is_antiperiod = False
                    self.extension = "smallestperiod"
            elif self.extension == "smallestperiod":
                # if isinstance(axis, DataPattern):
                #     raise AxisError(
                #         "[smallestperiod] cannot be called with DataPattern axis"
                #     )
                # else:
                is_smallestperiod = True
                is_oneperiod = False
                is_antiperiod = False
            elif self.extension == "antiperiod":
                if isinstance(axis, DataPattern):
                    raise AxisError(
                        "[antiperiod] cannot be called with DataPattern axis"
                    )
                else:
                    is_smallestperiod = False
                    is_oneperiod = False
                    is_antiperiod = True
            elif self.extension == "oneperiod" or self.transform == "fft":
                if isinstance(axis, DataPattern):
                    raise AxisError(
                        "[oneperiod] cannot be called with DataPattern axis"
                    )
                else:
                    is_smallestperiod = False
                    is_oneperiod = True
                    is_antiperiod = False
            elif self.extension in operation_list:
                # Remove periodicities in case of DataPattern otherwise operations can be applied on periodic signals
                is_smallestperiod = not self.is_pattern
                is_oneperiod = False
                is_antiperiod = False
            # Ignore symmetries if fft axis
            elif self.name == "freqs" or self.name == "wavenumber":
                is_smallestperiod = True
                is_oneperiod = False
                is_antiperiod = False
            else:
                if self.input_data is not None and not self.is_step:
                    # Check if symmetries need to be reconstructed to match input_data
                    axis_values = axis.get_values(
                        is_smallestperiod=True,
                        operation=self.operation,
                        is_real=is_real,
                    )
                    if min(self.input_data) >= min(axis_values) and max(
                        self.input_data
                    ) <= max(axis_values):
                        is_smallestperiod = True
                        is_oneperiod = False
                        is_antiperiod = False
                    else:
                        axis_values = axis.get_values(
                            is_oneperiod=True,
                            operation=self.operation,
                            is_real=is_real,
                        )
                        if min(self.input_data) >= min(axis_values) and max(
                            self.input_data
                        ) <= max(axis_values):
                            is_smallestperiod = False
                            is_oneperiod = True
                            is_antiperiod = False
                            self.extension = "oneperiod"
                        else:
                            is_smallestperiod = False
                            is_oneperiod = False
                            is_antiperiod = False
                            if not self.is_pattern:
                                self.extension = "interval"
                elif self.transform == "ifft":  # Ignore symmetries in ifft case
                    is_smallestperiod = True
                    is_oneperiod = False
                    is_antiperiod = False
                else:
                    is_smallestperiod = False
                    is_oneperiod = False
                    is_antiperiod = False
            # Get original values of the axis including unit and normalizations
            # Store before normalization/operation
            if (
                self.unit != self.corr_unit
                and self.unit != "SI"
                or self.operation is not None
            ):
                self.corr_values = np.array(
                    axis.get_values(
                        is_oneperiod=is_oneperiod,
                        is_antiperiod=is_antiperiod,
                        is_smallestperiod=is_smallestperiod,
                    )
                )
            # Prepare unit
            # if self.corr_unit is None:
            #     self.corr_unit = self.unit
            values = axis.get_values(
                is_oneperiod=is_oneperiod,
                is_antiperiod=is_antiperiod,
                is_smallestperiod=is_smallestperiod,
                unit=self.unit,
                operation=self.operation,
                is_real=is_real,
                corr_unit=self.corr_unit,
            )

            # Rebuild symmetries in fft case
            if self.transform == "fft":
                if "period" in axis.symmetries:
                    if axis.name != "time":
                        values = values * axis.symmetries["period"]
                elif "antiperiod" in axis.symmetries:
                    if axis.name != "time":
                        values = values * axis.symmetries["antiperiod"] / 2
            # Rebuild symmetries in ifft case
            if self.transform == "ifft":
                if self.extension not in [
                    "smallestperiod",
                    "oneperiod",
                    "antiperiod",
                    "max",
                    "min",
                    "sum",
                    "mean",
                    "rms",
                    "rss",
                    "integrate",
                    "integrate_local",
                    "derivate",
                    "antiderivate",
                    "axis_data",
                ]:
                    values = rebuild_symmetries_axis(values, axis.symmetries)
            # Interpolate axis with input data
            if self.input_data is None:
                self.values = values
            else:
                if len(self.input_data) == 2 and self.extension != "axis_data":
                    indices = [
                        i
                        for i, x in enumerate(values)
                        if x >= self.input_data[0] and x <= self.input_data[-1]
                    ]
                    if self.indices is None:
                        self.indices = indices
                    else:
                        indices_new = []
                        for i in self.indices:
                            if i in indices:
                                indices_new.append(i)
                        self.indices = indices_new
                    self.input_data = None
                else:
                    self.values = values
            if self.indices is not None:
                if isinstance(self.indices[0], str):  # N largest
                    N = int(self.indices[0])
                    # Sort values
                    if hasattr(axis, "sort_indices") and axis.sort_indices is not None:
                        self.indices = axis.sort_indices[:N]
                    else:
                        self.indices = np.argsort(values)[::-1][:N].tolist()
                self.values = values[self.indices]
                if self.extension in operation_list:
                    self.indices = None
