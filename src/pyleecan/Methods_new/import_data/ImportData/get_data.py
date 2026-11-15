from ....Classes.Data1D import Data1D
from ....Classes.DataFreq import DataFreq
from ....Classes.DataTime import DataTime


def get_data(self):
    """Generate Data objects

    Parameters
    ----------
    self : ImportData
        An ImportData object

    Returns
    -------
    Data: DataND
        The generated Data object

    """

    axes_list = []
    is_freq = False
    for axis in self.axes:
        if axis.name == "freqs" or axis.name == "wavenumber":
            is_freq = True
        axes_list.append(
            Data1D(
                values=axis.field.get_data(),
                name=axis.name,
                unit=axis.unit,
                symmetries=axis.symmetries,
                normalizations=axis.normalizations,
            )
        )

    if is_freq:
        Data = DataFreq(
            axes=axes_list,
            values=self.field.get_data(),
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            normalizations=self.normalizations,
        )
    else:
        Data = DataTime(
            axes=axes_list,
            values=self.field.get_data(),
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            normalizations=self.normalizations,
        )

    return Data
