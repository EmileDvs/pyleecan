from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_time import DataTime


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
    from ....Classes_new.scidatatool.data_dual import DataDual


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
