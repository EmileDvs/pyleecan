from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_connection_mat(self, Zs: int | None = None, p: int | None = None) -> np.ndarray:
    """Get the Winding Matrix

    Parameters
    ----------
    self : Winding
        A: Winding object
    Zs : int
        Number of Slot (Integer >0)
    p : int
        Number of pole pairs (Integer >0)

    Returns
    -------
    wind_mat: numpy.ndarray
        Winding Matrix (1, 1, Zs, qs)


    """

    if self.wind_mat is None:
        self.wind_mat = self.comp_connection_mat(Zs=Zs, p=p)
    elif Zs is not None and self.wind_mat.shape[2] != Zs:
        # Winding matrix is outdated
        self.clean()
        self.wind_mat = self.comp_connection_mat(Zs=Zs, p=p)

    wind_mat = self.wind_mat.copy()
    # Apply the transformations
    if self.is_reverse_wind:
        wind_mat = self.reverse_wind_mat(wind_mat)
    if self.Nslot_shift_wind not in [0, None]:
        wind_mat = self.shift_wind_mat(wind_mat, self.Nslot_shift_wind)
    if self.is_reverse_layer:
        wind_mat = self.reverse_layer(wind_mat)
    if self.is_change_layer:
        wind_mat = self.change_layer(wind_mat)
    if self.is_permute_B_C:
        wind_mat = self.permute_B_C(wind_mat)
    return wind_mat
