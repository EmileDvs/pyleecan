# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/SciDataTool/DataND.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/SciDataTool/DataND
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - plot_2D_Data: import name 'axes_dict' refers to different sources (pyleecan.Functions.SciDataTool.axes_dict and pyleecan.Functions.SciDataTool.Plot.axes_dict)
# - plot_3D_Data: import name 'axes_dict' refers to different sources (pyleecan.Functions.SciDataTool.axes_dict and pyleecan.Functions.SciDataTool.Plot.axes_dict)

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import set_array, check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Data import Data

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.SciDataTool.DataND.plot_2D_Data import plot_2D_Data
from pyleecan.Methods.SciDataTool.DataND.plot_3D_Data import plot_3D_Data
import numpy as np, csv, imageio, matplotlib.pyplot as plt
from pyleecan.Functions.SciDataTool.derivation_integration import (
    antiderivate,
    derivate,
    integrate,
    integrate_local,
    integrate_local_pattern,
)
from pyleecan.Functions.SciDataTool.sum_mean import (
    my_mean,
    my_sum,
    root_mean_square,
    root_sum_square,
)
from pyleecan.Functions.SciDataTool import (
    axes_dict,
    rev_axes_dict,
    NormError,
    UnitError,
    AxisError,
)
from pyleecan.Functions.SciDataTool.conversions import (
    convert as convert_unit,
    to_dB,
    to_dBA,
    get_unit_derivate,
    get_unit_integrate,
    convert,
    to_noct,
)
from pyleecan.Functions.SciDataTool.symmetries import (
    rebuild_symmetries,
    rebuild_symmetries as rebuild_symmetries_fct,
)
from pyleecan.Functions.SciDataTool.interpolations import (
    get_interpolation,
    get_interpolation_step,
    get_common_base,
)
from pyleecan.Classes._check import check_dimensions, check_var
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.SciDataTool.change_referential import (
    change_referential_spectrum,
    change_referential_waveform,
)
from pyleecan.Methods.SciDataTool.DataND.export_along import format_matrix
from os.path import join
from pyleecan.Functions.SciDataTool.Plot import (
    unit_dict,
    PARAM_3D,
    fft_dict,
    ifft_dict,
    PARAM_2D,
)
from pyleecan.Functions.SciDataTool.filter_spectral_leakage import (
    filter_spectral_leakage as filter_spectral_leakage_fct,
)
from pyleecan.Functions.SciDataTool.fft_functions import comp_fftn, comp_ifftn
from pyleecan.Functions.SciDataTool.fix_axes_order import fix_axes_order
from pyleecan.Functions.SciDataTool.parser import read_input_strings
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Functions.SciDataTool.omp import comp_undersampled_axe, omp


from pyleecan.Classes._check import InitUnKnowClassError


