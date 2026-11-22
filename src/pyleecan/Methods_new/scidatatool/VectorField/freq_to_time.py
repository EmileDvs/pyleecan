from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_nd import DataND


def freq_to_time(self):
    """Performs the Fourier Transform and stores the resulting field in a VectorField of DataTime objects.
    Parameters
    ----------
    self : VectorField
        a VectorField object
    Returns
    -------
    a VectorField object
    """


    comp_dict: dict[str, DataND] = dict()
    for key, comp in self.components.items():
        comp_dict[key] = comp.freq_to_time()

    return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)
