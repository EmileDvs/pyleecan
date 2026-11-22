from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from ....Classes_new.machine.lamination import Lamination


def get_phase_id(self, Nrad: int, Ntan: int, Zs: int, wind_mat: np.ndarray | None = None, lam: Lamination | None = None) -> int:
    """Return the id of the corresponding phase for the zone (Nrad,Ntan,Zs)

    Parameters
    ----------
    self : Winding
        A Winding object
    wind_mat : numpy.ndarray
        A matrix [Nrad,Ntan,Zs,qs] representing the winding
        (default: self.get_connection_mat())
    Nrad : int
        Zone radial coordinate
    Ntan : int
        Zone tagential coordinate
    Zs : int
        Zone slot number coordinate
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    Returns
    -------
    q_id: int
        Id of the phase
    """
    if wind_mat is None:
        wind_mat = self.get_connection_mat(lam=lam)
    return self._get_phase_id(wind_mat, Nrad, Ntan, Zs)
