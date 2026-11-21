# Experimental pydantic model generated from Generator/ClassesRef/SciDataTool/DataDual.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

from .._pyleecan_model import NDArray
from .data import Data
from .data_nd import DataND
from .data_time import DataTime

if TYPE_CHECKING:
    from .data_time import DataTime


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
    values_dt: NDArray | None = None
    """Values of the field in time/space domain"""
    axes_df: list[Data] | None = None
    """List of the Data1D objects corresponding to the axes in fourier domain"""
    values_df: NDArray | None = None
    """Values of the field in fourier domain"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.DataDual.get_along
    def get_along(
        self,
        *args,
        unit: str = "SI",
        is_norm: bool = False,
        axis_data: list = [],
        is_squeeze: bool = True,
        is_magnitude: bool = False,
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

    # Inlined from Methods.SciDataTool.DataDual.n2dqh
    def n2dqh(self, is_dqh_rms: bool = True, phase_dir: int | None = None) -> DataTime:
        """n phases to dqh equivalent coordinate transformation of the time data

        Parameters
        ----------
        self : DataDual
            A DataDual object
        is_dqh_rms : bool
            True to return dq currents in rms value (Pyleecan convention), False to return peak values
        phase_dir : int
            direction of phase distribution: +/-1 (-1 clockwise) to enforce

        Returns
        -------
        data_dqh : DataTime
            data object transformed in dqh frame
        """

        data_time = DataTime(
            name=self.name,
            unit=self.unit,
            symbol=self.symbol,
            axes=self.axes_dt,
            values=self.values_dt,
            normalizations=self.normalizations,
            is_real=self.is_real,
        )
        return data_time.n2dqh(is_dqh_rms=is_dqh_rms, phase_dir=phase_dir)

    # Inlined from Methods.SciDataTool.DataDual.dqh2n
    def dqh2n(
        self, n: int, is_n_rms: bool = False, phase_dir: int | None = None
    ) -> DataTime:
        """dqh to n phase coordinate transformation of the time data

        Parameters
        ----------
        self : DataDual
            A DataDual object
        n : int
            number of phases
        is_n_rms : bool
            True to return n currents in rms value, False to return peak values (Pyleecan convention)
        phase_dir : int
            direction of phase distribution: +/-1 (-1 clockwise) to enforce

        Returns
        -------
        data_n : DataTime
            data object containing values over time in n phase frame
        """

        data_time = DataTime(
            name=self.name,
            unit=self.unit,
            symbol=self.symbol,
            axes=self.axes_dt,
            values=self.values_dt,
            normalizations=self.normalizations,
            is_real=self.is_real,
        )
        return data_time.dqh2n(n=n, is_n_rms=is_n_rms, phase_dir=phase_dir)
