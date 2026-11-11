# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Data1D.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

import numpy as np

from ..Functions_new.SciDataTool.conversions import convert
from ..Functions_new.SciDataTool.symmetries import rebuild_symmetries_axis
from ._error import AxisError, NormError
from ._import import import_class
from .data import Data
from .norm_vector import NormVector


@dataclass(eq=False)
class Data1D(Data):
    """Class for axes defined as vectors

    Attributes
    ----------
    values : ndarray or None
        List or ndarray of the axis values
        Default: None
    is_components : bool
        True if the axis values are strings
        Default: False
    symmetries : dict
        Dictionary of the symmetries along each axis, used to reduce storage
        Default: -1
    is_overlay : bool
        True if axis must be used to overlay curves in plots
        Default: False
    delimiter : str or None
        Character used to separate attributes in string case (e.g. "r=0, stator, radial")
        Default: None
    sort_indices : list or None
        List of indices to use to sort axis
        Default: []
    filter : dict or None
        Dict of filter keys
        Default: {}
    char_to_rm : list or None
        List of characters to remove in filter table
        Default: []
    """

    values: np.ndarray | None = None
    """List or ndarray of the axis values"""
    is_components: bool = False
    """True if the axis values are strings"""
    symmetries: dict[str, Any] = field(default_factory=dict)
    """Dictionary of the symmetries along each axis, used to reduce storage"""
    is_overlay: bool = False
    """True if axis must be used to overlay curves in plots"""
    delimiter: str | None = None
    """Character used to separate attributes in string case (e.g. "r=0, stator, radial")"""
    sort_indices: list[Any] | None = field(default_factory=list)
    """List of indices to use to sort axis"""
    filter: dict[str, Any] | None = field(default_factory=dict)
    """Dict of filter keys"""
    char_to_rm: list[Any] | None = field(default_factory=list)
    """List of characters to remove in filter table"""

    # Inlined from Methods.SciDataTool.Data1D.check_filter
    def check_filter(self):
        """Check if filter is correctly defined
        Parameters
        ----------
        self: Data1D
            a Data1D object
        Returns
        -------
        keys: list
            list of filter keys in same order as in values
        """
        keys = []
        for i, value in enumerate(self.values):
            items = value.split(self.delimiter)
            if len(items) != len(self.filter.keys()):
                raise AxisError("Filter is not correctly defined")
            for item in items:
                is_match = False
                for key in self.filter:
                    if item in self.filter[key]:
                        is_match = True
                        if i == 0:
                            keys.append(key)
                if not is_match:
                    raise AxisError("Missing item in filter: " + item)

        return keys

    # Inlined from Methods.SciDataTool.Data1D.get_axis_periodic
    def get_axis_periodic(self, Nper, is_aper=False):
        """Returns the vector 'axis' taking symmetries into account.

        Parameters
        ----------
        self: Data1D
            a Data1D object
        Nper: int
            number of periods
        is_aper: bool
            return values on a semi period (only for antiperiodic signals)

        Returns
        -------
        New_axis: Data1D
            Axis with requested (anti-)periodicities
        """

        # Dynamic import to avoid loop
        Data1D = import_class("Data1D")

        try:
            # Reduce axis to the given periodicity
            Nper = Nper * 2 if is_aper else Nper
            values = self.values
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

            New_axis = Data1D(
                values=values_per,
                name=self.name,
                unit=self.unit,
                symmetries=symmetries,
                normalizations=self.normalizations,
                is_components=self.is_components,
                symbol=self.symbol,
            )

        except AxisError:
            # Periodicity cannot be applied, return full axis
            New_axis = self.copy()

        return New_axis

    # Inlined from Methods.SciDataTool.Data1D.get_filter
    def get_filter(self, filter_dict):
        """Get filtering indices
        Parameters
        ----------
        self: Data1D
            a Data1D object
        filter_dict: dict
            a dict of the values to filter (keep values defined in filter_dict)
        Returns
        -------
        indices: list
            list of indices to use to get corresponding filter
        """

        # Check that keys in filter_dict are correctly defined in self.filter
        if len(filter_dict.keys()) != len(self.filter.keys()):
            raise AxisError("Filter key not defined in Data1D.filter")
        for key in filter_dict:
            if key not in self.filter:
                raise AxisError("Filter key not defined in Data1D.filter")

        # Prepare filtering keys in correct order
        keys = self.check_filter()

        indices = []
        for i, value in enumerate(self.values):
            items = value.split(self.delimiter)
            nb_match = 0
            for j, item in enumerate(items):
                if item in filter_dict[keys[j]]:
                    nb_match += 1
            if nb_match == len(keys):
                indices.append(i)

        return indices

    # Inlined from Methods.SciDataTool.Data1D.get_length
    def get_length(
        self, is_oneperiod=False, is_antiperiod=False, is_smallestperiod=False
    ):
        """Returns the length of the axis taking symmetries into account.
        Parameters
        ----------
        self: Data1D
            a Data1D object
        is_oneperiod: bool
            return values on a single period
        is_antiperiod: bool
            return values on a semi period (only for antiperiodic signals)
        Returns
        -------
        Length of axis
        """
        N = len(self.values)
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

    # Inlined from Methods.SciDataTool.Data1D.get_periodicity
    def get_periodicity(self):
        """Gives periodicity of the axis.
        Parameters
        ----------
        self: Data1D
            a Data1D object
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

    # Inlined from Methods.SciDataTool.Data1D.get_values
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
        """Returns the vector 'axis' taking symmetries into account.
        Parameters
        ----------
        self: Data1D
            a Data1D object
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

        values = self.values
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
            module = import_module("pyleecan.Functions_new.SciDataTool.conversions")
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

    # Inlined from Methods.SciDataTool.Data1D.has_period
    def has_period(self):
        """Indicates if an axis has symmetries.
        Parameters
        ----------
        self: Data1D
            a Data1D object
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

    # Inlined from Methods.SciDataTool.Data1D.to_linspace
    def to_linspace(self):
        """Tests if values are a linspace and returns a DataLinspace (or Data1D if not possible)
        Parameters
        ----------
        self: Data1D
            a Data1D object
        Returns
        -------
        DataLinspace or Data1D
        """

        # Dynamic import to avoid loop
        DataLinspace = import_class("DataLinspace")

        values = self.values
        number = values.size

        if (
            number > 1
            and values.dtype.kind not in {"U", "S"}
            and np.allclose(
                values,
                np.linspace(values[0], values[-1], number, endpoint=True),
                rtol=1e-5,
                atol=1e-8,
                equal_nan=False,
            )
        ):
            New_axis = DataLinspace(
                initial=values[0],
                final=values[-1],
                number=number,
                include_endpoint=True,
                name=self.name,
                unit=self.unit,
                symmetries=self.symmetries,
                normalizations=self.normalizations.copy(),
                is_components=self.is_components,
                symbol=self.symbol,
            )
        else:
            New_axis = self.copy()

        return New_axis
