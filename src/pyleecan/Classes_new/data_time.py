# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataTime.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ..Functions.Load.import_class import import_class as _pyleecan_import_class
from ..Functions.SciDataTool import AxisError
from .data_1d import Data1D
from .data_nd import DataND


@dataclass(eq=False)
class DataTime(DataND):
    """Class for fields defined in time space

    Attributes
    ----------
    """

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

        # Dynamic import to avoid loop
        DataFreq = _pyleecan_import_class("pyleecan.Classes", "DataFreq")
        DataPattern = _pyleecan_import_class("pyleecan.Classes", "DataPattern")

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
            Axes = []
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
    def to_datadual(self, datafreq=None):
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

        # Dynamic import to avoid loop
        DataDual = _pyleecan_import_class("pyleecan.Classes", "DataDual")

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