class DataND(Data):
    """Abstract class for fields (time or frequency domain)"""

    VERSION = 1

    # cf Methods.SciDataTool.DataND._apply_operations
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

    # cf Methods.SciDataTool.DataND._comp_axes
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
                if axis_name in axes_dict.keys():
                    for index, axis in enumerate(self.axes):
                        if axis.name == axes_dict[axis_name][0]:
                            axis_requested.corr_name = axes_dict[axis_name][0]
                            axis_requested.corr_unit = axes_dict[axis_name][2]
                            axis_requested.is_components = axis.is_components
                            axis_requested.operation = (
                                axes_dict[axis_name][0] + "_to_" + axis_name
                            )
                            axis_requested.transform = axes_dict[axis_name][1]
                            transforms.append(axes_dict[axis_name][1])
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

    # cf Methods.SciDataTool.DataND._convert
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

    # cf Methods.SciDataTool.DataND._extract_slices
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

    # cf Methods.SciDataTool.DataND._extract_slices_fft
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

    # cf Methods.SciDataTool.DataND._get_field
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
                self.axes[axis_requested.index].symmetries = dict()

        return values

    # cf Methods.SciDataTool.DataND._get_freqs
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

    # cf Methods.SciDataTool.DataND._interpolate
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

    # cf Methods.SciDataTool.DataND._rebuild_symmetries
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

    # cf Methods.SciDataTool.DataND._set_values
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

    # cf Methods.SciDataTool.DataND.change_referential
    def change_referential(
        self,
        rotation_speed,
        is_waveform,
        atol=1e-9,
        axes_list_change=list(),
        arg_list=list(),
        freqs_new=np.array([]),
        I1=np.array([]),
        Irf_un=np.array([]),
        sym_t_new=dict(),
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

        Data1D = import_class("pyleecan.Classes", "Data1D")
        DataLinspace = import_class("pyleecan.Classes", "DataLinspace")
        DataPattern = import_class("pyleecan.Classes", "DataPattern")

        if is_waveform:
            DataClass = import_class("pyleecan.Classes", "DataTime")
        else:
            DataClass = import_class("pyleecan.Classes", "DataFreq")

        # Get axes list
        axes_list = self.get_axes()
        axes_name = [axis.name for axis in axes_list]

        if len(arg_list) == 0:
            # Get fft along frequency axis (keep other axes)
            arg_list = list()
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
            axes_list_change = list()
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
                        symmetries=dict(),  # Don't keep time symmetries, FFT inverse requests axis_data
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

    # cf Methods.SciDataTool.DataND.compare_along
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

    # cf Methods.SciDataTool.DataND.compare_magnitude_along
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

    # cf Methods.SciDataTool.DataND.compare_phase_along
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

    # cf Methods.SciDataTool.DataND.export_along
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
            module = __import__(
                "pyleecan.Classes.DataPattern", fromlist=["DataPattern"]
            )
            DataPattern = module.DataPattern
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
                    join(save_path, file_name_i + "." + file_format), "w+", newline=""
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
                            second_line = format_matrix(
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
                        matrix = format_matrix(
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
                            second_line = format_matrix(
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
                        matrix = format_matrix(
                            np.column_stack(
                                (results[axes_list_new[0].name].T, field)
                            ).astype("str"),
                            CHAR_LIST,
                        )
                        csvWriter.writerows(matrix)

        else:
            raise Exception("export format not supported")

    # cf Methods.SciDataTool.DataND.filter_spectral_leakage
    def filter_spectral_leakage(
        self,
        freqs_th,
        axes_list_filt=list(),
        arg_list=list(),
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

        module = __import__("pyleecan.Classes.DataFreq", fromlist=["DataFreq"])
        DataFreq = module.DataFreq

        module = __import__("pyleecan.Classes.DataPattern", fromlist=["DataPattern"])
        DataPattern = module.DataPattern

        module = __import__("pyleecan.Classes.Data1D", fromlist=["Data1D"])
        Data1D = module.Data1D

        if len(axes_list_filt) == 0 or len(arg_list) == 0:
            # Get fft along frequency axis (keep other axes)
            arg_list = list()  # Reinstantiate a different list
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
            axes_list_filt = list()  # Reinstantiate a different list
            axes_list_filt.append(
                Data1D(
                    name="freqs",
                    unit="Hz",
                    values=freqs_th_store,
                    normalizations=axes_list[0].normalizations,
                    symmetries=dict(),
                )
            )

            if "wavenumber" in result:
                axes_list_filt.append(
                    Data1D(
                        name="wavenumber",
                        unit="dimless",
                        values=result["wavenumber"],
                        normalizations=axes_list[1].normalizations,
                        symmetries=dict(),
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

    # cf Methods.SciDataTool.DataND.get_along
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

    # cf Methods.SciDataTool.DataND.get_axes
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

    # cf Methods.SciDataTool.DataND.get_data_along
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
        module = __import__("pyleecan.Classes." + Data_type, fromlist=[Data_type])
        DataClass = getattr(module, Data_type)

        for axis_name in axes_name_new:
            if not isinstance(results[axis_name], str):
                for i, axis in enumerate(self.axes):
                    if axis.name == axis_name:
                        index = i
                        name = axis.name
                        is_components = axis.is_components
                        axis_values = results[axis_name]
                        ax_unit = axis.unit
                    elif axis_name in axes_dict:
                        if axes_dict[axis_name][0] == axis.name:
                            index = i
                            name = axis_name
                            is_components = axis.is_components
                            axis_values = results[axis_name]
                            ax_unit = axes_dict[axis_name][2]
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
                    symmetries = dict()
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

    # cf Methods.SciDataTool.DataND.get_harmonics
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

    # cf Methods.SciDataTool.DataND.get_magnitude_along
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

    # cf Methods.SciDataTool.DataND.get_phase_along
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

    # cf Methods.SciDataTool.DataND.has_period
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

    # cf Methods.SciDataTool.DataND.orthogonal_mp
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
        assert (
            nombre_axes == 2 or nombre_axes == 1
        ), "Dimension error: {} not in {1,2}".format(nombre_axes)

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

    # cf Methods.SciDataTool.DataND.plot_2D_Data
    plot_2D_Data = plot_2D_Data

    # cf Methods.SciDataTool.DataND.plot_2D_Data_Animated
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
        module = __import__("pyleecan.Classes.DataPattern", fromlist=["DataPattern"])
        DataPattern = module.DataPattern

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

        images = list()  # List of images used to build the gif
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

    # cf Methods.SciDataTool.DataND.plot_3D_Data
    plot_3D_Data = plot_3D_Data

    # cf Methods.SciDataTool.DataND.plot_3D_Data_Animated
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
        module = __import__("pyleecan.Classes.DataPattern", fromlist=["DataPattern"])
        DataPattern = module.DataPattern

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

        images = list()  # List of images used to build the gif
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        axes=None,
        FTparameters=-1,
        values=None,
        is_real=True,
        symbol="",
        name="",
        unit="",
        normalizations=-1,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "axes" in list(init_dict.keys()):
                axes = init_dict["axes"]
            if "FTparameters" in list(init_dict.keys()):
                FTparameters = init_dict["FTparameters"]
            if "values" in list(init_dict.keys()):
                values = init_dict["values"]
            if "is_real" in list(init_dict.keys()):
                is_real = init_dict["is_real"]
            if "symbol" in list(init_dict.keys()):
                symbol = init_dict["symbol"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
            if "normalizations" in list(init_dict.keys()):
                normalizations = init_dict["normalizations"]
        # Set the properties (value check and convertion are done in setter)
        self.axes = axes
        self.FTparameters = FTparameters
        self.values = values
        self.is_real = is_real
        # Call Data init
        super(DataND, self).__init__(
            symbol=symbol, name=name, unit=unit, normalizations=normalizations
        )
        # The class is frozen (in Data init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        DataND_str = ""
        # Get the properties inherited from Data
        DataND_str += super(DataND, self).__str__()
        if len(self.axes) == 0:
            DataND_str += "axes = []" + linesep
        for ii in range(len(self.axes)):
            tmp = self.axes[ii].__str__().replace(linesep, linesep + "\t") + linesep
            DataND_str += "axes[" + str(ii) + "] =" + tmp + linesep + linesep
        DataND_str += "FTparameters = " + str(self.FTparameters) + linesep
        DataND_str += (
            "values = "
            + linesep
            + str(self.values).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        DataND_str += "is_real = " + str(self.is_real) + linesep
        return DataND_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Data
        if not super(DataND, self).__eq__(other):
            return False
        if other.axes != self.axes:
            return False
        if other.FTparameters != self.FTparameters:
            return False
        if not np.array_equal(other.values, self.values):
            return False
        if other.is_real != self.is_real:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Data
        diff_list.extend(
            super(DataND, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.axes is None and self.axes is not None) or (
            other.axes is not None and self.axes is None
        ):
            diff_list.append(name + ".axes None mismatch")
        elif self.axes is None:
            pass
        elif len(other.axes) != len(self.axes):
            diff_list.append("len(" + name + ".axes)")
        else:
            for ii in range(len(other.axes)):
                diff_list.extend(
                    self.axes[ii].compare(
                        other.axes[ii],
                        name=name + ".axes[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if other._FTparameters != self._FTparameters:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._FTparameters)
                    + ", other="
                    + str(other._FTparameters)
                    + ")"
                )
                diff_list.append(name + ".FTparameters" + val_str)
            else:
                diff_list.append(name + ".FTparameters")
        if not np.array_equal(other.values, self.values):
            diff_list.append(name + ".values")
        if other._is_real != self._is_real:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_real)
                    + ", other="
                    + str(other._is_real)
                    + ")"
                )
                diff_list.append(name + ".is_real" + val_str)
            else:
                diff_list.append(name + ".is_real")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Data
        S += super(DataND, self).__sizeof__()
        if self.axes is not None:
            for value in self.axes:
                S += getsizeof(value)
        if self.FTparameters is not None:
            for key, value in self.FTparameters.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.values)
        S += getsizeof(self.is_real)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from Data
        DataND_dict = super(DataND, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        if self.axes is None:
            DataND_dict["axes"] = None
        else:
            DataND_dict["axes"] = list()
            for obj in self.axes:
                if obj is not None:
                    DataND_dict["axes"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs,
                        )
                    )
                else:
                    DataND_dict["axes"].append(None)
        DataND_dict["FTparameters"] = (
            self.FTparameters.copy() if self.FTparameters is not None else None
        )
        if self.values is None:
            DataND_dict["values"] = None
        else:
            if type_handle_ndarray == 0:
                DataND_dict["values"] = self.values.tolist()
            elif type_handle_ndarray == 1:
                DataND_dict["values"] = self.values.copy()
            elif type_handle_ndarray == 2:
                DataND_dict["values"] = self.values
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        DataND_dict["is_real"] = self.is_real
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        DataND_dict["__class__"] = "DataND"
        return DataND_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.axes is None:
            axes_val = None
        else:
            axes_val = list()
            for obj in self.axes:
                axes_val.append(obj.copy())
        if self.FTparameters is None:
            FTparameters_val = None
        else:
            FTparameters_val = self.FTparameters.copy()
        if self.values is None:
            values_val = None
        else:
            values_val = self.values.copy()
        is_real_val = self.is_real
        symbol_val = self.symbol
        name_val = self.name
        unit_val = self.unit
        if self.normalizations is None:
            normalizations_val = None
        else:
            normalizations_val = dict()
            for key, obj in self.normalizations.items():
                normalizations_val[key] = obj.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            axes=axes_val,
            FTparameters=FTparameters_val,
            values=values_val,
            is_real=is_real_val,
            symbol=symbol_val,
            name=name_val,
            unit=unit_val,
            normalizations=normalizations_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.axes = None
        self.FTparameters = None
        self.values = None
        self.is_real = None
        # Set to None the properties inherited from Data
        super(DataND, self)._set_None()

    def _get_axes(self):
        """getter of axes"""
        if self._axes is not None:
            for obj in self._axes:
                if obj is not None:
                    obj.parent = self
        return self._axes

    def _set_axes(self, value):
        """setter of axes"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "axes"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("axes", value, "[Data]")
        self._axes = value

    axes = property(
        fget=_get_axes,
        fset=_set_axes,
        doc="""List of the Data1D objects corresponding to the axes

        :Type: [Data]
        """,
    )

    def _get_FTparameters(self):
        """getter of FTparameters"""
        return self._FTparameters

    def _set_FTparameters(self, value):
        """setter of FTparameters"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("FTparameters", value, "dict")
        self._FTparameters = value

    FTparameters = property(
        fget=_get_FTparameters,
        fset=_set_FTparameters,
        doc="""Tunable parameters for the Fourier Transforms

        :Type: dict
        """,
    )

    def _get_values(self):
        """getter of values"""
        return self._values

    values = property(
        fget=_get_values,
        fset=_set_values,
        doc="""Values of the field

        :Type: ndarray
        """,
    )

    def _get_is_real(self):
        """getter of is_real"""
        return self._is_real

    def _set_is_real(self, value):
        """setter of is_real"""
        check_var("is_real", value, "bool")
        self._is_real = value

    is_real = property(
        fget=_get_is_real,
        fset=_set_is_real,
        doc="""To indicate if the signal is real (use only positive frequencies)

        :Type: bool
        """,
    )
