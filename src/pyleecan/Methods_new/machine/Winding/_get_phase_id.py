from ....definitions import config_dict
from ....Functions_new.labels import decode_label
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]




@staticmethod
def _get_phase_id(wind_mat: np.ndarray, Nrad: int, Ntan: int, Zs: int) -> int | None:
    """Return the id of the corresponding phase for the zone (Nrad,Ntan,Zs)

    Parameters
    ----------
    wind_mat : numpy.ndarray
        A matrix [Nrad,Ntan,Zs,qs] representing the winding
    Nrad : int
        Zone radial coordinate
    Ntan : int
        Zone tagential coordinate
    Zs : int
        Zone slot number coordinate

    Returns
    -------
    q_id: int
        Id of the phase

    """
    A = wind_mat[Nrad, Ntan, Zs, :]
    for zz in range(len(A)):
        if A[zz] != 0:
            return zz
    return None  # If all the phase are at 0 : the zone is empty
