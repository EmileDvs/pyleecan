# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataND.csv
"""Generated experimental dataclass; do not edit by hand."""

import csv
import os
from dataclasses import dataclass, field
from typing import Any

import imageio
import matplotlib.pyplot as plt
import numpy as np

from ..Functions.SciDataTool import (
    AxisError,
    NormError,
    UnitError,
    axes_dict_transformation,
    rev_axes_dict,
)
from ..Functions.SciDataTool.change_referential import (
    change_referential_spectrum,
    change_referential_waveform,
)
from ..Functions.SciDataTool.conversions import (
    convert,
    get_unit_derivate,
    get_unit_integrate,
    to_dB,
    to_dBA,
    to_noct,
)
from ..Functions.SciDataTool.conversions import convert as convert_unit
from ..Functions.SciDataTool.derivation_integration import (
    antiderivate,
    derivate,
    integrate,
    integrate_local,
    integrate_local_pattern,
)
from ..Functions.SciDataTool.fft_functions import comp_fftn, comp_ifftn
from ..Functions.SciDataTool.filter_spectral_leakage import (
    filter_spectral_leakage as filter_spectral_leakage_fct,
)
from ..Functions.SciDataTool.fix_axes_order import fix_axes_order
from ..Functions.SciDataTool.interpolations import (
    get_common_base,
    get_interpolation,
    get_interpolation_step,
)
from ..Functions.SciDataTool.omp import comp_undersampled_axe, omp
from ..Functions.SciDataTool.parser import read_input_strings
from ..Functions.SciDataTool.Plot import (
    COLORS,
    PARAM_2D,
    PARAM_3D,
    axes_dict,
    fft_dict,
    ifft_dict,
    norm_dict,
    unit_dict,
)
from ..Functions.SciDataTool.Plot.plot_2D import plot_2D
from ..Functions.SciDataTool.Plot.plot_3D import plot_3D
from ..Functions.SciDataTool.Plot.plot_4D import plot_4D
from ..Functions.SciDataTool.sum_mean import (
    my_mean,
    my_sum,
    root_mean_square,
    root_sum_square,
)
from ..Functions.SciDataTool.symmetries import rebuild_symmetries
from ..Functions.SciDataTool.symmetries import (
    rebuild_symmetries as rebuild_symmetries_fct,
)
from ._check import check_dimensions, check_var
from ._import import import_class
from .data import Data
from .data_1d import Data1D
from .norm_indices import NormIndices


