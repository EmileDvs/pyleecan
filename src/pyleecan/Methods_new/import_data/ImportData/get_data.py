from ....Classes_new.scidatatool.data_1d import Data1D
from ....Classes_new.scidatatool.data_freq import DataFreq
from ....Classes_new.scidatatool.data_time import DataTime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.scidatatool.data_nd import DataND


def get_data(self) -> DataND:
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

    axes_list: list[Data] = []
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
