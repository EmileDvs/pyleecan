# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataLinspace.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

import numpy as np

from ..Functions.Load.import_class import import_class as _pyleecan_import_class
from ..Functions.SciDataTool import AxisError, NormError
from ..Functions.SciDataTool.conversions import convert
from ..Functions.SciDataTool.symmetries import rebuild_symmetries_axis
from .data import Data
from .norm_vector import NormVector


@dataclass(eq=False)
class DataLinspace(Data):
    """Class for axes defined as linspaces

    Attributes
    ----------
    initial : float or None
        First value
        Default: None
    final : float or None
        Last value
        Default: None
    step : float or None
        Step
        Default: None
    number : int or None
        Number of steps
        Default: None
    include_endpoint : bool
        True if the endpoint must be included
        Default: True
    is_components : bool
        True if the axis values are strings
        Default: False
    symmetries : dict
        Dictionary of the symmetries along each axis, used to reduce storage
        Default: -1
    is_overlay : bool
        True if axis must be used to overlay curves in plots
        Default: False
    """

    initial: float | None = None
    """First value"""
    final: float | None = None
    """Last value"""
    step: float | None = None
    """Step"""
    number: int | None = None
    """Number of steps"""
    include_endpoint: bool = True
    """True if the endpoint must be included"""
    is_components: bool = False
    """True if the axis values are strings"""
    symmetries: dict[str, Any] = field(default_factory=dict)
    """Dictionary of the symmetries along each axis, used to reduce storage"""
    is_overlay: bool = False
    """True if axis must be used to overlay curves in plots"""

    # Inlined from Methods.SciDataTool.DataLinspace.get_axis_periodic
    def get_axis_periodic(self, Nper, is_aper=False):
        """Returns the vector 'axis' taking symmetries into account.

        Parameters
        ----------
        self: DataLinspace
            a DataLinspace object
        Nper: int
            number of periods
        is_antiperiod: bool
            return values on a semi period (only for antiperiodic signals)

        Returns
        -------
        New_axis: DataLinspace
            Axis with requested (anti-)periodicities
        """

        # Dynamic import to avoid loop
        DataLinspace = _pyleecan_import_class("pyleecan.Classes", "DataLinspace")

        try:
            # Reduce axis to the given periodicity
            Nper = Nper * 2 if is_aper else Nper
            values = self.get_values()
            N = self.get_length()

            if N % Nper != 0:
                raise AxisError(
                    "length of axis is not divisible by the number of periods"
                )
            values_per = values[: int(N / Nper)]
            for norm in self.normalizations.values():
                if isinstance(norm, NormVector):
                    norm.vector = norm.vector[: int(N / Nper)]

            if is_aper:
                sym = "antiperiod"
            else:
                sym = "period"

            if Nper == 1 and sym == "period":
                symmetries = {}
            else:
                symmetries = {sym: Nper}

            New_axis = DataLinspace(
                initial=self.initial,
                final=values_per[-1],
                number=int(N / Nper),
                include_endpoint=True,
                name=self.name,
                unit=self.unit,
                symmetries=symmetries,
                normalizations=self.normalizations.copy(),
                is_components=self.is_components,
                symbol=self.symbol,
            )

        except AxisError:
            # Periodicity cannot be applied, return full axis
            New_axis = self.copy()

        return New_axis

    # Inlined from Methods.SciDataTool.DataLinspace.get_length
    def get_length(
        self, is_oneperiod=False, is_antiperiod=False, is_smallestperiod=False
    ):
        """Returns the length of the axis taking symmetries into account.
        Parameters
        ----------
        self: DataLinspace
            a DataLinspace object
        is_oneperiod: bool
            return values on a single period
        is_antiperiod: bool
            return values on a semi period (only for antiperiodic signals)
        Returns
        -------
        Length of axis
        """

        if self.number is None:
            N = round((self.final - self.initial + self.step) / self.step)
        else:
            N = self.number

        # Rebuild symmetries
        if is_smallestperiod:
            return N
        elif is_antiperiod:
            if "antiperiod" in self.symmetries:
                return N
            else:
                raise AxisError("axis has no antiperiodicity")
        elif is_oneperiod:
            if "antiperiod" in self.symmetries:
                return N * 2
            elif "period" in self.symmetries:
                return N
            else:
                return N
        else:
            if "antiperiod" in self.symmetries:
                return N * self.symmetries["antiperiod"]
            elif "period" in self.symmetries:
                return N * self.symmetries["period"]
            else:
                return N

    # Inlined from Methods.SciDataTool.DataLinspace.get_periodicity
    def get_periodicity(self):
        """Gives periodicity of the axis.
        Parameters
        ----------
        self: DataLinspace
            a DataLinspace object
        Returns
        -------
        per, is_antiper
        """

        per = 1
        is_antiper = False

        if "antiperiod" in self.symmetries:
            if self.symmetries["antiperiod"] > 1:
                per = self.symmetries["antiperiod"]
                is_antiper = True
        elif "period" in self.symmetries:
            if self.symmetries["period"] > 1:
                per = self.symmetries["period"]

        return (per, is_antiper)

    # Inlined from Methods.SciDataTool.DataLinspace.get_values
    def get_values(
        self,
        unit="SI",
        is_oneperiod=False,
        is_antiperiod=False,
        is_smallestperiod=False,
        normalization=None,
        operation=None,
        is_real=True,
        corr_unit=None,
        is_full=False,
    ):
        """Returns the vector 'axis' by rebuilding the linspace, symmetries and unit included.
        Parameters
        ----------
        self: DataLinspace
            a DataLinspace object
        unit: str
            requested unit
        is_oneperiod: bool
            return values on a single period
        is_antiperiod: bool
            return values on a semi period (only for antiperiodic signals)
        is_smallestperiod: bool
            return values on smallest available period
        normalization: str
            name of normalization to use
        operation: str
            name of the operation (e.g. "freqs_to_time")
        Returns
        -------
        Vector of axis values
        """

        if unit != "SI" and unit != self.unit:
            if unit in self.normalizations and normalization is None:
                normalization = unit
                unit = "SI"

        initial = self.initial
        if self.number == None:
            final = self.final
            number = (final - initial + self.step) / self.step
        elif self.final == None:
            number = self.number
            final = self.initial + (number - 1) * self.step
        else:
            number = self.number
            final = self.final
        values = np.linspace(
            initial, final, int(number), endpoint=self.include_endpoint
        )

        norm_vector = None

        # Ignore symmetries if fft axis
        if self.name == "freqs" or self.name == "wavenumber":
            is_smallestperiod = True

        # Rebuild symmetries
        if is_smallestperiod:
            pass
        elif is_antiperiod:
            if "antiperiod" in self.symmetries:
                pass
            else:
                raise AxisError("axis has no antiperiodicity")
        elif is_oneperiod:
            if "antiperiod" in self.symmetries:
                nper = self.symmetries["antiperiod"]
                self.symmetries["antiperiod"] = 2
                values = rebuild_symmetries_axis(values, self.symmetries)
                self.symmetries["antiperiod"] = nper
            elif "period" in self.symmetries:
                pass
            else:
                pass
        else:
            values = rebuild_symmetries_axis(values, self.symmetries)
            if (
                normalization is not None
                and normalization in self.normalizations
                and isinstance(self.normalizations[normalization], NormVector)
            ):
                norm_vector = self.normalizations[normalization].vector.copy()
                self.normalizations[normalization].vector = rebuild_symmetries_axis(
                    norm_vector, self.symmetries
                )

        # fft/ifft
        if operation is not None:
            module = import_module("pyleecan.Functions.SciDataTool.conversions")
            func = getattr(module, operation)  # Conversion function
            values = np.array(func(values, is_real=is_real))
            if is_full and (self.name == "freqs" or self.name == "wavenumber"):
                if "period" in self.symmetries:
                    if self.name != "time":
                        values = values * self.symmetries["period"]
                elif "antiperiod" in self.symmetries:
                    if self.name != "time":
                        values = values * self.symmetries["antiperiod"] / 2

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

        if norm_vector is not None:
            self.normalizations[normalization].vector = norm_vector

        return values

    # Inlined from Methods.SciDataTool.DataLinspace.has_period
    def has_period(self):
        """Indicates if an axis has symmetries.
        Parameters
        ----------
        self: DataLinspace
            a DataLinspace object
        Returns
        -------
        Boolean
        """
        answer = False

        if "antiperiod" in self.symmetries:
            if self.symmetries["antiperiod"] > 1:
                answer = True
        elif "period" in self.symmetries:
            if self.symmetries["period"] > 1:
                answer = True

        return answer
