import numpy as np


def set_Ud_Uq(self, Ud: float, Uq: float) -> None:
    """Set the value for Ud and Uq

    Parameters
    ----------
    self : OPdq
        An OPdq object
    Ud : float
        Ud value to set [Arms]
    Uq : float
        Uq value to set [Arms]
    """

    if Ud == 0 and Uq == 0:
        self.U0_ref = 0
        self.UPhi0_ref = 0
    else:
        Z = Ud + 1j * Uq
        self.U0_ref = abs(Z)
        self.UPhi0_ref = np.angle(Z)
