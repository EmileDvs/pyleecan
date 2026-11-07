# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/DataDual.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .data import Data
from .data_nd import DataND


@dataclass(eq=False)
class DataDual(DataND):
    """Class for fields defined in both time and freq domains

    Attributes
    ----------
    axes_dt : [Data] or None
        List of the Data1D objects corresponding to the axes in time/space domain
        Default: None
    values_dt : ndarray or None
        Values of the field in time/space domain
        Default: None
    axes_df : [Data] or None
        List of the Data1D objects corresponding to the axes in fourier domain
        Default: None
    values_df : ndarray or None
        Values of the field in fourier domain
        Default: None
    """

    axes_dt: list[Data] | None = None
    """List of the Data1D objects corresponding to the axes in time/space domain"""
    values_dt: np.ndarray | None = None
    """Values of the field in time/space domain"""
    axes_df: list[Data] | None = None
    """List of the Data1D objects corresponding to the axes in fourier domain"""
    values_df: np.ndarray | None = None
    """Values of the field in fourier domain"""

    # Inlined from Methods.SciDataTool.DataDual.get_along
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

        # Get best attributes (time/space or fourier)
        if self.is_freq(*args):
            if hasattr(self, "values_df") and self.values_df is not None:
                # Replace axes and values with fourier ones
                self.axes = self.axes_df
                self.values = self.values_df
            else:
                # Replace axes and values with time/space ones
                self.axes = self.axes_dt
                self.values = self.values_dt
        else:
            if hasattr(self, "values_dt") and self.values_dt is not None:
                # Replace axes and values with time/space ones
                self.axes = self.axes_dt
                self.values = self.values_dt
            else:
                # Replace axes and values with fourier ones
                self.axes = self.axes_df
                self.values = self.values_df

        # Call DataND.get_along()
        return super(type(self), self).get_along(
            *args,
            unit=unit,
            is_norm=is_norm,
            axis_data=axis_data,
            is_squeeze=is_squeeze,
            is_magnitude=is_magnitude,
            corr_unit=corr_unit,
        )

    @staticmethod
    def is_freq(*args):
        """Determine if input args require FreqPart"""
        is_freq = False
        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]
        for arg in args:
            if "freqs" in arg or "wavenumber" in arg:
                is_freq = True
                break
        return is_freq

    # Inlined from Methods.SciDataTool.DataDual.get_axes
    def get_axes(self, *args):
        """Returns the list of axes.
        Parameters
        ----------
        self: DataDual
            a DataDual object
        args : list
            list of axes names
        Returns
        -------
        axes_list : list of axes (Data)
        """

        if self.axes is None:
            axes = self.axes_dt + self.axes_df
        else:
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
