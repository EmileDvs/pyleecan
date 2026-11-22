import numpy as np


def to_linspace(self):
    """Tests if values are a linspace and returns a DataLinspace (or Data1D if not possible)
    Parameters
    ----------
    self: Data1D
        a Data1D object
    Returns
    -------
    DataLinspace or Data1D
    """

    # Local import: avoids circular imports
    from ....Classes_new.scidatatool.data_linspace import DataLinspace


    values = self.values
    number = values.size

    if (
        number > 1
        and values.dtype.kind not in {"U", "S"}
        and np.allclose(
            values,
            np.linspace(values[0], values[-1], number, endpoint=True),
            rtol=1e-5,
            atol=1e-8,
            equal_nan=False,
        )
    ):
        New_axis = DataLinspace(
            initial=values[0],
            final=values[-1],
            number=number,
            include_endpoint=True,
            name=self.name,
            unit=self.unit,
            symmetries=self.symmetries,
            normalizations=self.normalizations.copy(),
            is_components=self.is_components,
            symbol=self.symbol,
        )
    else:
        New_axis = self.copy()

    return New_axis
