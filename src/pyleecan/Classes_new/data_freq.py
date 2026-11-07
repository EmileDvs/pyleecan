# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataFreq.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.Load.import_class import import_class as _pyleecan_import_class
from ..Functions.SciDataTool import AxisError
from ..Functions.SciDataTool.sum_convolution import (
    get_conv_amplitudes,
    get_conv_indices,
    get_sum_amplitudes,
    get_sum_indices,
)
from .data_1d import Data1D
from .data_nd import DataND


@dataclass(eq=False)
class DataFreq(DataND):
    """Class for fields defined in Fourier space

    Attributes
    ----------
    """

    # Inlined from Methods.SciDataTool.DataFreq.conv
    def conv(
        self,
        other,
        f_min=None,
        f_max=np.inf,
        tol_freq=1e-4,
        name=None,
        symbol=None,
        unit=None,
        normalizations=None,
    ):
        """Convolution of two DataFreq objects

        Parameters
        ----------
        self : DataFreq
            A DataFreq object
        other : DataFreq
            Another DataFreq object
        f_min: float
            Minimum frequency of convolved spectrum [Hz]
        f_max: float
            Maximum frequency of convolved spectrum [Hz]
        tol_freq: float
            Absolute tolerance value to filter harmonic orders by their frequency value
        name: str
            name
        symbol: str
            symbol
        unit: str
            unit
        normalizations: {Normalization}
            Dict of normalization objects

        Returns
        -------
        result : DataFreq
            DataFreq object resulting from convolution of both DataFreq objects
        """

        if not isinstance(other, type(self)):
            raise Exception("other is not a DataFreq object")

        if len(self.axes) > 1:
            raise Exception("self contains more than one axis")

        if len(other.axes) > 1:
            raise Exception("other contains more than one axis")

        if self.axes[0].name != "freqs":
            raise Exception("self axis is not frequency axis")
        else:
            freqs1 = self.axes[0].get_values()
            if np.any(freqs1) < 0:
                raise Exception("self contains negative frequency values")

        if other.axes[0].name != "freqs":
            raise Exception("other axis is not frequency axis")
        else:
            freqs2 = other.axes[0].get_values()
            if np.any(freqs2) < 0:
                raise Exception("other contains negative frequency values")

        # Fill metadata
        if name is None:
            name = self.name
        if symbol is None:
            symbol = self.symbol
        if unit is None:
            unit = self.unit
        if normalizations is None:
            normalizations = self.normalizations

        # Compute spectrum orders resulting from convolution
        freqs_un, I0a, I0b, I1, I2 = get_conv_indices(
            freqs1, freqs2, f_min, f_max, tol_freq
        )

        # Compute spectrum amplitudes resulting from convolution
        amp = get_conv_amplitudes(self.values, other.values, I0a, I0b, I1, I2)

        # Create Frequency axis
        Freqs = self.axes[0].copy()
        Freqs.values = freqs_un

        # Create DataFreq resulting from convolution
        result = type(self)(
            name=name,
            unit=unit,
            symbol=symbol,
            axes=[Freqs],
            values=amp,
            normalizations=normalizations,
        )

        return result

    # Inlined from Methods.SciDataTool.DataFreq.freq_to_time
    def freq_to_time(self):
        """Performs the inverse Fourier Transform and stores the resulting field in a DataTime object.
        Parameters
        ----------
        self : DataFreq
            a DataFreq object
        Returns
        -------
        a DataTime object
        """

        # Dynamic import to avoid loop
        DataTime = _pyleecan_import_class("pyleecan.Classes", "DataTime")
        DataPattern = _pyleecan_import_class("pyleecan.Classes", "DataPattern")

        axes_str = []
        for i, axis in enumerate(self.axes):
            if axis.is_components:
                axis_str = axis.name + str(list(range(len(axis.values))))
            elif axis.name == "freqs":
                axis_str = "time[smallestperiod]"
            elif axis.name == "wavenumber":
                axis_str = "angle[smallestperiod]"
            elif isinstance(axis, DataPattern):
                axis_str = axis.name + "[pattern]"
            else:
                axis_str = axis.name + "[smallestperiod]"
            axes_str.append(axis_str)
        if axes_str == [axis.name for axis in self.axes]:
            raise AxisError(
                "No available axis is compatible with fft (should be time or angle)"
            )
        else:
            results = self.get_along(*axes_str)
            values = results.pop(self.symbol)
            Axes = []
            for axis in self.axes:
                if axis.name == "freqs":
                    axis_new = Data1D(
                        name="time",
                        is_components=False,
                        values=results["time"],
                        unit="s",
                        symmetries=axis.symmetries.copy(),
                        normalizations=axis.normalizations.copy(),
                    )
                elif axis.name == "wavenumber":
                    axis_new = Data1D(
                        name="angle",
                        is_components=False,
                        values=results["angle"],
                        unit="rad",
                        symmetries=axis.symmetries.copy(),
                        normalizations=axis.normalizations.copy(),
                    )
                else:
                    axis_new = axis.copy()
                Axes.append(axis_new)

            return DataTime(
                name=self.name,
                unit=self.unit,
                symbol=self.symbol,
                axes=Axes,
                values=values,
                is_real=self.is_real,
                normalizations=self.normalizations.copy(),
            )

    # Inlined from Methods.SciDataTool.DataFreq.sum
    def sum(
        self,
        other,
        tol_freq=1e-4,
        name=None,
        symbol=None,
        unit=None,
        normalizations=None,
    ):
        """Merge two DataFreq objects

        Parameters
        ----------
        self : DataFreq
            A DataFreq object
        other : DataFreq
            Another DataFreq object
        tol_freq: float
            Absolute tolerance value to filter harmonic orders by their frequency value
        name: str
            name
        symbol: str
            symbol
        unit: str
            unit
        normalizations: {Normalization}
            Dict of normalization objects

        Returns
        -------
        result : Spectrum
            DataFreq object resulting from summing both DataFreq objects
        """

        if not isinstance(other, type(self)):
            raise Exception("other is not a DataFreq object")

        if len(self.axes) > 1:
            raise Exception("self contains more than one axis")

        if len(other.axes) > 1:
            raise Exception("other contains more than one axis")

        if self.axes[0].name != "freqs":
            raise Exception("self axis is not frequency axis")
        else:
            freqs1 = self.axes[0].get_values()
            if np.any(freqs1) < 0:
                raise Exception("self contains negative frequency values")

        if other.axes[0].name != "freqs":
            raise Exception("other axis is not frequency axis")
        else:
            freqs2 = other.axes[0].get_values()
            if np.any(freqs2) < 0:
                raise Exception("other contains negative frequency values")

        # Fill metadata
        if name is None:
            name = self.name
        if symbol is None:
            symbol = self.symbol
        if unit is None:
            unit = self.unit
        if normalizations is None:
            normalizations = self.normalizations

        # Compute spectrum orders resulting from convolution
        freqs_un, I0b = get_sum_indices(freqs1, freqs2, tol_freq)

        # Compute spectrum amplitudes resulting from convolution
        amp = get_sum_amplitudes(self.values, other.values, I0b)

        # Create Frequency axis
        Freqs = self.axes[0].copy()
        Freqs.values = freqs_un

        # Create DataFreq resulting from convolution
        result = type(self)(
            name=name,
            unit=unit,
            symbol=symbol,
            axes=[Freqs],
            values=amp,
            normalizations=normalizations,
        )

        return result

    # Inlined from Methods.SciDataTool.DataFreq.to_datadual
    def to_datadual(self, datatime=None):
        """Creates a DataDual object.
        Parameters
        ----------
        self : DataFreq
            a DataFreq object
        datatime : DataTime
            a DataTime object
        Returns
        -------
        a DataDual object
        """

        # Dynamic import to avoid loop
        DataDual = _pyleecan_import_class("pyleecan.Classes", "DataDual")

        # Fill DataDual object with fourier data
        datadual = DataDual(
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            normalizations=self.normalizations.copy(),
            axes_df=self.axes,
            values_df=self.values,
        )

        # Add time/space data (from input or using ifft)
        if datatime is None:
            datatime = self.freq_to_time()
        datadual.axes_dt = datatime.axes
        datadual.values_dt = datatime.values

        return datadual