@dataclass(eq=False)
class DataND(Data):
    """Abstract class for fields (time or frequency domain)

    Attributes
    ----------
    axes : [Data] or None
        List of the Data1D objects corresponding to the axes
        Default: None
    FTparameters : dict
        Tunable parameters for the Fourier Transforms
        Default: -1
    values : ndarray or None
        Values of the field
        Default: None
    is_real : bool
        To indicate if the signal is real (use only positive frequencies)
        Default: True
    """

    axes: list[Data] | None = None
    """List of the Data1D objects corresponding to the axes"""
    FTparameters: dict[str, Any] = field(default_factory=dict)
    """Tunable parameters for the Fourier Transforms"""
    values: np.ndarray | None = None
    """Values of the field"""
    is_real: bool = True
    """To indicate if the signal is real (use only positive frequencies)"""

    # Inlined from Methods.SciDataTool.DataND._apply_operations
    def _apply_operations(self, values, axes_list, is_magnitude, unit, corr_unit):
        """Returns the values of the field transformed or converted
        Parameters
        ----------
        self: Data
            a Data object
        values: ndarray
            array of the field
        Returns
        -------
        values: ndarray
            values of the field
        """

        # Take magnitude before summing
        if is_magnitude and "dB" not in unit:
            values = np.abs(values)

        # Apply sums, means, etc
        for axis_requested in axes_list:
            # Get axis data
            ax_val = axis_requested.values
            extension = axis_requested.extension
            index = axis_requested.index
            if axis_requested.is_pattern:
                Nper, is_aper = None, None
            else:
                Nper, is_aper = self.axes[index].get_periodicity()
            if axis_requested.name in ["time", "angle", "z"]:
                is_phys = True
                is_freqs = False
            elif axis_requested.name in ["freqs", "frequency"]:
                is_phys = False
                is_freqs = True
            else:
                is_phys = False
                is_freqs = False
            if axis_requested.name in ["freqs", "frequency", "wavenumber"]:
                is_fft = True
            else:
                is_fft = False
            # max over max axes
            if extension in "max":
                values = np.nanmax(values, axis=index)
            # min over max axes
            elif extension in "min":
                values = np.nanmin(values, axis=index)
            # sum over sum axes
            elif extension in "sum":
                values = my_sum(
                    values, index, Nper, is_aper, unit, is_fft, corr_unit=corr_unit
                )
            # root sum square over rss axes
            elif extension == "rss":
                values = root_sum_square(
                    values,
                    ax_val,
                    index,
                    Nper,
                    is_aper,
                    is_phys,
                    unit,
                    is_fft,
                    corr_unit=corr_unit,
                )
            # mean value over mean axes
            elif extension == "mean":
                values = my_mean(values, ax_val, index, Nper, is_aper, is_phys, is_fft)
            # RMS over rms axes
            elif extension == "rms":
                values = root_mean_square(
                    values, ax_val, index, Nper, is_aper, is_phys, is_fft
                )
            # integration over integration axes
            elif extension == "integrate":
                values = integrate(values, ax_val, index, Nper, is_aper, is_phys)
            # local integration over integration axes
            elif extension == "integrate_local":
                if axis_requested.name == "z":
                    values, ax_val = integrate_local_pattern(values, ax_val, index)
                    axis_requested.values = ax_val
                else:
                    values = integrate_local(
                        values, ax_val, index, Nper, is_aper, is_phys, is_freqs
                    )
            # antiderivation over antiderivation axes
            elif extension == "antiderivate":
                values = antiderivate(
                    values, ax_val, index, Nper, is_aper, is_phys, is_freqs
                )
            # derivation over derivation axes
            elif extension == "derivate":
                values = derivate(
                    values, ax_val, index, Nper, is_aper, is_phys, is_freqs
                )

        if is_magnitude and "dB" in unit:  # Correction for negative/small dB/dBA
            values[values < 2] = 0
            values = np.abs(values)

        return values

    # Inlined from Methods.SciDataTool.DataND._comp_axes
    def _comp_axes(self, axes_list):
        """Completes the RequestedAxis objects in axes_list.
        Parameters
        ----------
        self: Data
            a Data object
        axes_list: list
            a list of RequestedAxis objects
        Returns
        -------
        list of RequestedAxis objects + transformations
        """

        transforms = []
        # Check if the requested axis is defined in the Data object
        for axis_requested in axes_list[:]:
            axis_name = axis_requested.name
            for index, axis in enumerate(self.axes):
                if axis.name == axis_name:
                    axis_requested.index = index
                    axis_requested.corr_name = axis_name
                    axis_requested.corr_unit = axis.unit
                    axis_requested.is_components = axis.is_components
                    if axis_name in rev_axes_dict.keys():
                        axis_requested.transform = "fft_axis"
                        transforms.append("fft")
            if axis_requested.index is None:
                # Check if requested axis is in correspondance dicts
                if axis_name in axes_dict_transformation.keys():
                    for index, axis in enumerate(self.axes):
                        if axis.name == axes_dict_transformation[axis_name][0]:
                            axis_requested.corr_name = axes_dict_transformation[
                                axis_name
                            ][0]
                            axis_requested.corr_unit = axes_dict_transformation[
                                axis_name
                            ][2]
                            axis_requested.is_components = axis.is_components
                            axis_requested.operation = (
                                axes_dict_transformation[axis_name][0]
                                + "_to_"
                                + axis_name
                            )
                            axis_requested.transform = axes_dict_transformation[
                                axis_name
                            ][1]
                            transforms.append(axes_dict_transformation[axis_name][1])
                            axis_requested.index = index
                    if axis_requested.index is None:
                        # Axis does not exist and is ignored
                        axes_list.remove(axis_requested)
                elif axis_name in rev_axes_dict.keys():
                    for index, axis in enumerate(self.axes):
                        if axis.name == rev_axes_dict[axis_name][0]:
                            axis_requested.corr_name = rev_axes_dict[axis_name][0]
                            axis_requested.corr_unit = rev_axes_dict[axis_name][2]
                            axis_requested.is_components = axis.is_components
                            axis_requested.operation = (
                                rev_axes_dict[axis_name][0] + "_to_" + axis_name
                            )
                            axis_requested.transform = rev_axes_dict[axis_name][1]
                            transforms.append(rev_axes_dict[axis_name][1])
                            axis_requested.index = index
                    if axis_requested.index is None:
                        # Axis does not exist and is ignored
                        axes_list.remove(axis_requested)
                else:
                    # Axis does not exist and is ignored
                    axes_list.remove(axis_requested)
        # Extract the requested axes (symmetries + unit)
        for axis_requested in axes_list:
            axis_requested.get_axis(
                self.axes[axis_requested.index], is_real=self.is_real
            )
        return axes_list, transforms

    # Inlined from Methods.SciDataTool.DataND._convert
    def _convert(self, values, unit, is_norm, is_squeeze, axes_list):
        """Returns the values of the field transformed or converted.
        Parameters
        ----------
        self: Data
            a Data object
        values: ndarray
            array of the field
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        Returns
        -------
        values: ndarray
            values of the field
        """

        if is_squeeze:
            values = np.squeeze(values)

        if unit == self.unit or unit == "SI":
            if is_norm:
                try:
                    values = self.normalizations["ref"].normalize(values)
                except Exception:
                    raise NormError("Reference value not specified for normalization")
        elif unit == "dB":
            ref_value = 1.0
            if "ref" in self.normalizations:
                ref_value *= self.normalizations["ref"].ref
            values = to_dB(np.abs(values), self.unit, ref_value)
        elif unit == "dBA":
            ref_value = 1.0
            if "ref" in self.normalizations:
                ref_value *= self.normalizations["ref"].ref
            is_match = False
            for axis in axes_list:
                if axis.name == "freqs" or axis.corr_name == "freqs":
                    if axis.corr_values is not None and axis.unit not in [
                        "SI",
                        axis.corr_unit,
                    ]:
                        axis_values = axis.corr_values
                    else:
                        axis_values = axis.values
                    index = axis.index
                    values = np.apply_along_axis(
                        to_dBA, index, values, axis_values, self.unit, ref_value
                    )
                    is_match = True
                elif axis.name == "frequency":
                    if axis.corr_values is None:
                        axis_values = axis.values
                    else:
                        axis_values = axis.corr_values
                    index = axis.index
                    values = np.apply_along_axis(
                        to_dBA, index, values, axis_values, self.unit, ref_value
                    )
                    is_match = True
            if not is_match:
                axis_names = [axis.name for axis in self.axes]
                if "speed" in axis_names and "order" in axis_names:
                    freqs = self._get_freqs()
                    freqs = freqs.ravel("C")
                    shape = values.shape
                    values = values.reshape(freqs.shape + shape[2:])
                    values = np.apply_along_axis(
                        to_dBA, 0, values, freqs, self.unit, ref_value
                    )
                    values = values.reshape(shape)
                else:
                    raise UnitError(
                        "dBA conversion only available for fft with frequencies"
                    )
        elif unit in self.normalizations:
            values = self.normalizations.get(unit).normalize(values)
        else:
            values = convert_unit(values, self.unit, unit)

        return values

    # Inlined from Methods.SciDataTool.DataND._extract_slices
    def _extract_slices(self, values, axes_list):
        """Returns the values of the field (with symmetries and transformations).
        Parameters
        ----------
        self: Data
            a Data object
        values: ndarray
            array of the field
        axes_list: list
            a list of RequestedAxis objects
        Returns
        -------
        values: ndarray
            values of the field
        """

        axes_dict_other = {}

        # Extract the slices of the field
        for index, axis in enumerate(self.axes):
            is_match = False
            for axis_requested in axes_list:
                if axis.name == axis_requested.corr_name:
                    is_match = True
                    if (
                        axis_requested.indices is not None
                        and axis_requested.transform != "fft"
                    ):
                        values = np.take(values, axis_requested.indices, axis=index)
            if not is_match:  # Axis was not specified -> take slice at the first value
                axes_dict_other[axis.name] = [axis.get_values()[0], axis.unit]
                values = np.take(values, [0], axis=index)
        return values, axes_dict_other

    # Inlined from Methods.SciDataTool.DataND._extract_slices_fft
    def _extract_slices_fft(self, values, axes_list):
        """Returns the values of the field (with symmetries and transformations).
        Parameters
        ----------
        self: Data
            a Data object
        values: ndarray
            array of the field
        axes_list: list
            a list of RequestedAxis objects
        Returns
        -------
        values: ndarray
            values of the field
        """

        # Extract the slices of the field
        for index, axis in enumerate(self.axes):
            is_match = False
            for axis_requested in axes_list:
                if axis.name == axis_requested.corr_name:
                    is_match = True
                    if (
                        axis_requested.indices is not None
                        and axis_requested.transform == "fft"
                    ):
                        values = np.take(values, axis_requested.indices, axis=index)
            if not is_match:  # Axis was not specified -> take slice at the first value
                values = np.take(values, [0], axis=index)
        return values

    # Inlined from Methods.SciDataTool.DataND._get_field
    def _get_field(self, axes_list):
        """Returns the values of the field (with symmetries and sums).
        Parameters
        ----------
        self: Data
            a Data object
        axes_list: list
            a list of RequestedAxis objects
        Returns
        -------
        values: ndarray
            values of the field
        """

        values = self.values
        for axis_requested in axes_list:
            # Rebuild symmetries when needed
            axis_symmetries = self.axes[axis_requested.index].symmetries

            if axis_requested.is_pattern and (
                axis_requested.transform == "fft"
                or axis_requested.extension
                in [
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
                ]
                or axis_requested.indices not in [None, []]
                and max(axis_requested.indices) >= values.shape[axis_requested.index]
            ):
                # DataPattern case where all values are requested
                values = np.take(
                    values, axis_requested.rebuild_indices, axis_requested.index
                )
            elif axis_requested.transform == "fft" and "antiperiod" in axis_symmetries:
                # FFT case if axis is anti-periodic
                nper = axis_symmetries["antiperiod"]
                axis_symmetries["antiperiod"] = 2
                values = rebuild_symmetries(
                    values, axis_requested.index, axis_symmetries
                )
                axis_symmetries["antiperiod"] = nper
            elif (
                axis_requested.indices is not None
                and max(axis_requested.indices) > values.shape[axis_requested.index]
            ):
                # Slicing case where requested indices are among other periods
                values = rebuild_symmetries(
                    values, axis_requested.index, axis_symmetries
                )
                self.axes[axis_requested.index].symmetries = {}

        return values

    # Inlined from Methods.SciDataTool.DataND._get_freqs
    def _get_freqs(self):
        """Returns the frequency vector or array, if available.
        Parameters
        ----------
        self: Data
            a Data object
        Returns
        -------
        freqs : frequency vector or array
        """

        axis_names = [axis.name for axis in self.axes]
        axis_norm = [list(axis.normalizations.keys()) for axis in self.axes]

        index = None
        operation = None
        index_speed = None
        index_order = None

        if "freqs" in axis_names:
            index = axis_names.index("freqs")
        elif "frequency" in axis_names:
            index = axis_names.index("frequency")
        elif "time" in axis_names:
            index = axis_names.index("frequency")
            operation = "time_to_freqs"
        elif "speed" in axis_names and "order" in axis_names:
            index_speed = axis_names.index("speed")
            index_order = axis_names.index("order")
            is_norm = False
        else:
            for i, norm in enumerate(axis_norm):
                if "speed" in norm:
                    index_speed = i
                    is_norm = True
            if index_speed is not None and "order" in axis_names:
                index_order = axis_names.index("order")
            else:
                raise AxisError("Cannot compute frequencies from available axes")

        if index is not None:
            freqs = self.get_axes()[index].get_values(operation=operation)
        else:  # f = speed * 60 / order
            if is_norm:
                normalization = "speed"
            else:
                normalization = None
            speed = self.get_axes()[index_speed].get_values(normalization=normalization)
            order_strings = self.get_axes()[index_order].get_values().tolist()
            orders = np.array(
                [int(s.split(";")[0].replace("H", "")) for s in order_strings]
            )
            os, so = np.meshgrid(orders, speed)
            freqs = so * 60 / os

        return freqs

    # Inlined from Methods.SciDataTool.DataND._interpolate
    def _interpolate(self, values, axes_list):
        """Returns the values of the field interpolated over the axes values.
        Parameters
        ----------
        self: Data
            a Data object
        values: ndarray
            array of the field
        axes_list: list
            a list of RequestedAxis objects
        Returns
        -------
        values: ndarray
            values of the field
        """

        # Interpolate over axis values
        for axis_requested in axes_list:
            if axis_requested.input_data is not None:
                if axis_requested.is_step:
                    values = get_interpolation_step(
                        values,
                        axis_requested.values,
                        axis_requested.input_data,
                        axis_requested.index,
                    )
                else:
                    values = get_interpolation(
                        values,
                        axis_requested.values,
                        axis_requested.input_data,
                        axis_requested.index,
                    )
                # Store new axis data into axis_requested.values
                axis_requested.values = axis_requested.input_data
        return values

    # Inlined from Methods.SciDataTool.DataND._rebuild_symmetries
    def _rebuild_symmetries(
        self,
        values,
        axes_list,
    ):
        """Reconstructs the field of a Data object taking symmetries into account
        Parameters
        ----------
        self: Data
            a Data object
        values: ndarray
            ndarray of a field
        axes_list: list
            a list of RequestedAxis objects
        Returns
        -------
        ndarray of the reconstructed field
        """

        for axis in axes_list:
            if (
                axis.transform != "fft"
                and axis.is_pattern
                and (
                    axis.extension
                    not in [
                        "max",
                        "min",
                        "sum",
                        "rss",
                        "mean",
                        "rms",
                        "integrate",
                        "integrate_local",
                        "derivate",
                        "smallestperiod",
                    ]
                    and axis.indices is None
                )
            ):
                values = np.take(values, axis.rebuild_indices, axis.index)
            elif axis.transform != "fft" and axis.extension in [
                "whole",
                "interval",
                "oneperiod",
                "antiperiod",
                "smallestperiod",
            ]:
                if axis.extension == "smallestperiod":
                    is_smallestperiod = True
                    is_oneperiod = False
                    is_antiperiod = False
                elif axis.extension == "antiperiod":
                    is_smallestperiod = False
                    is_oneperiod = False
                    is_antiperiod = True
                elif axis.extension == "oneperiod":
                    is_smallestperiod = False
                    is_oneperiod = True
                    is_antiperiod = False
                # Ignore symmetries if fft axis
                elif axis.name in ["freqs", "wavenumber"] or (
                    axis.transform == "ifft"
                    # and len(axis.values) != len(axis.corr_values)
                    and len(axis.values) == values.shape[axis.index]
                ):
                    is_smallestperiod = True
                    is_oneperiod = False
                    is_antiperiod = False
                else:
                    is_smallestperiod = False
                    is_oneperiod = False
                    is_antiperiod = False

                # Rebuild symmetries
                axis_symmetries = self.axes[axis.index].symmetries
                if is_oneperiod:
                    if "antiperiod" in axis_symmetries:
                        nper = axis_symmetries["antiperiod"]
                        axis_symmetries["antiperiod"] = 2
                        values = rebuild_symmetries_fct(
                            values, axis.index, axis_symmetries
                        )
                        axis_symmetries["antiperiod"] = nper
                elif not is_smallestperiod and not is_antiperiod:
                    values = rebuild_symmetries_fct(values, axis.index, axis_symmetries)
        return values

    # Inlined from Methods.SciDataTool.DataND._set_values
    def _set_values(self, value):
        """setter of values"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("values", value, "ndarray")

        # Check dimensions
        if value is not None:
            value = np.squeeze(value)
        value = check_dimensions(value, self.axes)
        self._values = value

    # Inlined from Methods.SciDataTool.DataND.change_referential
    def change_referential(
        self,
        rotation_speed,
        is_waveform,
        atol=1e-9,
        axes_list_change=[],
        arg_list=[],
        freqs_new=np.array([]),
        I1=np.array([]),
        Irf_un=np.array([]),
        sym_t_new={},
        ta_in=tuple(),
        ta_out=tuple(),
        atol_freq=1e-6,
    ):
        """Change referential of a SciDataTool DataND object

        Parameters
        ----------
        self : DataND
            a DataND object
        rotation_speed : float
            rotation speed [rpm]
        is_waveform: bool
            True to perform referential change in waveform domain (time/space) otherwise perform it in spectral domain (freqs/wavenumber)
        atol: float
            Absolute tolerance under which amplitudes are assumed to be 0
        axes_list_change : [Data]
            Axes list to be stored in referential changed DataFreq
        arg_list: list
            List of strings to call get_along
        freqs_new : ndarray
            frequencies vector in the new rotating referential
        I1 : ndarray
            Array of component indices in new spectrum
        Irf_un: ndarray
            Array of indices of unique frequency/wavenumber couples
        ta_in: tuple
            Tuple of input time/angle meshgrids
        ta_out: tuple
            Tuple of output time/angle meshgrids
        atol_freq: float
            Absolute tolerance under which frequencies are assumed to be equal

        Returns
        -------
        data_new : DataND
            a DataND object in new referential
        axes_list_change : [Data]
            Axes list to be stored in changed DataND
        arg_list: list
            List of strings to call get_along
        freqs_new : ndarray
            frequencies vector in the new rotating referential
        I1 : ndarray
            Array of component indices in new spectrum
        Irf_un: ndarray
            Array of indices of unique frequency/wavenumber couples
        ta_in: tuple
            Tuple of input time/angle meshgrids
        ta_out: tuple
            Tuple of output time/angle meshgrids

        """

        DataLinspace = import_class("DataLinspace")
        DataPattern = import_class("DataPattern")

        if is_waveform:
            DataClass = import_class("DataTime")
        else:
            DataClass = import_class("DataFreq")

        # Get axes list
        axes_list = self.get_axes()
        axes_name = [axis.name for axis in axes_list]

        if len(arg_list) == 0:
            # Get fft along frequency axis (keep other axes)
            arg_list = []
            for axis in axes_list:
                if axis.name == "time":
                    if is_waveform:
                        arg_list.append("time[oneperiod]")
                    else:
                        arg_list.append("freqs")
                elif axis.name == "angle":
                    if is_waveform:
                        arg_list.append("angle[oneperiod]")
                    else:
                        arg_list.append("wavenumber")
                elif axis.name == "z" and isinstance(axis, DataPattern):
                    arg_list.append("z[smallestpattern]")
                else:
                    arg_list.append(axis.name)

        # Referential changed is requested in waveform domain if time is in arg_list
        is_waveform = "time[oneperiod]" in arg_list

        if not is_waveform and hasattr(self, "is_real"):
            # Force non real data to get all spectrum
            is_real = self.is_real
            self.is_real = False
        else:
            is_real = True

        # Extract data from vectorfield on one period
        result = self.get_along(*arg_list, is_squeeze=False)
        values = result[self.symbol]

        if is_waveform:
            # Get axes values
            time0 = result["time"]
            angle0 = result["angle"]

            # Check requested time anti-periodicity
            is_aper_t = "antiperiod" in sym_t_new

            # Get angle periodicity on one period
            per_a, is_aper_a = axes_list[1].get_periodicity()
            per_a = int(per_a / 2) if is_aper_a else per_a

            val_new, time_new, angle_new, ta_in, ta_out = change_referential_waveform(
                values,
                time0,
                angle0,
                rotation_speed,
                is_aper_a,
                is_aper_t,
                ta_in,
                ta_out,
            )
        else:
            freqs = result["freqs"]
            wavenumber = result["wavenumber"]

            val_new, freqs_new, I1, Irf_un = change_referential_spectrum(
                freqs,
                wavenumber,
                rotation_speed,
                values,
                atol=atol,
                freqs_new=freqs_new,
                I1=I1,
                Irf_un=Irf_un,
                is_double_f0=is_real and "freqs" in axes_name,
                atol_freq=atol_freq,
            )

            if is_real:
                # Adapt spectrum amplitude
                if "time" in axes_name:
                    # Input data is DataTime, FFT has just been performed in four quadrants
                    # so all amplitudes are multiplied by 2 after restriction to positive frequencies
                    coeff = 2
                else:
                    # Input data is DataFreq, since data is a real spectrum no need to multiply again
                    # all harmonics by two
                    coeff = 1

                # Restrict spectrum to positive frequencies only and multiply amplitudes by coeff
                Ifreq_pos = freqs_new >= 0
                freqs_store = freqs_new[Ifreq_pos]
                val_new = val_new[Ifreq_pos] * coeff
                val_new[0] = val_new[0] / coeff
            else:
                freqs_store = freqs_new

        if len(axes_list_change) == 0:
            axes_list_change = []
            for axis in axes_list:
                if axis.name == "time" and is_waveform:
                    axis_new = axis.copy()
                    axis_new.symmetries = sym_t_new
                    axis_new.number = time_new.size
                    if isinstance(axis_new, DataLinspace):
                        axis_new.final = time_new[-1]
                        axis_new.include_endpoint = True
                    else:
                        axis_new.values = time0

                elif axis.name == "angle" and is_waveform:
                    axis_new = axis.copy()
                    if is_aper_a:
                        axis_new.symmetries = {"antiperiod": int(2 * per_a)}
                    else:
                        axis_new.symmetries = {"period": per_a}
                    axis_new.number = angle_new.size
                    if isinstance(axis_new, DataLinspace):
                        axis_new.final = angle_new[-1]
                        axis_new.include_endpoint = True
                    else:
                        axis_new.values = angle_new

                elif axis.name == "freqs" or (axis.name == "time" and not is_waveform):
                    axis_new = Data1D(
                        name="freqs",
                        unit="Hz",
                        values=freqs_store,
                        normalizations=axis.normalizations.copy(),
                        symmetries={},  # Don't keep time symmetries, FFT inverse requests axis_data
                    )

                elif axis.name == "wavenumber" or (
                    axis.name == "angle" and not is_waveform
                ):
                    axis_new = Data1D(
                        name="wavenumber",
                        unit="dimless",
                        values=wavenumber,
                        normalizations=axis.normalizations.copy(),
                        symmetries=axis.symmetries.copy(),
                    )

                else:
                    axis_new = axis.copy()

                axes_list_change.append(axis_new)

        data_new = DataClass(
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            axes=axes_list_change,
            values=val_new,
            normalizations=self.normalizations.copy(),
            is_real=is_real,
        )

        if not is_waveform and hasattr(self, "is_real"):
            # Reset data
            self.is_real = is_real

        return (
            data_new,
            axes_list_change,
            arg_list,
            freqs_new,
            I1,
            Irf_un,
            ta_in,
            ta_out,
        )

    # Inlined from Methods.SciDataTool.DataND.compare_along
    def compare_along(self, *args, data_list=[], unit="SI", is_norm=False):
        """Returns the ndarrays of both fields interpolated in the same axes, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        data_list: list
            list of Data objects to compare
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        Returns
        -------
        list of 1Darray of axis values, ndarrays of fields
        """
        if data_list == []:
            return self.get_along(args, unit=unit, is_norm=is_norm)
        else:
            # Extract requested axes + field values
            results = self.get_along(args, unit=unit, is_norm=is_norm)
            values = results.pop(self.symbol)
            axes_list = results.pop("axes_list")
            axes_dict_other = results.pop("axes_dict_other")
            axes = results
            data_axis_values = []
            data_values = []
            return_dict = {}
            for data in data_list:
                results = data.get_along(args, unit=unit, is_norm=is_norm)
                data_values.append(results.pop(data.symbol))
                data_axis_values.append(results)
            # Get the common bases
            common_axis_values = {}
            for axis in axes.keys():
                common_axis_values[axis] = axes[axis]
                for i, data in enumerate(data_list):
                    common_axis_values[axis] = get_common_base(
                        common_axis_values[axis], data_axis_values[i][axis]
                    )
                # Interpolate over common axis values
                values = get_interpolation(values, axes[axis], common_axis_values[axis])
                for i, data in enumerate(data_list):
                    data_values[i] = get_interpolation(
                        data_values[i],
                        data_axis_values[i][axis],
                        common_axis_values[axis],
                    )
                return_dict[axis] = common_axis_values[axis]
            # Return axis and values
            return_dict[self.symbol] = values
            return_dict["axes_list"] = axes_list
            return_dict["axes_dict_other"] = axes_dict_other
            for i, data in enumerate(data_list):
                return_dict[data.symbol + "_" + str(i)] = data_values[i]
            return return_dict

    # Inlined from Methods.SciDataTool.DataND.compare_magnitude_along
    def compare_magnitude_along(self, *args, unit="SI", data_list=[], is_norm=False):
        """Returns the ndarrays of both fields interpolated in the same axes, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        data_list: list
            list of Data objects to compare
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        Returns
        -------
        list of 1Darray of axis values, ndarrays of fields
        """
        if data_list == []:
            return self.get_magnitude_along(args, unit=unit, is_norm=is_norm)
        else:
            # Extract requested axes + field values
            results = self.get_magnitude_along(args, unit=unit, is_norm=is_norm)
            values = results.pop(self.symbol)
            axes_list = results.pop("axes_list")
            axes_dict_other = results.pop("axes_dict_other")
            axes = results
            data_axis_values = []
            data_values = []
            return_dict = {}
            for data in data_list:
                results = data.get_magnitude_along(args, unit=unit, is_norm=is_norm)
                data_values.append(results.pop(data.symbol))
                data_axis_values.append(results)
            # Get the common bases
            common_axis_values = {}
            for axis in axes.keys():
                common_axis_values[axis] = axes[axis]
                for i, data in enumerate(data_list):
                    common_axis_values[axis] = get_common_base(
                        common_axis_values[axis], data_axis_values[i][axis]
                    )
                # Interpolate over common axis values
                values = get_interpolation(values, axes[axis], common_axis_values[axis])
                for i, data in enumerate(data_list):
                    data_values[i] = get_interpolation(
                        data_values[i],
                        data_axis_values[i][axis],
                        common_axis_values[axis],
                    )
                return_dict[axis] = common_axis_values[axis]
            # Return axis and values
            return_dict[self.symbol] = values
            return_dict["axes_list"] = axes_list
            return_dict["axes_dict_other"] = axes_dict_other
            for i, data in enumerate(data_list):
                return_dict[data.symbol + "_" + str(i)] = data_values[i]
            return return_dict

    # Inlined from Methods.SciDataTool.DataND.compare_phase_along
    def compare_phase_along(self, *args, unit="SI", data_list=[], is_norm=False):
        """Returns the ndarrays of both fields interpolated in the same axes, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        data_list: list
            list of Data objects to compare
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        Returns
        -------
        list of 1Darray of axis values, ndarrays of fields
        """
        if data_list == []:
            return self.get_phase_along(args, unit=unit, is_norm=is_norm)
        else:
            # Extract requested axes + field values
            results = self.get_phase_along(args, unit=unit, is_norm=is_norm)
            values = results.pop(self.symbol)
            axes_list = results.pop("axes_list")
            axes_dict_other = results.pop("axes_dict_other")
            axes = results
            data_axis_values = []
            data_values = []
            return_dict = {}
            for data in data_list:
                results = data.get_phase_along(args, unit=unit, is_norm=is_norm)
                data_values.append(results.pop(data.symbol))
                data_axis_values.append(results)
            # Get the common bases
            common_axis_values = {}
            for axis in axes.keys():
                common_axis_values[axis] = axes[axis]
                for i, data in enumerate(data_list):
                    common_axis_values[axis] = get_common_base(
                        common_axis_values[axis], data_axis_values[i][axis]
                    )
                # Interpolate over common axis values
                values = get_interpolation(values, axes[axis], common_axis_values[axis])
                for i, data in enumerate(data_list):
                    data_values[i] = get_interpolation(
                        data_values[i],
                        data_axis_values[i][axis],
                        common_axis_values[axis],
                    )
                return_dict[axis] = common_axis_values[axis]
            # Return axis and values
            return_dict[self.symbol] = values
            return_dict["axes_list"] = axes_list
            return_dict["axes_dict_other"] = axes_dict_other
            for i, data in enumerate(data_list):
                return_dict[data.symbol + "_" + str(i)] = data_values[i]
            return return_dict

    # Inlined from Methods.SciDataTool.DataND.export_along
    def export_along(
        self,
        *args,
        is_2D=True,
        unit="SI",
        save_path=None,
        file_name=None,
        file_format="csv",
        is_multiple_files=False,
        plot_options={},
        CHAR_LIST=["$", "{", "}"],
    ):
        """Exports the sliced or interpolated version of the data, using conversions and symmetries if needed, in a file.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        file_format: str
            export format ("csv", ...)
        Returns
        -------
        a DataND object
        """

        # If args not specified, write only oneperiod/pattern
        if args == tuple():
            # Dynamic import to avoid loop
            DataPattern = import_class("DataPattern")
            arg_list = []
            for axis in self.get_axes():
                if isinstance(axis, DataPattern):
                    arg_list.append(axis.name + "[pattern]")
                else:
                    arg_list.append(axis.name + "[oneperiod]")
            args = tuple(arg_list)

        # Get requested data
        if is_2D:
            Xdata, Ydatas, title, xlabel, ylabel, legends = self.plot_2D_Data(
                *args, **plot_options, unit=unit, is_export=True
            )
            axes_list_new = []
            if "for " in title:
                slices = title.split("for ")[1]
            else:
                slices = ""
        else:
            if "is_norm" in plot_options:
                is_norm = plot_options["is_norm"]
            else:
                is_norm = False
            if "axis_data" in plot_options:
                axis_data = plot_options["axis_data"]
            else:
                axis_data = None
            is_fft = False
            for arg in args:
                if "freqs" in arg or "wavenumber" in arg:
                    is_fft = True
            if is_fft:
                results = self.get_magnitude_along(
                    *args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
            else:
                results = self.get_along(
                    *args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
            axes_list = results["axes_list"]

            # Remove slice axes
            axes_list_new = []
            slices = ""
            for axis in axes_list:
                if axis.unit == "SI":
                    axis.unit = unit_dict[axis.name]
                if len(results[axis.name]) == 1:
                    slices += axis.name + "=" + str(results[axis.name][0])
                elif isinstance(results[axis.name], str):
                    slices += axis.name + "=" + results[axis.name]
                else:
                    axes_list_new.append(axis)
            for axis in results["axes_dict_other"]:
                if slices != "":
                    slices = slices + ", "
                slices += axis + "=" + str(results["axes_dict_other"][axis][0])
            if slices != "":
                slices = "sliced at " + slices

        # Default file_name
        if file_name is None:
            file_name = self.symbol + "_Data"

        if file_format == "csv":
            # Write csv files
            # Format: first axis in column, second in row, third in file
            if is_2D or len(axes_list_new) < 3:
                nfiles = 1
            elif len(axes_list_new) == 3 and is_multiple_files:
                nfiles = len(axes_list_new[2].values)
            elif len(axes_list_new) == 3:
                raise Exception(
                    "cannot export more than 2 dimensions in single csv file. Activate is_multiple_files to write in multiple csv files."
                )
            else:
                raise Exception("cannot export more than 3 dimensions in csv file")

            for i in range(nfiles):
                if nfiles > 1:
                    file_name_i = (
                        file_name
                        + "_"
                        + axes_list_new[2].name
                        + str(axes_list_new[2].values[i])
                    )
                    if slices == "":
                        slices = "sliced at "
                    slices_i = (
                        slices
                        + axes_list_new[2].name
                        + "="
                        + str(axes_list_new[2].values[i])
                    )
                else:
                    file_name_i = file_name
                    slices_i = slices
                with open(
                    os.path.join(save_path, file_name_i + "." + file_format),
                    "w+",
                    newline="",
                ) as my_csv:
                    csvWriter = csv.writer(my_csv, delimiter=",")
                    # First line: meta-data
                    if unit == "SI":
                        unit = self.unit
                    if "dB" in unit:
                        unit += (
                            " re. "
                            + str(self.normalizations["ref"].ref)
                            + " "
                            + self.unit
                        )

                    meta_data = [self.symbol, self.name, "[" + unit + "]", slices_i]
                    csvWriter.writerow(meta_data)

                    if is_2D:
                        # Second line: axes + second axis values
                        if len(Ydatas) > 1:
                            A2_cell = xlabel + "/" + legends[-1].split("=")[0]
                            second_line = self.format_matrix(
                                np.insert(
                                    np.array(legends).astype("<U64"),
                                    0,
                                    A2_cell,
                                ),
                                CHAR_LIST,
                            )
                        else:
                            A2_cell = xlabel
                            second_line = [A2_cell]
                        csvWriter.writerow(second_line)

                        # Rest of file: first axis + matrix
                        if len(Ydatas) == 1:
                            field = np.array(Ydatas[0])
                        else:
                            field = np.array(Ydatas)
                        if field.shape[0] != len(Xdata[0]):
                            field = field.T
                        matrix = self.format_matrix(
                            np.column_stack((np.array(Xdata[0]).T, field)).astype(
                                "str"
                            ),
                            CHAR_LIST,
                        )
                        csvWriter.writerows(matrix)

                    else:
                        # Second line: axes + second axis values
                        if len(axes_list_new) == 1:
                            A2_cell = (
                                axes_list_new[0].name
                                + "["
                                + axes_list_new[0].unit
                                + "]"
                            )
                            second_line = [A2_cell]
                        else:
                            A2_cell = (
                                axes_list_new[0].name
                                + "["
                                + axes_list_new[0].unit
                                + "]"
                                + "/"
                                + axes_list_new[1].name
                                + "["
                                + axes_list_new[1].unit
                                + "]"
                            )
                            second_line = self.format_matrix(
                                np.insert(
                                    results[axes_list_new[1].name].astype("<U64"),
                                    0,
                                    A2_cell,
                                ),
                                CHAR_LIST,
                            )
                        csvWriter.writerow(second_line)

                        # Rest of file: first axis + matrix
                        if len(results[self.symbol].shape) == 1:
                            # Transpose if 1D array
                            field = results[self.symbol].T
                        elif nfiles > 1:
                            # Slice third axis
                            field = np.take(results[self.symbol], i, axis=2)
                        else:
                            field = results[self.symbol]
                        matrix = self.format_matrix(
                            np.column_stack(
                                (results[axes_list_new[0].name].T, field)
                            ).astype("str"),
                            CHAR_LIST,
                        )
                        csvWriter.writerows(matrix)

        else:
            raise Exception("export format not supported")

    @staticmethod
    def format_matrix(a, char_list):
        for char in char_list:
            a = np.char.replace(a, char, "")
        return a

    # Inlined from Methods.SciDataTool.DataND.filter_spectral_leakage
    def filter_spectral_leakage(
        self,
        freqs_th,
        axes_list_filt=[],
        arg_list=[],
        Wmatf=np.array([]),
        If=np.array([]),
        is_return_calc_data=False,
    ):
        """Filter spectral leakage from a SciDataTool DataND object

        Parameters
        ----------
        self : DataND
            a DataND object
        freqs_th : ndarray
            theoretical frequencies
        axes_list_filt : [Data]
            Axes list to be stored in filtered DataFreq
        arg_list : list
            List of axes arguments to call SciDataTool get_along()
        Wmatf : ndarray
            Filtering matrix
        If: ndarray
            Index of FFT harmonics components used to calculate Wmatf
        is_return_all_args: bool
            True to return all data that can be used to speed calculation for further use

        Returns
        -------
        data_filt : DataND
            a DataND object
        axes_list_filt : [Data]
            Axes list to be stored in filtered DataFreq
        arg_list : list
            List of axes arguments to call SciDataTool get_along()
        Wmatf : ndarray
            Filtering matrix
        If: ndarray
            Index of FFT harmonics components used to calculate Wmatf
        freqs_th : ndarray
            theoretical frequencies
        """

        DataFreq = import_class("DataFreq")

        DataPattern = import_class("DataPattern")

        if len(axes_list_filt) == 0 or len(arg_list) == 0:
            # Get fft along frequency axis (keep other axes)
            arg_list = []  # Reinstantiate a different list
            axes_list = self.get_axes()
            for axis in axes_list:
                if axis.name == "time":
                    arg_list.append("freqs")
                elif axis.name == "angle":
                    arg_list.append("wavenumber")
                elif axis.name == "z" and isinstance(axis, DataPattern):
                    arg_list.append("z[smallestpattern]")
                else:
                    arg_list.append(axis.name)

        is_real = self.is_real
        self.is_real = False  # To have negative frequencies
        result = self.get_along(*arg_list, is_squeeze=False)
        freqs = result["freqs"]
        spectrum = result[self.symbol]

        if Wmatf.size == 0:
            # Get time step
            Time = self.get_axes("time")
            if len(Time) > 0:
                time = Time[0].get_values()
            else:
                result_time = self.get_along("time")
                time = result_time["time"]
            dt = time[1] - time[0]
            Nt = time.size
        else:
            Nt, dt = None, None

        if is_real and np.where(freqs < 0)[0].size == 0:
            # Mirror values to negative frequencies
            If0 = freqs != 0
            spectrum[If0, ...] *= 0.5
            If0[-1] = bool(np.mod(freqs.size, 2) == 0)
            freqs = np.concatenate((-np.flip(freqs), freqs[If0]))
            spectrum = np.concatenate(
                (
                    np.flip(np.conj(spectrum)),
                    spectrum[If0, ...],
                ),
                axis=0,
            )

        # Restrict filtering to negative wavenumber only
        if is_real and "wavenumber" in result:
            wavenumber = result["wavenumber"]
            Irn = wavenumber <= 0
            spectrum = spectrum[:, Irn, ...]

        spectrum_filt, freqs_th, Wmatf, If = filter_spectral_leakage_fct(
            spectrum, freqs, freqs_th, Nt, dt, is_freq_pos=False, Wmatf=Wmatf, If=If
        )

        if is_real:
            # Multiply all components by two except zero frequency component
            spectrum_filt *= 2
            I0 = freqs_th == 0
            spectrum_filt[I0, ...] = 0.5 * spectrum_filt[I0, ...]

            # Keep only positive frequencies
            Ifp = freqs_th >= 0
            freqs_th_store = freqs_th[Ifp]

            # Mirror spectrum
            if "wavenumber" in result:
                # Mirror negative frequencies to negative wavenumbers
                Ifn = ~Ifp
                if freqs_th_store[0] == 0:
                    Ifn[I0] = True
                spectrum_filt = np.concatenate(
                    (
                        spectrum_filt[Ifp, ...],
                        np.flip(np.conj(spectrum_filt[Ifn, 1:-1, ...])),
                    ),
                    axis=1,
                )
            else:
                spectrum_filt = spectrum_filt[Ifp, ...]

        else:
            freqs_th_store = np.array(freqs_th)

        if len(axes_list_filt) == 0:
            axes_list_filt = []  # Reinstantiate a different list
            axes_list_filt.append(
                Data1D(
                    name="freqs",
                    unit="Hz",
                    values=freqs_th_store,
                    normalizations=axes_list[0].normalizations,
                    symmetries={},
                )
            )

            if "wavenumber" in result:
                axes_list_filt.append(
                    Data1D(
                        name="wavenumber",
                        unit="dimless",
                        values=result["wavenumber"],
                        normalizations=axes_list[1].normalizations,
                        symmetries={},
                    )
                )

            # Copy other axes
            if "angle" in [axis.name for axis in self.axes] or "wavenumber" in [
                axis.name for axis in self.axes
            ]:
                n = 2
            else:
                n = 1
            for axis in axes_list[n:]:
                axes_list_filt.append(axis.copy())

        data_filt = DataFreq(
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            axes=axes_list_filt,
            values=spectrum_filt,
            normalizations=self.normalizations,
            is_real=True,
        )

        self.is_real = is_real

        if is_return_calc_data:
            return data_filt, axes_list_filt, arg_list, Wmatf, If, freqs_th

        else:
            return data_filt

    # Inlined from Methods.SciDataTool.DataND.get_along
    def get_along(
        self,
        *args,
        unit="SI",
        is_norm=False,
        axis_data=[],
        is_squeeze=True,
        is_magnitude=False,
        corr_unit=None,
    ):
        """Returns the ndarray of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """
        # Read the axes input in args
        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        # Fix axes order
        args = fix_axes_order([axis.name for axis in self.get_axes()], args)

        axes_list = read_input_strings(args, axis_data)
        # Extract the requested axes (symmetries + unit)
        axes_list, transforms = self._comp_axes(axes_list)
        # Get the field
        values = self._get_field(axes_list)
        # If DataFreq + 1 ifft axis + 1 fft axis: perform ifft on all axes then fft
        save_transforms = None
        save_names = None
        if "ifft" in transforms and "fft" in transforms:
            save_transforms = [axis.transform for axis in axes_list]
            save_names = [axis.name for axis in axes_list]
            for axis in axes_list:
                if axis.name == "freqs":
                    axis.transform = "ifft"
                    axis.name = "time"
                elif axis.name == "wavenumber":
                    axis.transform = "ifft"
                    axis.name = "angle"
        # Inverse fft
        if "ifft" in transforms:
            values = comp_ifftn(
                values, axes_list, is_real=self.is_real, axes_list=self.axes
            )
        # Prepare fft in ifft/fft case
        if save_transforms is not None:
            for i, transform in enumerate(save_transforms):
                axes_list[i].name = save_names[i]
                if transform == "fft_axis":
                    axes_list[i].transform = "fft"
                    save_transforms[i] = "fft"
                else:
                    axes_list[i].transform = transform
        # Slices along time/space axes
        values, axes_dict_other = self._extract_slices(values, axes_list)
        # fft
        if "fft" in transforms:
            values = comp_fftn(values, axes_list, is_real=self.is_real)
        # Slices along fft axes
        values = self._extract_slices_fft(values, axes_list)
        # Rebuild symmetries
        values = self._rebuild_symmetries(values, axes_list)
        # Interpolate over axis values
        values = self._interpolate(values, axes_list)
        # Apply operations such as sum, integration, derivations etc.
        values = self._apply_operations(
            values, axes_list, is_magnitude, unit=self.unit, corr_unit=corr_unit
        )
        # Conversions
        values = self._convert(values, unit, is_norm, is_squeeze, axes_list)
        # Return axes and values
        return_dict = {}
        for axis_requested in axes_list:
            if axis_requested.extension in [
                "max",
                "min",
                "sum",
                "rss",
                "mean",
                "rms",
                "integrate",
            ]:
                return_dict[axis_requested.name] = axis_requested.extension
            else:
                return_dict[axis_requested.name] = axis_requested.values
        return_dict[self.symbol] = values
        return_dict["axes_list"] = axes_list
        return_dict["axes_dict_other"] = axes_dict_other
        return return_dict

    # Inlined from Methods.SciDataTool.DataND.get_axes
    def get_axes(self, *args):
        """Returns the list of axes.
        Parameters
        ----------
        self: Data
            a Data object
        args : list
            list of axes names
        Returns
        -------
        axes_list : list of axes (Data)
        """

        axes = self.axes

        if len(args) > 0:
            axes_list = []
            for name in args:
                for axis in axes:
                    if axis.name == name:
                        axes_list.append(axis)
        else:
            axes_list = axes

        return axes_list

    # Inlined from Methods.SciDataTool.DataND.get_data_along
    def get_data_along(self, *args, unit="SI", is_norm=False, axis_data=[]):
        """Returns the sliced or interpolated version of the data, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        a DataND object
        """

        if "dB" in unit:
            results = self.get_magnitude_along(
                *args, is_squeeze=False, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
        else:
            results = self.get_along(
                *args, is_squeeze=False, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
        values = results.pop(self.symbol)
        del results["axes_dict_other"]
        axes_list = results.pop("axes_list")
        Axes = []

        axes_name_new = list(results.keys())
        if "time" in axes_name_new:
            Data_type = "DataTime"
        elif "freqs" in axes_name_new:
            Data_type = "DataFreq"
        else:
            Data_type = "DataND"

        # Dynamic import to avoid loop
        DataClass = import_class(Data_type)

        for axis_name in axes_name_new:
            if not isinstance(results[axis_name], str):
                for i, axis in enumerate(self.axes):
                    if axis.name == axis_name:
                        index = i
                        name = axis.name
                        is_components = axis.is_components
                        axis_values = results[axis_name]
                        ax_unit = axis.unit
                    elif axis_name in axes_dict_transformation:
                        if axes_dict_transformation[axis_name][0] == axis.name:
                            index = i
                            name = axis_name
                            is_components = axis.is_components
                            axis_values = results[axis_name]
                            ax_unit = axes_dict_transformation[axis_name][2]
                    elif axis_name in rev_axes_dict:
                        if rev_axes_dict[axis_name][0] == axis.name:
                            index = i
                            name = axis_name
                            is_components = axis.is_components
                            axis_values = results[axis_name]
                            ax_unit = rev_axes_dict[axis_name][2]
                # Update symmetries
                if (
                    "smallestperiod" in args[index]
                    or args[index]
                    in [
                        "freqs",
                        "wavenumber",
                    ]
                    or "antiderivate" in args[index]
                    or "derivate" in args[index]
                ):
                    symmetries = self.axes[index].symmetries.copy()
                else:
                    symmetries = {}
                Axis = Data1D(
                    name=name,
                    unit=ax_unit,
                    values=axis_values,
                    is_components=is_components,
                    normalizations=self.axes[index].normalizations.copy(),
                    symmetries=symmetries,
                ).to_linspace()
                if hasattr(self.axes[index], "sort_indices") and hasattr(
                    Axis, "sort_indices"
                ):
                    Axis.sort_indices = self.axes[index].sort_indices
                Axes.append(Axis)

        # Update unit if dB/dBA conversion
        if "dB" in unit:
            unit = unit
        else:
            # Update unit if derivation or integration
            unit = self.unit
            for axis in axes_list:
                if axis.extension in ["antiderivate", "integrate", "integrate_local"]:
                    unit = get_unit_integrate(unit, axis.corr_unit)
                elif axis.extension == "derivate":
                    unit = get_unit_derivate(unit, axis.corr_unit)

        return DataClass(
            name=self.name,
            unit=unit,
            symbol=self.symbol,
            axes=Axes,
            values=values,
            normalizations=self.normalizations.copy(),
            is_real=self.is_real,
        )

    # Inlined from Methods.SciDataTool.DataND.get_harmonics
    def get_harmonics(
        self, N_harm, *args, unit="SI", is_norm=False, axis_data=None, is_flat=False
    ):
        """Returns the complex Fourier Transform of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        N_harm: int
            Number of largest harmonics to be extracted
        args: list
            Axes names, ranges and units
        unit: str
            Unit demanded by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        is_flat: bool
            Boolean if the output data remains flattened (for 2D cases)
        Returns
        -------
        list of 1Darray of axes values, ndarray of magnitude of FT
        """
        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args
        return_dict = self.get_magnitude_along(
            args, unit=unit, is_norm=is_norm, axis_data=axis_data
        )
        values = return_dict[self.symbol]

        # 2D case
        if "freqs" in return_dict and "wavenumber" in return_dict:
            r = return_dict["wavenumber"]
            f = return_dict["freqs"]
            # Flatten the data
            values_flat = values.flatten()
            R, F = np.meshgrid(r, f)
            f = F.flatten()
            r = R.flatten()
            # Get the N_harm largest peaks
            indices = np.argsort(np.negative(values_flat))
            indices = indices[:N_harm]
            values = values_flat[indices]
            f = f[indices]
            r = r[indices]
            if len(values.shape) == 2 and not is_flat:
                f.reshape((N_harm, N_harm))
                r.reshape((N_harm, N_harm))
                values.reshape((N_harm, N_harm))
            return_dict["freqs"] = f
            return_dict["wavenumber"] = r
            return_dict[self.symbol] = values

        # 1D cases
        elif "freqs" in return_dict:
            f = return_dict["freqs"]
            indices = np.argsort(np.negative(values))
            indices = indices[:N_harm]
            f = f[indices]
            values = values[indices]
            return_dict["freqs"] = f
            return_dict[self.symbol] = values
        elif "wavenumber" in return_dict:
            r = return_dict["wavenumber"]
            indices = np.argsort(np.negative(values))
            indices = indices[:N_harm]
            r = r[indices]
            values = values[indices]
            return_dict["wavenumber"] = r
            return_dict[self.symbol] = values

        return return_dict

    # Inlined from Methods.SciDataTool.DataND.get_magnitude_along
    def get_magnitude_along(
        self,
        *args,
        unit="SI",
        is_norm=False,
        axis_data=[],
        is_squeeze=True,
        is_sum=True,
        corr_unit=None,
    ):
        """Returns the ndarray of the magnitude of the FT, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of magnitude values
        """
        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        # Fix axes order
        args = fix_axes_order([axis.name for axis in self.get_axes()], args)

        # For dB/dBA conversions, first extraction with freqs axis
        if "dB" in unit and unit != self.unit and is_sum:
            new_args = list(args).copy()
            freq_name = None
            index_freq = None
            index_speed = None
            index_order = None
            args_freqs = ["freqs", "frequency", "time"]
            for i, axis in enumerate(self.axes):  # Find frequency axis
                if axis.name in args_freqs:
                    freq_name = axis.name
            if freq_name is not None:
                for i, arg in enumerate(args):
                    if freq_name in arg:
                        if "sum" in arg or "rss" in arg:
                            new_args[i] = freq_name
                            index_freq = i
                if index_freq is None:  # No sum on freqs axis -> can extract directly
                    return self.get_magnitude_along(
                        *args,
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                    )
                else:
                    data = self.get_data_along(
                        *new_args, axis_data=axis_data, unit=unit
                    )  # Extract first along freqs axis
                    return data.get_magnitude_along(
                        *[args[index_freq]],
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                        corr_unit=self.unit,
                    )  # Then sum on freqs axis
            else:  # Try speed/order
                is_match = 0
                for i, axis in enumerate(self.axes):  # Find frequency axis
                    if axis.name == "speed":
                        is_match += 1
                        arg_speed = "speed"
                    elif axis.name == "order":
                        is_match += 1
                    elif "speed" in axis.normalizations:
                        is_match += 1
                        arg_speed = axis.name + "->speed"
                if is_match == 2:
                    for i, arg in enumerate(args):
                        if "speed" in arg:
                            if arg.split("{")[0] != arg_speed:
                                new_args[i] = arg_speed
                                index_speed = i
                        elif "order" in arg:
                            if arg.split("{")[0] != "order":
                                new_args[i] = "order"
                                index_order = i
                elif is_match == 1:
                    for i, arg in enumerate(args):
                        if "speed" in arg:
                            if arg.split("{")[0] != arg_speed:
                                new_args[i] = arg_speed
                                index_speed = i
                elif unit == "dB" or "A-weight" in self.normalizations:
                    self.get_magnitude_along(
                        *args,
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                    )
                else:
                    raise AxisError(
                        "Cannot convert to " + unit + " without a frequency axis"
                    )
                if (
                    index_speed is None and index_order is None
                ):  # No sum on freqs axis -> can extract directly
                    return self.get_magnitude_along(
                        *args,
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                    )
                elif index_speed is None:  # Sum on order axis
                    if "[" in args[-1]:
                        new_args[-1] = args[-1].split("[")[0]
                    data = self.get_data_along(
                        *new_args, axis_data=axis_data, unit=unit
                    )  # Extract first along order axis
                    return data.get_magnitude_along(
                        *[arg_speed, args[index_order]] + args[2:],
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                        corr_unit=self.unit,
                    )  # Then sum on order axis
                elif index_order is None:  # Sum on speed axis
                    data = self.get_data_along(
                        *new_args, axis_data=axis_data, unit=unit
                    )  # Extract first along speed axis
                    return data.get_magnitude_along(
                        *args,
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                        corr_unit=self.unit,
                    )  # Then sum on speed axis
                else:  # Sum on speed and order axes
                    data = self.get_data_along(
                        *new_args, axis_data=axis_data, unit=unit
                    )  # Extract first along speed and order axes
                    return data.get_magnitude_along(
                        *[args[index_speed], args[index_order]],
                        axis_data=axis_data,
                        unit=unit,
                        is_squeeze=is_squeeze,
                        is_sum=False,
                        corr_unit=self.unit,
                    )  # Then sum on speed and order axes

        else:
            return_dict = self.get_along(
                *args,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
                is_magnitude=True,
                corr_unit=corr_unit,
            )
            values = return_dict[self.symbol]

            # 1/nth octave band
            for axis in return_dict["axes_list"]:
                if axis.name == "freqs" or axis.corr_name == "freqs":
                    index = axis.index
                    if axis.noct is not None:
                        (values, foct) = np.apply_along_axis(
                            to_noct, index, values, return_dict["freqs"], noct=axis.noct
                        )
                        return_dict[axis.name] = foct
            # Convert into right unit (apart because of dBA conversion)
            if unit == self.unit or unit == "SI":
                if is_norm:
                    try:
                        values = self.normalizations["ref"].normalize(values)
                    except:
                        raise NormError(
                            "Reference value not specified for normalization"
                        )
            elif unit == "dB":
                ref_value = 1.0
                if "ref" in self.normalizations:
                    ref_value *= self.normalizations["ref"].ref
                values = to_dB(values, self.unit, ref_value)
            elif unit == "dBA":
                ref_value = 1.0
                if "ref" in self.normalizations:
                    ref_value *= self.normalizations["ref"].ref
                if "A-weight" in self.normalizations:
                    values = to_dB(values, self.unit, ref_value)
                    # Extract requested indices from A-weight
                    axes_list = return_dict["axes_list"]
                    index_list = []
                    for ii, axis in enumerate(axes_list):
                        if (
                            axis.indices is not None
                            and len(axis.indices) > 1
                            and len(axis.indices) < len(axis.values)
                        ):
                            index_list.append(ii)
                    A_weight = self.normalizations["A-weight"].vector
                    for index in index_list:
                        A_weight = np.take(
                            A_weight,
                            axes_list[index].indices,
                            axis=index,
                        )
                    # Flatten to apply A-weighting
                    A_weight = A_weight.ravel("C")
                    shape = values.shape
                    values = values.reshape(
                        A_weight.shape
                        + shape[len(self.normalizations["A-weight"].vector.shape) :]
                    )
                    values = np.apply_along_axis(np.add, 0, values, A_weight)
                    values = values.reshape(shape)
                elif "freqs" in return_dict.keys():
                    for axis in return_dict["axes_list"]:
                        if axis.name == "freqs" or axis.corr_name == "freqs":
                            index = axis.index
                    if return_dict["axes_list"][
                        index
                    ].corr_values is not None and return_dict["axes_list"][
                        index
                    ].unit not in [
                        "SI",
                        return_dict["axes_list"][index].corr_unit,
                    ]:
                        freqs = return_dict["axes_list"][index].corr_values
                    else:
                        freqs = return_dict["freqs"]
                    values = np.apply_along_axis(
                        to_dBA, index, values, freqs, self.unit, ref_value
                    )
                elif "frequency" in return_dict.keys():
                    for axis in return_dict["axes_list"]:
                        if axis.name == "frequency" or axis.corr_name == "frequency":
                            index = axis.index
                    if return_dict["axes_list"][
                        index
                    ].corr_values is not None and return_dict["axes_list"][
                        index
                    ].unit not in [
                        "SI",
                        return_dict["axes_list"][index].corr_unit,
                    ]:
                        freqs = return_dict["axes_list"][index].corr_values
                    else:
                        freqs = return_dict["frequency"]
                    values = np.apply_along_axis(
                        to_dBA, index, values, freqs, self.unit, ref_value
                    )
                elif "order" in return_dict:
                    freqs = self._get_freqs()
                    freqs = freqs.ravel("C")
                    shape = values.shape
                    values = values.reshape(freqs.shape + shape[2:])
                    values = np.apply_along_axis(
                        to_dBA, 0, values, freqs, self.unit, ref_value
                    )
                    values = values.reshape(shape)
                else:
                    raise UnitError(
                        "dBA conversion only available for fft with frequencies"
                    )

            elif unit in self.normalizations:
                values = self.normalizations.get(unit).normalize(values)
            else:
                values = convert(values, self.unit, unit)
            return_dict[self.symbol] = values
            return return_dict

    # Inlined from Methods.SciDataTool.DataND.get_phase_along
    def get_phase_along(self, *args, unit="SI", is_norm=False, axis_data=[]):
        """Returns the ndarray of the magnitude of the FT, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of magnitude values
        """
        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args
        return_dict = self.get_along(args, axis_data=axis_data)
        values = return_dict[self.symbol]
        # Compute magnitude
        values = np.angle(values)
        # Convert into right unit (apart because of degree conversion)
        if unit == self.unit or unit == "SI":
            if is_norm:
                try:
                    values = self.normalizations["ref"].normalize(values)
                except:
                    raise NormError("Reference value not specified for normalization")
        elif unit == "°":
            values = convert(values, "rad", "°")
        elif unit in self.normalizations:
            values = self.normalizations.get(unit).normalize(values)
        else:
            values = convert(values, self.unit, unit)
        return_dict[self.symbol] = values
        return return_dict

    # Inlined from Methods.SciDataTool.DataND.has_period
    def has_period(self):
        """Indicates if a field has symmetries.
        Parameters
        ----------
        self: DataND
            a DataND object
        Returns
        -------
        Boolean
        """
        answer = False

        for axis in self.axes:
            if axis.symmetries != {}:
                answer = True

        return answer

    # Inlined from Methods.SciDataTool.DataND.orthogonal_mp
    def orthogonal_mp(
        self,
        Time: Data1D,
        n_coefs: int = None,
        precompute: bool = True,
        dictionary=None,
    ):
        """
        Execute the Orthogonal Matching Pursuit, this method returns a DataND object with the Time axe,
        self is the DataND undersampled object.

        Parameters
        ----------
        Time: The time axe on which the signals are recovered
        M: The undersampling indices, Time.values[M] is the time axe of self
        n_coefs: The number of atoms of the dictionary used to recover the signal,
        if None set to 10 % of len(M)
        dictionary: A special dictionary which is pass to the backend

        Returns
        recovered_dataND: A new dataND object composed of the recovered components
        """

        # This method should only be used for 1D or 2D field, where the
        # undersampling is in the time's direction
        nombre_axes = len(self.axes)
        assert nombre_axes == 2 or nombre_axes == 1, (
            "Dimension error: {} not in {1,2}".format(nombre_axes)
        )

        axes_name = [self.axes[i].name for i in range(nombre_axes)]
        assert "time" in axes_name, "There is no time axe"
        axes_name.remove("time")

        # Extract the axes
        if nombre_axes == 2:
            [Angle] = self.get_axes(axes_name[0])
        [Time_undersampled] = self.get_axes("time")

        M = comp_undersampled_axe(Time, Time_undersampled)

        n = len(Time.values)

        # Stack the signals into the columns of the matrix Y (n,n_targets)
        Y = self.values

        # Compute the OMP
        Y_full = omp(
            Y, M, n, n_coefs=n_coefs, precompute=precompute, dictionary=dictionary
        )

        # Build the DataND object
        if nombre_axes == 1:
            recovered_dataND = type(self)(
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                values=Y_full,
                axes=[Time],
                is_real=self.is_real,
            )
        if nombre_axes == 2:
            recovered_dataND = type(self)(
                name=self.name,
                symbol=self.symbol,
                unit=self.unit,
                axes=[Time, Angle],
                values=Y_full,
                is_real=self.is_real,
            )

        return recovered_dataND

    # Inlined from Methods.SciDataTool.DataND.plot_2D_Data
    def plot_2D_Data(
        self,
        *arg_list,
        axis_data=None,
        is_norm=False,
        unit="SI",
        overall_axes=[],
        contribution_axis=None,
        data_list=[],
        legend_list=[],
        color_list=None,
        linestyles=None,
        linewidth_list=[1.5],
        save_path=None,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        is_logscale_x=False,
        is_logscale_y=False,
        is_disp_title=True,
        is_grid=True,
        is_auto_ticks=True,
        is_auto_range=True,
        xlabel=None,
        ylabel=None,
        title=None,
        fig=None,
        ax=None,
        barwidth=100,
        type_plot=None,
        fund_harm_dict=None,
        is_show_fig=None,
        win_title=None,
        thresh=None,
        font_name="arial",
        font_size_title=12,
        font_size_label=10,
        font_size_legend=8,
        is_show_legend=True,
        is_outside_legend=False,
        is_frame_legend=True,
        is_indlabels=False,
        annotations=None,
        is_export=False,
    ):
        """Plots a field as a function of time

        Parameters
        ----------
        data : Data
            a Data object
        *arg_list : list of str
            arguments to specify which axes to plot
        is_norm : bool
            boolean indicating if the field must be normalized
        unit : str
            unit in which to plot the field
        data_list : list
            list of Data objects to compare
        legend_list : list
            list of legends to use for each Data object (including reference one) instead of data.name
        color_list : list
            list of colors to use for each Data object
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        x_min : float
            minimum value for the x-axis
        x_max : float
            maximum value for the x-axis
        y_min : float
            minimum value for the y-axis
        y_max : float
            maximum value for the y-axis
        is_logscale_x : bool
            boolean indicating if the x-axis must be set in logarithmic scale
        is_logscale_y : bool
            boolean indicating if the y-axis must be set in logarithmic scale
        is_disp_title : bool
            boolean indicating if the title must be displayed
        is_grid : bool
            boolean indicating if the grid must be displayed
        is_auto_ticks : bool
            in fft, adjust ticks to freqs (deactivate if too close)
        is_auto_range : bool
            in fft, display up to 1% of max
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            ax on which to plot the data
        barwidth : float
            barwidth scaling factor, only if type_plot = "bargraph"
        type_plot : str
            type of 2D graph : "curve", "bargraph", "barchart" or "quiver"
        fund_harm_dict : dict
            Dict containing axis name as key and frequency/order/wavenumber of fundamental harmonic as value to display fundamental harmonic in red in the fft
        is_show_fig : bool
            True to show figure after plot
        win_title : str
            Title of the plot window
        thresh : float
            threshold for automatic fft ticks
        is_outside_legend : bool
            True to display legend outside the graph
        is_frame_legend : bool
            True to display legend in a frame
        """

        # Dynamic import to avoid import loop
        DataPattern = import_class("DataPattern")

        # Extract arg_list it the function called from another script with *arg_list
        if len(arg_list) == 1 and type(arg_list[0]) == tuple:
            arg_list = arg_list[0]

        axes_names = [
            axis.name for axis in read_input_strings(arg_list, axis_data=axis_data)
        ]

        # Fix axes order
        arg_list_along = fix_axes_order(
            [axis.name for axis in self.get_axes()], arg_list
        )

        # In case of 1D fft, keep only positive wavenumbers
        for i, arg in enumerate(arg_list_along):
            if "wavenumber" in arg and "=" not in arg and "[" not in arg:
                liste = list(arg_list_along)
                liste[i] = arg.replace("wavenumber", "wavenumber>0")
                arg_list_along = tuple(liste)

        if color_list == [] or color_list is None:
            color_list = COLORS

        new_color_list = color_list.copy()

        # Set unit
        if unit == "SI":
            unit = self.unit

        # Detect if is fft, build ylabel
        if "dB" in unit and "ref" in self.normalizations:
            unit_str = (
                "["
                + unit
                + " re. "
                + str(self.normalizations["ref"].ref)
                + " $"
                + self.unit
                + "$]"
            )
        else:
            unit_str = r"$[" + unit + "]$"
        is_fft = False
        if (
            any("wavenumber" in s for s in arg_list)
            or any("freqs" in s for s in arg_list)
        ) and type_plot != "curve":
            is_fft = True
            if self.symbol == "Magnitude":
                if ylabel is None:
                    ylabel = "Magnitude " + unit_str
            else:
                if ylabel is None:
                    ylabel = r"$|\widehat{" + self.symbol + "}|$ " + unit_str
        else:
            if is_norm:
                if ylabel is None:
                    ylabel = (
                        r"$\frac{"
                        + self.symbol
                        + "}{"
                        + self.symbol
                        + "_0}\\,$"
                        + unit_str
                    )
            else:
                if self.symbol == "Magnitude":
                    if ylabel is None:
                        ylabel = "Magnitude " + unit_str
                else:
                    if ylabel is None:
                        ylabel = r"$" + self.symbol + "\\,$" + unit_str

        # Extract field and axes
        Xdatas = []
        Ydatas = []
        data_list2 = [self] + data_list
        for i, d in enumerate(data_list2):
            if is_fft or "dB" in unit:
                result = d.get_magnitude_along(
                    *arg_list_along, axis_data=axis_data, unit=unit, is_norm=is_norm
                )
                if i == 0:
                    axes_list = result.pop("axes_list")
                    axes_dict_other = result.pop("axes_dict_other")
                    result_0 = result
            else:
                result = d.get_along(
                    *arg_list_along, axis_data=axis_data, unit=unit, is_norm=is_norm
                )
                if i == 0:
                    axes_list = result.pop("axes_list")
                    axes_dict_other = result.pop("axes_dict_other")
                    result_0 = result
            Ydatas.append(result.pop(d.symbol))
            # in string case not overlay, Xdatas is a linspace
            if (
                axes_list[list(result.keys()).index(axes_names[0])].is_components
                and axes_list[list(result.keys()).index(axes_names[0])].extension
                != "list"
            ):
                xdata = np.linspace(
                    0, len(result[axes_names[0]]) - 1, len(result[axes_names[0]])
                )
            else:
                xdata = result[axes_names[0]]
            Xdatas.append(xdata)

        # Build xlabel and title
        title1 = self.name[0].capitalize() + self.name[1:] + " "
        title2 = "for "
        for axis in axes_list:
            if axis.unit in norm_dict and axis.unit != "Hz":
                name = norm_dict[axis.unit].split(" [")[0]
            elif axis.name in axes_dict:
                name = axes_dict[axis.name]
            else:
                name = axis.name
            if (
                axis.extension
                in [
                    "whole",
                    "interval",
                    "oneperiod",
                    "antiperiod",
                    "smallestperiod",
                    "axis_data",
                    "list",
                ]
                and len(axis.values) > 1
                or (len(axis.values) == 1 and len(axes_list) == 1)
            ):
                if axis.unit == "SI":
                    if axis.name in unit_dict:
                        axis_unit = unit_dict[axis.name]
                    else:
                        axis_unit = axis.unit
                    if xlabel is None:
                        xlabel = (
                            name[0].capitalize() + name[1:] + " [" + axis_unit + "]"
                        )
                    main_axis_name = name
                elif axis.unit in norm_dict:
                    if xlabel is None:
                        xlabel = norm_dict[axis.unit]
                    if axis.unit == "Hz":
                        main_axis_name = "frequency"
                    else:
                        main_axis_name = axis.unit
                else:
                    axis_unit = axis.unit
                    if xlabel is None:
                        xlabel = (
                            name[0].capitalize() + name[1:] + " [" + axis_unit + "]"
                        )
                    main_axis_name = name
                if (
                    axis.name == "angle"
                    and axis.unit == "°"
                    and round(np.nanmax(axis.values) / 6) % 5 == 0
                ):
                    xticks = [i * round(np.nanmax(axis.values) / 6) for i in range(7)]
                else:
                    xticks = None
                if (
                    axes_list[list(result.keys()).index(axes_names[0])].is_components
                    and not self.get_axes()[0].is_overlay
                ):
                    xticklabels = result[axes_names[0]]
                    xticks = Xdatas[0]
                else:
                    xticklabels = None
                    xticks = None
            else:
                if axis.corr_unit == "SI":
                    if axis.name in unit_dict:
                        axis_unit = unit_dict[axis.name]
                    else:
                        axis_unit = axis.unit
                elif axis.corr_unit in norm_dict and axis.corr_unit != "Hz":
                    axis_unit = norm_dict[axis.corr_unit]
                else:
                    axis_unit = axis.unit

                if isinstance(result_0[axis.name], str):
                    title2 += name + "=" + result_0[axis.name]
                else:
                    if isinstance(result_0[axis.name][0], str):
                        axis_str = result_0[axis.name][0]
                    else:
                        if result_0[axis.name][0] > 10:
                            fmt = "{:.5g}"
                        else:
                            fmt = "{:.3g}"
                        axis_str = np.array2string(
                            result_0[axis.name], formatter={"float_kind": fmt.format}
                        ).replace(" ", ", ")

                    if len(result_0[axis.name]) == 1:
                        axis_str = axis_str.strip("[]")

                    index = None
                    if axis.is_pattern and len(axis.values) == 1:
                        for axis_obj in self.get_axes():
                            if axis_obj.name == axis.name:
                                index = axis.indices[0]

                    title2 += (
                        name + "=" + axis_str.rstrip(", ") + " [" + axis_unit + "]"
                    )
                    if index is not None:
                        title2 += " (slice " + str(index + 1) + "), "
                    else:
                        title2 += ", "

        # Title part 3 containing axes that are here but not involved in requested axes
        title3 = ""
        for axis_name in axes_dict_other:
            is_display = True
            for axis in self.axes:
                if axis.name == axis_name:
                    if isinstance(axis, DataPattern) and len(axis.unique_indices) == 1:
                        is_display = False
            if is_display:
                if isinstance(axes_dict_other[axis_name][0], str):
                    title3 += axis_name + "=" + axes_dict_other[axis_name][0]
                else:
                    if axes_dict_other[axis_name][0] > 10:
                        fmt = "{:.5g}"
                    else:
                        fmt = "{:.3g}"
                    title3 += (
                        axis_name
                        + "="
                        + np.array2string(
                            axes_dict_other[axis_name][0],
                            formatter={"float_kind": fmt.format},
                        ).replace(" ", ", ")
                        + " ["
                        + axes_dict_other[axis_name][1]
                        + "], "
                    )

        if title2 == "for " and title3 == "":
            title2 = ""

        # Detect discontinuous axis (Norm_indices) to use bargraph
        for axis in axes_list:
            if axis.unit in self.axes[axis.index].normalizations:
                if isinstance(
                    self.axes[axis.index].normalizations[axis.unit], NormIndices
                ):
                    type_plot = "bargraph"

        # Detect how many curves are overlaid, build legend and color lists
        if legend_list == [] and data_list != []:
            legend_list = [d.name for d in data_list2]
        elif legend_list == []:
            legend_list = ["" for d in data_list2]
        legends = []
        # Prepare colors
        linestyle_list = linestyles
        for i, d in enumerate(data_list2):
            is_overlay = False
            for axis in axes_list:
                if axis.extension == "list" and len(axis.values) > 1:
                    is_overlay = True
                    if linestyles is None:
                        linestyles = ["dashed"]
                    n_curves = len(axis.values)
                    if axis.unit == "SI":
                        if axis.name in unit_dict:
                            axis_unit = unit_dict[axis.name]
                        else:
                            axis_unit = axis.unit
                    elif axis.unit in norm_dict:
                        axis_unit = norm_dict[axis.unit]
                    else:
                        axis_unit = axis.unit
                    if len(d.axes[axis.index].get_values()) > 1:
                        legends += [
                            (
                                legend_list[i]
                                + " "
                                + axis.name
                                + "="
                                + axis.values.tolist()[j].replace(";", "")
                                + " "
                                + axis_unit
                                if isinstance(axis.values.tolist()[j], str)
                                else legend_list[i]
                                + " "
                                + axis.name
                                + "="
                                + "%.3g" % axis.values.tolist()[j]
                                + " "
                                + axis_unit
                            )
                            .replace("SI", "")
                            .replace(" []", "")
                            for j in range(n_curves)
                        ]
                    else:
                        legends += [legend_list[i]]

            if not is_overlay:
                legends += [legend_list[i]]
                # Adjust colors in non overlay case with overlay axis
                if len(data_list2) > 1:
                    for axis in self.get_axes():
                        if axis.is_overlay and len(color_list) > len(axis.values):
                            new_color_list[1:] = color_list[len(axis.values) :]

        # Split Ydatas if the plot overlays several curves
        if is_overlay:
            Ydata = []
            for d in Ydatas:
                if d.ndim != 1:
                    axis_index = np.where(np.array(d.shape) == n_curves)[0]
                    if axis_index.size > 1:
                        print("WARNING, several axes with same dimensions")
                    Ydata += np.split(d, n_curves, axis=axis_index[-1])
                else:
                    Ydata += [d]
            Ydatas = [np.squeeze(d) for d in Ydata]
            Xdata = []
            for i in range(len(data_list2)):
                Xdata += [Xdatas[i] for x in range(n_curves)]
            Xdatas = Xdata

        # Finish title
        if title is None:
            # Reformat in case of operation
            for ope in ["max", "min", "mean"]:
                if "=" + ope in title2:
                    title2 = ""
                    title1 = (
                        ope[0].capitalize()
                        + ope[1:]
                        + " "
                        + title1[0].lower()
                        + title1[1:]
                    )

            # Concatenate all title parts
            if is_overlay:
                title = title1 + title3
            else:
                title = title1 + title2 + title3

            # Remove last coma due to title2 or title3
            title = title.rstrip(", ")

            # Remove dimless and quotes
            title = title.replace("SI", "").replace("[]", "").replace("'", "")

        xlabel = xlabel.replace("SI", "").replace(" []", "")  # Remove dimless units
        ylabel = ylabel.replace("SI", "").replace(" []", "")  # Remove dimless units

        # Overall computation
        if overall_axes != []:
            if self.unit == "W":
                op = "=sum"
            else:
                op = "=rss"
            arg_list_ovl = [0 for i in range(len(arg_list))]
            # Add sum to overall_axes
            for axis in overall_axes:
                is_match = False
                for i, arg in enumerate(arg_list):
                    if axis in arg:
                        is_match = True
                        arg_list_ovl[i] = axis + op
                if not is_match:
                    arg_list_ovl.append(axis + op)
            # Add other requested axes
            for i, arg in enumerate(arg_list):
                if arg_list_ovl[i] == 0:
                    arg_list_ovl[i] = arg
            if is_fft or "dB" in unit:
                result = self.get_magnitude_along(
                    *arg_list_ovl, unit=unit, axis_data=axis_data
                )
            else:
                result = self.get_along(*arg_list_ovl, unit=unit, axis_data=axis_data)
            Y_overall = result[self.symbol]
            # in string case not overlay, Xdatas is a linspace
            if (
                axes_list[list(result.keys()).index(axes_names[0])].is_components
                and axes_list[list(result.keys()).index(axes_names[0])].extension
                != "list"
            ):
                xdata = np.linspace(
                    0, len(result[axes_names[0]]) - 1, len(result[axes_names[0]])
                )
            else:
                xdata = result[list(result)[0]]
            Ydatas.insert(0, Y_overall)
            Xdatas.insert(0, xdata)
            new_color_list = new_color_list.copy()
            new_color_list.insert(0, "#000000")
            legends.insert(0, "Overall")

        # Contribution computation
        if contribution_axis is not None:
            contribution_name = contribution_axis.split("[")[0]
            selection = contribution_axis.split("[")[1].rstrip("]").split(",")
            contrib_axis = self.get_axes(contribution_name)[0]
            type_plot = "stack"
            OVL = Y_overall
            if True in ["sum" in arg for arg in arg_list_along]:
                sum_index = ["sum" in arg for arg in arg_list_along].index(True)
            else:
                sum_index = ["rss" in arg for arg in arg_list_along].index(True)
            contrib_index = None
            if contribution_name in [axis.name for axis in axes_list]:
                contrib_index = [axis.name for axis in axes_list].index(
                    contribution_name
                )
            contrib_array = np.zeros((contrib_axis.get_length(), len(Y_overall)))
            for i in range(contrib_axis.get_length()):
                if unit == "dBA":
                    arg_list_new = [
                        (
                            axis.name
                            if axis.name != contribution_name
                            else contribution_name + "[" + str(i) + "]"
                        )
                        for axis in self.get_axes()
                    ]
                    contrib = self.get_magnitude_along(*arg_list_new, unit="SI")[
                        self.symbol
                    ]
                    symbol = "AS" + self.symbol.capitalize() + "L"
                    name = (
                        "Sound " + self.name.lower().replace("acoustic ", "") + " Level"
                    )
                    A_weighting = (
                        self.get_magnitude_along(*arg_list_new, unit="dBA")[self.symbol]
                        - self.get_magnitude_along(*arg_list_new, unit="dB")[
                            self.symbol
                        ]
                    )
                    if self.unit == "W":
                        upper_sum = np.sum(
                            10 ** (0.1 * A_weighting)
                            * contrib
                            / self.normalizations["ref"].ref,
                            axis=sum_index,
                        )
                        cont = upper_sum / (10 ** (0.1 * OVL))
                    else:
                        upper_sum = np.sum(
                            10 ** (0.1 * A_weighting) * contrib**2, axis=sum_index
                        )
                        cont = upper_sum / (
                            (self.normalizations["ref"].ref ** 2) * 10 ** (0.1 * OVL)
                        )
                elif unit == "dB":
                    arg_list_new = [
                        (
                            arg
                            if contribution_name not in arg
                            else contribution_name + "[" + str(i) + "]"
                        )
                        for arg in arg_list_along
                    ]
                    contrib = self.get_magnitude_along(*arg_list_new, unit="SI")[
                        self.symbol
                    ]
                    if "acoustic" in self.name.lower():
                        symbol = "S" + self.symbol.capitalize() + "L"
                        name = (
                            "Sound "
                            + self.name.lower().replace("acoustic ", "")
                            + " Level"
                        )
                    else:
                        symbol = self.symbol
                        name = self.name
                    if self.unit == "W":
                        cont = contrib / (
                            self.normalizations["ref"].ref * 10 ** (0.1 * OVL)
                        )
                    else:
                        cont = contrib**2 / (
                            (self.normalizations["ref"].ref ** 2) * 10 ** (0.1 * OVL)
                        )
                else:
                    symbol = self.symbol
                    name = self.name
                    if self.unit == "W":
                        cont = Ydatas[i + 1] / OVL
                    else:
                        cont = Ydatas[i + 1] ** 2 / OVL**2
                contrib_array[i, :] = cont * 100
            # Remove small contributions
            # Iloads = where(sqrt(np_sum(contrib_array ** 2, 1)) > 1e-2)[0]
            # Sort in decreasing order
            Isort = np.argsort(-np.sqrt(np.sum(contrib_array**2, 1)), axis=0)
            Ydatas = [Ydatas[0]]
            legends = [r"100% (overall $" + symbol + "$)"]
            new_color_list = [new_color_list[0]]
            for i in range(len(Isort)):
                if (
                    contrib_index is not None
                    and axes_list[contrib_index].indices is not None
                    and "all" in selection
                ):
                    if Isort[i] in axes_list[contrib_index].indices:
                        Ydatas.append(contrib_array[Isort[i], :])
                        legends.append(contrib_axis.values[Isort[i]])
                        new_color_list.append(color_list[i % (len(color_list))])
                elif "all" in selection or all(
                    [s in contrib_axis.values[Isort[i]] for s in selection]
                ):
                    Ydatas.append(contrib_array[Isort[i], :])
                    legends.append(contrib_axis.values[Isort[i]])
                    new_color_list.append(color_list[i % (len(color_list))])
            sel_str = ""
            if "all" not in selection:
                if "stator" in selection:
                    sel_str += " applied to stator"
                elif "rotor" in selection:
                    sel_str += " applied to rotor"
                if "radial" in selection:
                    sel_str += " in radial direction"
                elif "circ." in selection:
                    sel_str += " in circumferential direction"
                title = " ".join(selection).capitalize()
            else:
                title = axes_dict[contribution_name].capitalize()
            ylabel = name + " contribution [%]"
            title = "Contribution of magnetic Load Cases" + sel_str

        # Deactivate legend if only one item
        if type_plot == "point":
            legends = []

        if "dB" in unit:  # Replace <=0 by nans
            for ydata in Ydatas:
                ydata[ydata <= 0] = np.nan

        # Call generic plot function
        if is_fft:
            if thresh is None:
                if self.normalizations is not None and "ref" in self.normalizations:
                    thresh = self.normalizations["ref"].ref
                else:
                    thresh = 0.02

            freqs = Xdatas[0]
            if "dB" in unit:
                indices = [
                    ind
                    for ind, y in enumerate(Ydatas[0])
                    if abs(y)
                    > max(10 * np.log10(thresh) + abs(np.nanmax(Ydatas[0])), 0)
                ]
            else:
                if Ydatas[0].size == 1:
                    indices = [0]
                else:
                    indices = [
                        ind
                        for ind, y in enumerate(Ydatas[0])
                        if abs(y) > abs(thresh * np.nanmax(Ydatas[0]))
                    ]
            xticks = np.unique(np.insert(freqs[indices], 0, 0))

            if is_auto_range:
                if len(xticks) > 1:
                    if x_min is None:
                        x_min = xticks[0]
                    else:
                        x_min = max(x_min, xticks[0])
                    if x_max is None:
                        x_max = xticks[-1]
                    else:
                        x_max = min(x_max, xticks[-1])
                else:
                    if x_min is None:
                        x_min = np.nanmin(freqs)
                    else:
                        x_min = max(x_min, np.nanmin(freqs))
                    if x_max is None:
                        x_max = np.nanmax(freqs)
                    else:
                        x_max = min(x_max, np.nanmax(freqs))

            else:
                if x_min is None:
                    x_min = np.nanmin(freqs)
                if x_max is None:
                    x_max = np.nanmax(freqs)

            x_min = x_min - x_max * 0.05
            x_max = x_max * 1.05

            if (
                len(xticks) == 0
                or (
                    len(xticks) > 20
                    and not axes_list[
                        list(result.keys()).index(axes_names[0])
                    ].is_components
                )
                or not is_auto_ticks
            ):
                xticks = None

            # Force bargraph for fft if type_graph not specified
            if type_plot is None:
                type_plot = "bargraph"

            # Option to draw fundamental harmonic in red
            if not fund_harm_dict:
                fund_harm = None
            else:
                # Activate the option only if main axis is in dict and only one Data is plotted
                if main_axis_name in fund_harm_dict and len(Ydatas) == 1:
                    fund_harm = fund_harm_dict[main_axis_name]
                else:
                    # Deactivate the option
                    fund_harm = None

            if is_export:
                return Xdatas, Ydatas, title, xlabel, ylabel, legends
            plot_2D(
                Xdatas,
                Ydatas,
                legend_list=legends,
                color_list=new_color_list,
                linestyle_list=linestyle_list,
                linewidth_list=linewidth_list,
                fig=fig,
                ax=ax,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                type_plot=type_plot,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                is_logscale_x=is_logscale_x,
                is_logscale_y=is_logscale_y,
                is_disp_title=is_disp_title,
                is_grid=is_grid,
                xticks=xticks,
                xticklabels=xticklabels,
                save_path=save_path,
                barwidth=barwidth,
                fund_harm=fund_harm,
                is_show_fig=is_show_fig,
                win_title=win_title,
                font_name=font_name,
                font_size_title=font_size_title,
                font_size_label=font_size_label,
                font_size_legend=font_size_legend,
                is_show_legend=is_show_legend,
                is_outside_legend=is_outside_legend,
                is_frame_legend=is_frame_legend,
                is_indlabels=is_indlabels,
            )

        else:
            # Force curve plot if type_plot not specified
            if type_plot is None:
                type_plot = "curve"
            annot = None
            # Hidden annotations
            if annotations is not None:
                try:
                    annot = []
                    for ii in range(len(self.get_axes(annotations[0])[0].get_values())):
                        if annotations[2] == "max":
                            index = np.argmax(np.take(result[self.symbol], ii, axis=0))
                            annot.append("main " + annotations[1].rstrip("s") + ": ")
                    # Keep only requested indices
                    annot = np.array(annot)[
                        axes_list[
                            [axis.name for axis in axes_list].index(annotations[0])
                        ].indices
                    ].tolist()
                    if len(overall_axes) != 0:
                        annot.insert(0, "Overall")
                except Exception:
                    pass

            if is_export:
                return Xdatas, Ydatas, title, xlabel, ylabel, legends
            plot_2D(
                Xdatas,
                Ydatas,
                legend_list=legends,
                color_list=new_color_list,
                fig=fig,
                ax=ax,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                type_plot=type_plot,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                is_logscale_x=is_logscale_x,
                is_logscale_y=is_logscale_y,
                is_disp_title=is_disp_title,
                is_grid=is_grid,
                xticks=xticks,
                xticklabels=xticklabels,
                barwidth=barwidth,
                linestyle_list=linestyle_list,
                linewidth_list=linewidth_list,
                save_path=save_path,
                is_show_fig=is_show_fig,
                win_title=win_title,
                font_name=font_name,
                font_size_title=font_size_title,
                font_size_label=font_size_label,
                font_size_legend=font_size_legend,
                is_show_legend=is_show_legend,
                is_outside_legend=is_outside_legend,
                is_frame_legend=is_frame_legend,
                is_indlabels=is_indlabels,
                annotations=annot,
            )

    # Inlined from Methods.SciDataTool.DataND.plot_2D_Data_Animated
    def plot_2D_Data_Animated(
        self,
        animated_axis,
        suptitle_ref,
        *param_list,
        nb_frames=50,
        fps=10,
        **param_dict,
    ):
        """Gen

        Parameters
        ----------
        animated_axis : str
            The field will be animated along this axis
        nb_frames : int
            number of frames used to build the gif
        fps: int
            frames displayed per second
        """
        # Relative import of DataPattern to prevent circular import
        DataPattern = import_class("DataPattern")

        # Making sure that we have the right argument for a plot2D
        plot_options = param_dict.copy()
        for param in PARAM_3D:
            if param in plot_options:
                del plot_options[param]

        # Detecting if animated axis is a DataPattern, if true changing the input given to the function
        for ax_obj in self.get_axes():
            if (
                ax_obj.name == animated_axis.split("[")[0]
                or animated_axis.split("[")[0] in fft_dict
                and fft_dict[animated_axis.split("[")[0]] == ax_obj.name
                or animated_axis.split("[")[0] in ifft_dict
                and ifft_dict[animated_axis.split("[")[0]] == ax_obj.name
            ):
                animated_axis_obj = ax_obj
                break

        if isinstance(animated_axis_obj, DataPattern):
            # Removing "[one_period]" as it is not available with a DataPattern
            animated_axis_unit = "{" + animated_axis.split("{")[1]
            animated_axis = animated_axis.split("[")[0] + animated_axis_unit

        if "freqs" in param_list or "wavenumber" in param_list:
            result = self.get_magnitude_along(
                animated_axis, *param_list, unit=param_dict["unit"]
            )
        else:
            result = self.get_along(animated_axis, *param_list, unit=param_dict["unit"])

        animated_axis_unit = "{" + animated_axis.split("{")[1]
        animated_axis = animated_axis.split("{")[0].split("[")[0]

        # Creating a list of frames that will need to create the animation
        if isinstance(animated_axis_obj, DataPattern):
            frames_list = animated_axis_obj.get_values()
            frames_list = [
                "[" + str(idx_frame) + "]" for idx_frame in range(len(frames_list))
            ]
            fps = 1
        else:
            value_max = np.nanmax(result[animated_axis])
            value_min = np.nanmin(result[animated_axis])
            variation_step = (value_max - value_min) / nb_frames

            frames_list = np.arange(
                start=value_min, stop=value_max, step=variation_step
            )
            frames_list = ["=" + str(frame) for frame in frames_list]

        # detecting if we are animating a regular plot (=> computing limit for y) or a "fft" plot (=> limit already set)
        if plot_options["y_min"] == None or plot_options["y_max"] == None:
            # Setting the options of the plot
            y_max = np.nanmax(result[self.symbol])
            y_min = np.nanmin(result[self.symbol])
            marge = (
                y_max - y_min
            ) * 0.05  # 5% of the height of plot to add to the border top/bottom of gif
            plot_options["y_min"] = np.nanmin(result[self.symbol]) - abs(marge)
            plot_options["y_max"] = np.nanmax(result[self.symbol]) + abs(marge)

        plot_options["is_show_fig"] = False

        # Getting the name of the gif
        save_path = plot_options["save_path"].replace(".png", ".gif")
        plot_options["save_path"] = None

        images = []  # List of images used to build the gif
        for val in frames_list:
            # plotting image
            self.plot_2D_Data(
                *param_list, animated_axis + val + animated_axis_unit, **plot_options
            )
            # Getting the figure generated with plot_2D_DATA
            fig = plt.gcf()

            # Adding the suptitle of the figure if there is one
            if suptitle_ref != "":
                fig.suptitle(suptitle_ref)

            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype="uint8")
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            images.append(image)

            # Creating the gif
            plt.close(fig)

        imageio.mimsave(save_path, images, format="GIF-PIL", fps=fps)

    # Inlined from Methods.SciDataTool.DataND.plot_3D_Data
    def plot_3D_Data(
        self,
        *arg_list,
        axis_data=None,
        is_norm=False,
        unit="SI",
        save_path=None,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        z_min=None,
        z_max=None,
        z_range=None,
        is_auto_ticks=True,
        is_auto_range=True,
        is_2D_view=True,
        is_contour=False,
        is_same_size=True,
        N_stem=100,
        fig=None,
        ax=None,
        is_show_fig=None,
        is_logscale_x=False,
        is_logscale_y=False,
        is_logscale_z=False,
        thresh=None,
        is_switch_axes=False,
        colormap="jet",
        win_title=None,
        font_name="arial",
        font_size_title=12,
        font_size_label=10,
        font_size_legend=8,
        xlabel=None,
        ylabel=None,
        zlabel=None,
        title=None,
        is_disp_title=True,
        type_plot=None,
        annotation_delim=None,
        marker_color="k",
        is_shading_flat=None,
        is_hide_annotation=False,
        is_filter_x=True,
        is_filter_y=True,
    ):
        """Plots a field as a function of two axes

        Parameters
        ----------
        data : Data
            a Data object
        *arg_list : list of str
            arguments to specify which axes to plot
        is_norm : bool
            boolean indicating if the field must be normalized
        unit : str
            unit in which to plot the field
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        x_min : float
            minimum value for the x-axis
        x_max : float
            maximum value for the x-axis
        y_min : float
            minimum value for the y-axis
        y_max : float
            maximum value for the y-axis
        z_min : float
            minimum value for the z-axis
        z_max : float
            maximum value for the z-axis
        z_range : float
            range to use for the z-axis
        is_auto_ticks : bool
            in fft, adjust ticks to freqs (deactivate if too close)
        is_auto_range : bool
            in fft, display up to 1% of max
        is_2D_view : bool
            True to plot Data in xy plane and put z as colormap
        is_contour : bool
            True to show contour line if is_fft = False and is_2D_view = True
        is_same_size : bool
            True to have all color blocks with same size in 2D view
        N_stem : int
            number of harmonics to plot (only for stem plots)
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            ax on which to plot the data
        is_show_fig : bool
            True to show figure after plot
        is_logscale_x : bool
            boolean indicating if the x-axis must be set in logarithmic scale
        is_logscale_y : bool
            boolean indicating if the y-axis must be set in logarithmic scale
        is_logscale_z : bool
            boolean indicating if the z-axis must be set in logarithmic scale
        thresh : float
            threshold for automatic fft ticks
        is_switch_axes : bool
            to switch x and y axes
        is_shading_flat : bool
            True to use flat shading instead of Gouraud for pcolormesh or bilinear for pcolor
        """

        # Dynamic import to avoid import loop
        DataPattern = import_class("DataPattern")

        if len(arg_list) == 1 and type(arg_list[0]) == tuple:
            arg_list = arg_list[0]  # if called from another script with *arg_list

        axes_names = [
            axis.name for axis in read_input_strings(arg_list, axis_data=axis_data)
        ]

        # Fix axes order
        arg_list_along = fix_axes_order(
            [axis.name for axis in self.get_axes()], arg_list
        )

        # Set unit
        if unit == "SI":
            unit = self.unit
        if "dB" in unit:
            if "ref" in self.normalizations:
                ref = self.normalizations["ref"].ref
            else:
                ref = 1
            unit_str = r"[" + unit + " re. " + str(ref) + " $" + self.unit + "$]"
        else:
            unit_str = r"$[" + unit + "]$"

        # Detect fft
        is_fft = False
        if any("wavenumber" in s for s in arg_list) or any(
            "freqs" in s for s in arg_list
        ):
            is_fft = True
            if zlabel is None:
                if self.symbol == "Magnitude":
                    zlabel = "Magnitude " + unit_str
                else:
                    zlabel = r"$|\widehat{" + self.symbol + "}|$ " + unit_str
        else:
            if zlabel is None:
                if is_norm:
                    zlabel = (
                        r"$\frac{"
                        + self.symbol
                        + "}{"
                        + self.symbol
                        + "_0}$ "
                        + unit_str
                    )
                else:
                    if self.symbol == "Magnitude":
                        zlabel = "Magnitude " + unit_str
                    else:
                        zlabel = r"$" + self.symbol + "$ " + unit_str

        # Extract field and axes
        if is_fft:
            if is_2D_view:
                result = self.get_magnitude_along(
                    *arg_list_along, axis_data=axis_data, unit=unit, is_norm=is_norm
                )
            else:
                result = self.get_harmonics(
                    N_stem,
                    *arg_list_along,
                    axis_data=axis_data,
                    unit=unit,
                    is_norm=is_norm,
                    is_flat=True,
                )
        else:
            result = self.get_along(
                *arg_list_along, axis_data=axis_data, unit=unit, is_norm=is_norm
            )

        if type_plot == "scatter" and not is_fft:
            is_fft = True
            is_same_size = False
        axes_list = result["axes_list"]
        axes_dict_other = result["axes_dict_other"]
        if axes_list[list(result.keys()).index(axes_names[0])].is_components:
            Xdata = np.linspace(
                0, len(result[axes_names[0]]) - 1, len(result[axes_names[0]])
            )
        else:
            Xdata = result[axes_names[0]]
        if axes_list[list(result.keys()).index(axes_names[1])].is_components:
            Ydata = np.linspace(
                0, len(result[axes_names[1]]) - 1, len(result[axes_names[1]])
            )
        else:
            Ydata = result[axes_names[1]]
        Zdata = result[self.symbol]
        if Xdata.size == 1:
            Zdata = Zdata[None, ...]
        if Ydata.size == 1:
            Zdata = Zdata[..., None]
        if is_fft and not is_2D_view:
            X_flat = Xdata
            Y_flat = Ydata
            Z_flat = Zdata

        else:
            Y_map, X_map = np.meshgrid(Ydata, Xdata)
            X_flat = X_map.flatten()
            Y_flat = Y_map.flatten()
            Z_flat = Zdata.flatten()
        if z_range is None:
            if z_min is None:
                if is_fft:
                    z_min = 0
                else:
                    if "dB" in unit:
                        z_min = np.floor(np.nanmin(Zdata))
                    else:
                        z_min = np.nanmin(Zdata)
            if z_max is None:
                z_max = np.nanmax(Zdata)
        else:
            if z_min is None and z_max is None:
                if "dB" in unit:
                    z_max = np.ceil(np.nanmax(Zdata))
                else:
                    z_max = np.nanmax(Zdata)
            if z_max is None:
                z_max = z_min + z_range
            if z_min is None:
                z_min = z_max - z_range

        # Build labels and titles
        title1 = self.name[0].capitalize() + self.name[1:] + " "
        axis = axes_list[list(result.keys()).index(axes_names[0])]
        if axis.name in axes_dict:
            name = axes_dict[axis.name]
        else:
            name = axis.name
        if axis.unit == "SI":
            axis_unit = unit_dict[axis.name]
            if xlabel is None:
                xlabel = name[0].capitalize() + name[1:] + " [" + axis_unit + "]"
        elif axis.unit in norm_dict:
            if xlabel is None:
                xlabel = norm_dict[axis.unit]
        else:
            axis_unit = axis.unit
            if xlabel is None:
                xlabel = name[0].capitalize() + name[1:] + " [" + axis_unit + "]"
        if (
            axis.name == "angle"
            and axis.unit == "°"
            and round(np.nanmax(axis.values) / 6) % 5 == 0
        ):
            xticks = [i * round(np.nanmax(axis.values) / 6) for i in range(7)]
        else:
            xticks = None
        if axis.is_components:
            xticklabels = result[axis.name]
            xticks = Xdata
            if annotation_delim is not None and annotation_delim in xticklabels[0]:
                annotations_x = np.array(
                    [label.split(annotation_delim)[1] for label in xticklabels]
                )
                xticklabels = np.array(
                    [label.split(annotation_delim)[0] for label in xticklabels]
                )
        else:
            xticklabels = None
            annotations_x = np.core.numeric.zeros_like(Xdata)

        axis = axes_list[list(result.keys()).index(axes_names[1])]
        if axis.name in axes_dict:
            name = axes_dict[axis.name]
        else:
            name = axis.name
        if axis.unit == "SI":
            axis_unit = unit_dict[axis.name]
            if ylabel is None:
                ylabel = name[0].capitalize() + name[1:] + " [" + axis_unit + "]"
        elif axis.unit in norm_dict:
            if ylabel is None:
                ylabel = norm_dict[axis.unit]
        else:
            axis_unit = axis.unit
            if ylabel is None:
                ylabel = name[0].capitalize() + name[1:] + " [" + axis_unit + "]"
        if (
            axis.name == "angle"
            and axis.unit == "°"
            and round(np.nanmax(axis.values) / 6) % 5 == 0
        ):
            yticks = [i * round(np.nanmax(axis.values) / 6) for i in range(7)]
        else:
            yticks = None
        if axis.is_components:
            yticklabels = result[axis.name]
            yticks = Ydata
            if annotation_delim is not None and annotation_delim in yticklabels[0]:
                annotations_y = np.array(
                    [label.split(annotation_delim)[1] for label in yticklabels]
                )
                yticklabels = np.array(
                    [label.split(annotation_delim)[0] for label in yticklabels]
                )
            else:
                annotations_y = np.core.numeric.zeros_like(Ydata)
        else:
            yticklabels = None
            annotations_y = np.core.numeric.zeros_like(Ydata)

        if is_fft and is_2D_view and annotation_delim is not None:
            _, annotations = np.meshgrid(annotations_y, annotations_x)
            annotations = annotations.flatten()
        else:
            annotations = None

        # Detect discontinuous axis (Norm_indices) to use flat shading
        if is_shading_flat is None:
            is_shading_flat = False
            flat_indices = []
            for axis in axes_list:
                if axis.unit in self.axes[axis.index].normalizations:
                    if isinstance(
                        self.axes[axis.index].normalizations[axis.unit], NormIndices
                    ):
                        is_shading_flat = True
                        flat_indices.append(axes_names.index(axis.name))

        title2 = "for "
        for axis in axes_list:
            if not (
                axis.extension
                in [
                    "whole",
                    "interval",
                    "oneperiod",
                    "antiperiod",
                    "smallestperiod",
                    "axis_data",
                    "list",
                ]
                and len(axis.values) > 1
                or (len(axis.values) == 1 and len(axes_list) == 1)
            ):
                is_display = True
            else:
                is_display = False
            if is_display:
                if axis.unit == "SI":
                    axis_unit = unit_dict[axis.name]
                elif axis.unit in norm_dict:
                    axis_unit = norm_dict[axis.unit]
                else:
                    axis_unit = axis.unit

                if isinstance(result[axis.name], str):
                    axis_str = result[axis.name]
                else:
                    if isinstance(result[axis.name][0], str):
                        axis_str = result[axis.name][0]
                    else:
                        if result[axis.name][0] > 10:
                            fmt = "{:.5g}"
                        else:
                            fmt = "{:.3g}"
                        axis_str = (
                            np.array2string(
                                result[axis.name],
                                formatter={"float_kind": fmt.format},
                            )
                            .replace(" ", ", ")
                            .replace("[", "")
                            .replace("]", "")
                            + " ["
                            + axis_unit
                            + "]"
                        )

                    index = None
                    if axis.is_pattern and len(axis.values) == 1:
                        for axis_obj in self.get_axes():
                            if axis_obj.name == axis.name:
                                index = axis.indices[0]

                    title2 += axis.name + "=" + axis_str
                    if index is not None:
                        title2 += " (slice " + str(index + 1) + "), "
                    else:
                        title2 += ", "

        title3 = ""
        for axis_name in axes_dict_other:
            is_display = True
            for axis in self.axes:
                if axis.name == axis_name:
                    if isinstance(axis, DataPattern) and len(axis.unique_indices) == 1:
                        is_display = False
            if is_display:
                if isinstance(axes_dict_other[axis_name][0], str):
                    axis_str = axes_dict_other[axis_name][0]
                else:
                    if axes_dict_other[axis_name][0] > 10:
                        fmt = "{:.5g}"
                    else:
                        fmt = "{:.3g}"
                    axis_str = (
                        np.array2string(
                            axes_dict_other[axis_name][0],
                            formatter={"float_kind": fmt.format},
                        ).replace(" ", ", ")
                        + " ["
                        + axes_dict_other[axis_name][1]
                        + "], "
                    )

                title3 += axis_name + "=" + axis_str

        if title2 == "for " and title3 == "":
            title2 = ""

        if title is None:
            title = title1 + title2 + title3
            title = title.rstrip(", ")

        title = title.replace("SI", "").replace(" []", "")
        xlabel = xlabel.replace("SI", "").replace(" []", "")  # Remove dimless units
        ylabel = ylabel.replace("SI", "").replace(" []", "")  # Remove dimless units
        zlabel = zlabel.replace("SI", "").replace(" []", "")  # Remove dimless units

        if is_fft:
            if thresh is None:
                if self.normalizations is not None and "ref" in self.normalizations:
                    thresh = self.normalizations["ref"].ref
                else:
                    thresh = 0.02

            if "dB" in unit:
                threshold = max(10 * np.log10(thresh) + abs(np.nanmax(Zdata)), 0)
            else:
                threshold = abs(thresh * np.nanmax(Zdata))
            indices_x = np.any(np.where(Zdata > threshold, True, False), axis=1)
            indices_y = np.any(np.where(Zdata > threshold, True, False), axis=0)

            if is_filter_x:
                xticks = Xdata[indices_x]
                if xticklabels is not None:
                    xticklabels = xticklabels[indices_x]
            else:
                xticks = Xdata
            if is_filter_y:
                yticks = Ydata[indices_y]
                if yticklabels is not None:
                    yticklabels = yticklabels[indices_y]
            else:
                yticks = Ydata

            annotation_threshold = None
            if annotations is not None:
                annotation_threshold = threshold
            if is_auto_range:
                if len(xticks) > 1:
                    if x_min is None:
                        x_min = xticks[0]
                    else:
                        x_min = max(x_min, xticks[0])
                    if x_max is None:
                        x_max = xticks[-1]
                    else:
                        x_max = min(x_max, xticks[-1])
                else:
                    if x_min is None:
                        x_min = np.nanmin(Xdata)
                    else:
                        x_min = max(x_min, np.nanmin(Xdata))
                    if x_max is None:
                        x_max = np.nanmax(Xdata)
                    else:
                        x_max = min(x_max, np.nanmax(Xdata))
                if len(yticks) > 1:
                    if y_min is None:
                        if (
                            axes_list[1].name == "wavenumber"
                            or axes_list[1].corr_name == "wavenumber"
                        ):
                            y_min = max(yticks[0], -100)
                        else:
                            y_min = 0
                    else:
                        y_min = max(y_min, yticks[0])
                    if y_max is None:
                        if (
                            axes_list[1].name == "wavenumber"
                            or axes_list[1].corr_name == "wavenumber"
                        ):
                            y_max = min(yticks[-1], 100)
                        else:
                            y_max = yticks[-1]
                    else:
                        y_max = min(y_max, yticks[-1])
                else:
                    if y_min is None:
                        y_min = max(np.nanmin(Ydata), -100)
                    else:
                        y_min = max(y_min, np.nanmin(Ydata))
                    if y_max is None:
                        y_max = min(np.nanmax(Ydata), 100)
                    else:
                        y_max = min(y_max, np.nanmax(Ydata))
            else:
                if x_min is None:
                    x_min = np.nanmin(Xdata)
                if x_max is None:
                    x_max = np.nanmax(Xdata)
                if y_min is None:
                    y_min = np.nanmin(Ydata)
                if y_max is None:
                    y_max = np.nanmax(Ydata)

            x_min = x_min - x_max * 0.05
            x_max = x_max * 1.05
            y_min = y_min - y_max * 0.2
            y_max = y_max * 1.2

            if len(xticks) == 0 or (
                np.logical_and(xticks > x_min, xticks < x_max).sum() > 20
                and not axes_list[
                    list(result.keys()).index(axes_names[0])
                ].is_components
            ):
                xticks = None
            if len(yticks) == 0 or (
                np.logical_and(yticks > y_min, yticks < y_max).sum() > 20
                and not axes_list[
                    list(result.keys()).index(axes_names[1])
                ].is_components
            ):
                yticks = None

            if not is_auto_ticks:
                xticks = None
                yticks = None
            if is_2D_view:
                if type_plot is None:
                    type_plot = "scatter"
                plot_4D(
                    X_flat,
                    Y_flat,
                    Z_flat,
                    Sdata=None,
                    is_same_size=is_same_size,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    z_max=z_max,
                    z_min=z_min,
                    title=title,
                    xticks=xticks,
                    yticks=yticks,
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    zlabel=zlabel,
                    fig=fig,
                    ax=ax,
                    type_plot=type_plot,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_logscale_z=is_logscale_z,
                    is_switch_axes=is_switch_axes,
                    colormap=colormap,
                    win_title=win_title,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                    is_grid=True,
                    is_disp_title=is_disp_title,
                    annotations=annotations,
                    annotation_threshold=annotation_threshold,
                    marker_color=marker_color,
                    is_hide_annotation=is_hide_annotation,
                )
            else:
                plot_3D(
                    X_flat,
                    Y_flat,
                    Z_flat,
                    fig=fig,
                    ax=ax,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    z_min=0,
                    z_max=z_max,
                    title=title,
                    xticks=xticks,
                    yticks=yticks,
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    zlabel=zlabel,
                    type_plot="stem",
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_logscale_z=is_logscale_z,
                    is_switch_axes=is_switch_axes,
                    colormap=colormap,
                    win_title=win_title,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                    is_disp_title=is_disp_title,
                )
        else:
            if x_min is None:
                x_min = np.nanmin(Xdata)
            if x_max is None:
                x_max = np.nanmax(Xdata)
            if y_min is None:
                y_min = np.nanmin(Ydata)
            if y_max is None:
                y_max = np.nanmax(Ydata)
            if is_2D_view:
                if type_plot is None:
                    type_plot = "pcolor"
                if is_shading_flat and type_plot == "pcolormesh":
                    # 0.5 offset
                    if 0 in flat_indices:
                        Xdata = Xdata - 0.5
                        x_min -= 0.5
                        x_max -= 0.5
                    if 1 in flat_indices:
                        Ydata = Ydata - 0.5
                        y_min -= 0.5
                        y_max -= 0.5
                    Ydata, Xdata = np.meshgrid(Ydata, Xdata)
                if type_plot == "pcolor":
                    Zdata = Zdata.T
                plot_3D(
                    Xdata,
                    Ydata,
                    Zdata,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    z_max=z_max,
                    z_min=z_min,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    zlabel=zlabel,
                    title=title,
                    xticks=xticks,
                    yticks=yticks,
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    fig=fig,
                    ax=ax,
                    type_plot=type_plot,
                    is_contour=is_contour,
                    is_shading_flat=is_shading_flat,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_logscale_z=is_logscale_z,
                    is_switch_axes=is_switch_axes,
                    colormap=colormap,
                    win_title=win_title,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                    is_disp_title=is_disp_title,
                )
            else:
                plot_3D(
                    X_map,
                    Y_map,
                    Zdata,
                    fig=fig,
                    ax=ax,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    z_min=z_min,
                    z_max=z_max,
                    title=title,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    zlabel=zlabel,
                    yticks=yticks,
                    xticklabels=xticklabels,
                    yticklabels=yticklabels,
                    type_plot="surf",
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_logscale_z=is_logscale_z,
                    is_switch_axes=is_switch_axes,
                    colormap=colormap,
                    win_title=win_title,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                    is_disp_title=is_disp_title,
                    is_shading_flat=is_shading_flat,
                )

    # Inlined from Methods.SciDataTool.DataND.plot_3D_Data_Animated
    def plot_3D_Data_Animated(
        self,
        animated_axis,
        suptitle_ref,
        *param_list,
        nb_frames=50,
        fps=10,
        **param_dict,
    ):
        """Gen

        Parameters
        ----------
        animated_axis : str
            The field will be animated along this axis
        nb_frames : int
            number of frames used to build the gif
        fps: int
            frames displayed per second
        """

        # Relative import of DataPattern to prevent circular import
        DataPattern = import_class("DataPattern")

        # Making sure that we have the right argument for a plot3D
        plot_options = param_dict.copy()
        for param in PARAM_2D:
            if param in plot_options:
                del plot_options[param]

        # Detecting if animated axis is a DataPattern, if true changing the input given to the function
        for ax_obj in self.get_axes():
            if ax_obj.name in ifft_dict:
                if ifft_dict[ax_obj.name] == animated_axis.split("[")[0]:
                    animated_axis_obj = ax_obj
                    break
            else:
                if ax_obj.name == animated_axis.split("[")[0]:
                    animated_axis_obj = ax_obj
                    break

        if isinstance(animated_axis_obj, DataPattern):
            # Removing one_period as it is not available with a DataPattern
            animated_axis_unit = "{" + animated_axis.split("{")[1]
            animated_axis = animated_axis.split("[")[0] + animated_axis_unit

        if "freqs" in param_list or "wavenumber" in param_list:
            result = self.get_magnitude_along(animated_axis, *param_list)
        else:
            result = self.get_along(animated_axis, *param_list)

        animated_axis_unit = "{" + animated_axis.split("{")[1]
        animated_axis = animated_axis.split("{")[0].split("[")[0]

        # Creating a list of frames that will need to create the animation
        if isinstance(animated_axis_obj, DataPattern):
            frames_list = animated_axis_obj.get_values()
            frames_list = [
                "[" + str(idx_frame) + "]" for idx_frame in range(len(frames_list))
            ]
            fps = 1
        else:
            value_max = np.nanmax(result[animated_axis])
            value_min = np.nanmin(result[animated_axis])
            variation_step = (value_max - value_min) / nb_frames

            frames_list = np.arange(
                start=value_min, stop=value_max, step=variation_step
            )
            frames_list = ["=" + str(frame) for frame in frames_list]

        plot_options["is_show_fig"] = False

        # Getting the name of the gif
        save_path = plot_options["save_path"].replace(".png", ".gif")
        plot_options["save_path"] = None

        images = []  # List of images used to build the gif
        for val in frames_list:
            # plotting image
            self.plot_3D_Data(
                *param_list, animated_axis + val + animated_axis_unit, **plot_options
            )
            # Getting the figure generated with plot_2D_DATA
            fig = plt.gcf()

            # Adding the suptitle of the figure if there is one
            if suptitle_ref != "":
                fig.suptitle(suptitle_ref)

            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype="uint8")
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            images.append(image)

            # Creating the gif
            plt.close(fig)

        imageio.mimsave(save_path, images, format="GIF-PIL", fps=fps)
