# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataPattern.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

import numpy as np

from ..Functions.SciDataTool import NormError
from ..Functions.SciDataTool.conversions import convert
from .data import Data


@dataclass(eq=False)
class DataPattern(Data):
    """Class for axes defined as vectors

    Attributes
    ----------
    rebuild_indices : list or None
        Indices to rebuild complete axis
        Default: []
    unique_indices : list or None
        Indices which were taken from complete axis
        Default: []
    is_step : bool
        True if the axis is defined by step
        Default: True
    values : ndarray or None
        List or ndarray of the axis values
        Default: None
    is_components : bool
        True if the axis values are strings
        Default: False
    symmetries : dict
        Dictionary of the symmetries along each axis, used to reduce storage
        Default: -1
    values_whole : ndarray or None
        Complete axis
        Default: None
    is_overlay : bool
        True if axis must be used to overlay curves in plots
        Default: False
    """

    rebuild_indices: list[Any] | None = field(default_factory=list)
    """Indices to rebuild complete axis"""
    unique_indices: list[Any] | None = field(default_factory=list)
    """Indices which were taken from complete axis"""
    is_step: bool = True
    """True if the axis is defined by step"""
    values: np.ndarray | None = None
    """List or ndarray of the axis values"""
    is_components: bool = False
    """True if the axis values are strings"""
    symmetries: dict[str, Any] = field(default_factory=dict)
    """Dictionary of the symmetries along each axis, used to reduce storage"""
    values_whole: np.ndarray | None = None
    """Complete axis"""
    is_overlay: bool = False
    """True if axis must be used to overlay curves in plots"""

    # Inlined from Methods.SciDataTool.DataPattern.get_length
    def get_length(self, is_pattern=False, is_smallestperiod=False):
        """Returns the length of the axis taking symmetries into account.
        Parameters
        ----------
        self: DataPattern
            a DataPattern object
        is_pattern: bool
            return length of pattern
        Returns
        -------
        Length of axis
        """
        if is_smallestperiod:
            return len(self.values)
        elif is_pattern:
            return len(self.values)
        else:
            return len(self.rebuild_indices)

    # Inlined from Methods.SciDataTool.DataPattern.get_values
    def get_values(
        self,
        unit="SI",
        is_oneperiod=False,
        is_antiperiod=False,
        is_smallestperiod=False,
        is_pattern=False,
        normalization=None,
        operation=None,
        is_real=True,
        corr_unit=None,
        is_full=False,
    ):
        """Returns the vector 'axis' taking symmetries into account.
        Parameters
        ----------
        self: DataPattern
            a DataPattern object
        unit: str
            requested unit
        is_oneperiod: bool
            return values on a single period (unused here)
        is_antiperiod: bool
            return values on a semi period (unused here)
        is_smallestperiod: bool
            return values on smallest available period (pattern here => is_pattern)
        is_pattern: bool
            return values on smallest available pattern
        normalization: str
            name of normalization to use
        operation: str
            name of the operation (e.g. "freqs_to_time")
        Returns
        -------
        Vector of axis values
        """
        values = self.values

        # Rebuild pattern
        if is_smallestperiod or is_pattern:
            pass
        else:
            if self.values_whole is not None:
                values = self.values_whole
            else:
                values = values[self.rebuild_indices]

        # fft/ifft
        if operation is not None:
            module = import_module("pyleecan.Functions.SciDataTool.conversions")
            func = getattr(module, operation)  # Conversion function
            values = np.array(func(values, is_real=is_real))

        if unit != "SI" and unit != self.unit:
            if unit in self.normalizations and normalization is None:
                normalization = unit
                unit = "SI"

        # Normalization
        if normalization is not None:
            if normalization in self.normalizations:
                if (
                    self.normalizations[normalization].unit == "SI"
                    or self.normalizations[normalization].unit == self.unit
                ):
                    # Axis is in the correct unit for the normalization
                    values = self.normalizations[normalization].normalize(values)
                else:
                    raise NormError("Normalization is not available in this unit")
            else:
                raise NormError("Normalization is not available")

        # Unit conversion
        if unit != "SI" and unit != self.unit:
            if corr_unit is not None:
                values = convert(values, corr_unit, unit)
            else:
                values = convert(values, self.unit, unit)

        return values

    # Inlined from Methods.SciDataTool.DataPattern.has_period
    def has_period(self):
        """Indicates if an axis has symmetries.
        Parameters
        ----------
        self: DataPattern
            a DataPatternobject
        Returns
        -------
        Boolean
        """

        return False
