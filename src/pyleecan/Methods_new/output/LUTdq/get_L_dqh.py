from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_L_dqh(self, Id: float, Iq: float, L_endwinding: float = 0, Phi_dqh: np.ndarray | None = None) -> np.ndarray | None:
    """Get the total dqh inductance
    TODO: calculate end-winding inductance from machine

    Parameters
    ----------
    self : LUTdq
        a LUTdq object
    Id : float
        current Id
    Iq : float
        current Iq
    L_endwinding : float
        end winding inductance provided by user
    Phi_dqh: ndarray
        Stator winding dqh flux

    Returns
    ----------
    Ldqh : ndarray
        ddqh inductance
    """

    Lmdqh = self.get_Lm_dqh(Id=Id, Iq=Iq, Phi_dqh=Phi_dqh)

    if Lmdqh is None:
        return None
    else:
        return Lmdqh + L_endwinding
