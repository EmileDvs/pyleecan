# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataTime.csv
"""Generated experimental dataclass; do not edit by hand."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ...classes_common.errors import AxisError
from ...Functions_new.SciDataTool.dqh_transformation import (
    get_phase_dir_DataTime,
    n2dqh,
)
from .data import Data
from .data_1d import Data1D
from .data_nd import DataND
from .normalization import Normalization

if TYPE_CHECKING:
    from .data import Data
    from .data_freq import DataFreq
    from .normalization import Normalization


@dataclass(eq=False)
class DataTime(DataND):
    """Class for fields defined in time space

    Attributes
    ----------
    """

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.DataTime.time_to_freq
    def time_to_freq(self):
        """Performs the Fourier Transform and stores the resulting field in a DataFreq object.
        Parameters
        ----------
        self : DataTime
            a DataTime object
        Returns
        -------
        a DataFreq object
        """

        from .data_freq import DataFreq
        from .data_pattern import DataPattern

        axes_str = []
        for i, axis in enumerate(self.axes):
            if axis.is_components:
                axis_str = axis.name + str(list(range(len(axis.values))))
            elif axis.name == "time":
                axis_str = "freqs"
            elif axis.name == "angle":
                axis_str = "wavenumber"
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
                if axis.name == "time":
                    if "antiperiod" in axis.symmetries:
                        symmetries = {"period": int(axis.symmetries["antiperiod"] / 2)}
                    else:
                        symmetries = axis.symmetries.copy()
                    axis_new = Data1D(
                        name="freqs",
                        is_components=False,
                        values=results["freqs"],
                        unit="Hz",
                        symmetries=symmetries,
                        normalizations=axis.normalizations.copy(),
                    ).to_linspace()
                elif axis.name == "angle":
                    if "antiperiod" in axis.symmetries:
                        symmetries = {"period": int(axis.symmetries["antiperiod"] / 2)}
                    else:
                        symmetries = axis.symmetries.copy()
                    axis_new = Data1D(
                        name="wavenumber",
                        is_components=False,
                        values=results["wavenumber"],
                        unit="dimless",
                        symmetries=symmetries,
                        normalizations=axis.normalizations.copy(),
                    ).to_linspace()
                else:
                    axis_new = axis.copy()
                Axes.append(axis_new)
            return DataFreq(
                name=self.name,
                unit=self.unit,
                symbol=self.symbol,
                axes=Axes,
                values=values,
                is_real=self.is_real,
                normalizations=self.normalizations.copy(),
            )

    # Inlined from Methods.SciDataTool.DataTime.to_datadual
    def to_datadual(self, datafreq: DataFreq | None = None):
        """Creates a DataDual object.
        Parameters
        ----------
        self : DataTime
            a DataTime object
        datafreq : DataFreq
            a DataFreq object
        Returns
        -------
        a DataDual object
        """

        from .data_dual import DataDual

        # Fill DataDual object with time/space data
        datadual = DataDual(
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            normalizations=self.normalizations.copy(),
            axes_dt=self.axes,
            values_dt=self.values,
        )

        # Add fourier data (from input or using fft)
        if datafreq is None:
            datafreq = self.time_to_freq()
        datadual.axes_df = datafreq.axes
        datadual.values_df = datafreq.values

        return datadual

    # Inlined from Methods.SciDataTool.DataTime.n2dqh
    def n2dqh(self, is_dqh_rms: bool = True, phase_dir: int | None = None) -> DataTime:
        """n phases to dqh equivalent coordinate transformation of DataTime object

        Parameters
        ----------
        self : DataTime
            data object containing values over time and phase axes
        is_dqh_rms : boolean
            True to return dq currents in rms value (Pyleecan convention), False to return peak values
        phase_dir: int
            direction of phase distribution: +/-1 (-1 clockwise) to enforce

        Returns
        -------
        data_dqh : DataTime
            data object transformed in dqh frame

        """

        if phase_dir is None:
            # Check if input data object is compliant with dqh transformation
            # and get phase_dir from data object
            phase_dir = get_phase_dir_DataTime(self)

        if "angle_elec" not in self.axes[0].normalizations:
            raise Exception("Time axis should contain angle_elec normalization")

        # Get values for one time period converted in electrical angle and for all phases
        angle_elec = self.axes[0].get_values(
            normalization="angle_elec", is_oneperiod=True
        )
        data_n_val = self.get_along("time[oneperiod]", "phase", is_squeeze=False)[
            self.symbol
        ]

        # Convert values to dqh frame
        data_dqh_val = n2dqh(data_n_val, angle_elec, is_dqh_rms, phase_dir)

        # Get time axis on one period
        per_t, is_aper_t = self.axes[0].get_periodicity()
        per_t = int(per_t / 2) if is_aper_t else per_t
        Time = self.axes[0].get_axis_periodic(per_t, is_aper=False)

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

        # Create DataTime object in dqh frame
        data_dqh = DataTime(
            name=self.name + " in DQH frame",
            unit=self.unit,
            symbol=self.symbol,
            values=data_dqh_val,
            axes=[Time, axis_dq],
            normalizations=normalizations,
            is_real=self.is_real,
        )

        return data_dqh
