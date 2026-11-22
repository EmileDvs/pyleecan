# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataFreq.csv
"""Generated experimental dataclass; do not edit by hand."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.errors import AxisError
from ...Functions_new.SciDataTool.dqh_transformation import dqh2n_freq as dqh2n_fct
from ...Functions_new.SciDataTool.dqh_transformation import get_phase_dir_DataFreq
from ...Functions_new.SciDataTool.dqh_transformation import n2dqh_freq as n2dqh_fct
from ...Functions_new.SciDataTool.sum_convolution import (
    get_conv_amplitudes,
    get_conv_indices,
    get_sum_amplitudes,
    get_sum_indices,
)
from ...Functions_new.Winding.gen_phase_list import gen_name
from .data import Data
from .data_1d import Data1D
from .data_nd import DataND
from .normalization import Normalization

if TYPE_CHECKING:
    from .data import Data
    from .data_time import DataTime
    from .normalization import Normalization


@dataclass(eq=False)
class DataFreq(DataND):
    """Class for fields defined in Fourier space

    Attributes
    ----------
    """

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.DataFreq.conv
    def conv(
        self,
        other: DataFreq,
        f_min: float | None = None,
        f_max: float = np.inf,
        tol_freq: float = 1e-4,
        name: str | None = None,
        symbol: str | None = None,
        unit: str | None = None,
        normalizations: dict[str, Normalization] | None = None,
    ) -> DataFreq:
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

        # Local import: avoids circular imports
        from .data_pattern import DataPattern
        from .data_time import DataTime

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
            Axes: list[Data] = []
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
        other: DataFreq,
        tol_freq: float = 1e-4,
        name: str | None = None,
        symbol: str | None = None,
        unit: str | None = None,
        normalizations: dict[str, Normalization] | None = None,
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
    def to_datadual(self, datatime: DataTime | None = None):
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

        # Local import: avoids circular imports
        from .data_dual import DataDual

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

    # Inlined from Methods.SciDataTool.DataFreq.n2dqh
    def n2dqh(
        self,
        current_dir: int,
        felec: float,
        is_dqh_rms: bool = True,
        phase_dir: int | None = None,
    ) -> DataFreq:
        """n phases to dqh equivalent coordinate transformation of DataFreq/DataTime object

        Parameters
        ----------
        self : DataFreq/DataTime
            data object containing values over freqs and phase axes
        is_dqh_rms : boolean
            True to return dq currents in rms value (Pyleecan convention), False to return peak values
        phase_dir: int
            direction of phase distribution: +/-1 (-1 clockwise) to enforce
        current_dir: int
            direction of current waveform: +/-1 (-1 clockwise) to enforce
        felec: float
            fundamental electrical frequency [Hz]

        Returns
        -------
        data_dqh : DataFreq
            data object transformed in dqh frame

        """

        if phase_dir is None:
            # Check if input data object is compliant with dqh transformation
            # and get phase_dir from data object
            phase_dir = get_phase_dir_DataFreq(self)

        # Get values for one time period converted in electrical angle and for all phases
        result_n = self.get_along("freqs", "phase", is_squeeze=False)

        # Convert values to dqh frame
        Z_dqh, freqs_dqh = n2dqh_fct(
            Z_n=result_n[self.symbol],
            freqs=result_n["freqs"],
            phase_dir=phase_dir,
            current_dir=current_dir,
            felec=felec,
            is_dqh_rms=is_dqh_rms,
        )

        # Create frequency axis
        norm_freq: dict[str, Normalization] = {}
        ax_freq = self.axes[0]
        if ax_freq.normalizations is not None and len(ax_freq.normalizations) > 0:
            for key, val in ax_freq.normalizations.items():
                norm_freq[key] = val.copy()
        Freqs = Data1D(
            name="freqs", unit="Hz", values=freqs_dqh, normalizations=norm_freq
        )

        # Create DQH axis
        axis_dq = Data1D(
            name="phase",
            unit="",
            values=["direct", "quadrature", "homopolar"],
            is_components=True,
        )

        # Get normalizations
        normalizations: dict[str, Normalization] = {}
        if self.normalizations is not None and len(self.normalizations) > 0:
            for key, val in self.normalizations.items():
                normalizations[key] = val.copy()

        # Create DataFreq object in dqh frame
        data_dqh = DataFreq(
            name=self.name + " in DQH frame",
            unit=self.unit,
            symbol=self.symbol,
            values=Z_dqh,
            axes=[Freqs, axis_dq],
            normalizations=normalizations,
            is_real=self.is_real,
        )

        return data_dqh

    # Inlined from Methods.SciDataTool.DataFreq.dqh2n
    def dqh2n(
        self,
        n: int,
        current_dir: int,
        felec: float,
        is_n_rms: bool = False,
        phase_dir: int | None = None,
    ) -> DataFreq:
        """dqh to n phase coordinate transformation of DataFreq object

        Parameters
        ----------
        self : DataFreq
            data object containing values over time in dqh frame
        n: int
            number of phases
        current_dir: int
            direction of current waveform: +/-1 (-1 clockwise) to enforce
        felec: float
            fundamental electrical frequency [Hz]
        is_n_rms : boolean
            True to return n currents in rms value, False to return peak values (Pyleecan convention)
        phase_dir: int
            direction of phase distribution: +/-1 (-1 clockwise) to enforce

        Returns
        -------
        data_n : DataFreq
            data object containing values over time and phase axes
        """

        # Get values for one time period converted in electrical angle and for all phases

        result_dqh = self.get_along("freqs", "phase", is_squeeze=False)

        # Convert values to dqh frame
        Z_abc, freqs_abc = dqh2n_fct(
            Z_dqh=result_dqh[self.symbol],
            freqs=result_dqh["freqs"],
            phase_dir=phase_dir,
            current_dir=current_dir,
            felec=felec,
            n=n,
            is_n_rms=is_n_rms,
        )

        # Create frequency axis
        norm_freq: dict[str, Normalization] = {}
        ax_freq = self.axes[0]
        if ax_freq.normalizations is not None and len(ax_freq.normalizations) > 0:
            for key, val in ax_freq.normalizations.items():
                norm_freq[key] = val.copy()
        Freqs = Data1D(
            name="freqs", unit="Hz", values=freqs_abc, normalizations=norm_freq
        )

        # Create DQH axis
        Phase = Data1D(
            name="phase",
            unit="",
            values=np.array(gen_name(n)),
            is_components=True,
        )

        # Get normalizations
        normalizations: dict[str, Normalization] = {}
        if self.normalizations is not None and len(self.normalizations) > 0:
            for key, val in self.normalizations.items():
                normalizations[key] = val.copy()

        # Create DataFreq object in dqh frame
        data_n = DataFreq(
            name=self.name.replace(" in DQH frame", ""),
            unit=self.unit,
            symbol=self.symbol,
            values=Z_abc,
            axes=[Freqs, Phase],
            normalizations=normalizations,
            is_real=self.is_real,
        )

        return data_n
