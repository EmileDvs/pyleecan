import numpy as np


def get_modulation_index(self) -> float:
    """Function to compute the carrier

    Parameters
    ----------
    self : ImportGenPWM
        an ImportGenPWM object

    Returns
    -------
    M_I: float
        Modulation index

    """

    if self.U0 is None:
        raise Exception("Cannot calculate modulation index if self.U0 is None")

    if self.Vdc1 is None:
        raise Exception("Cannot calculate modulation index if self.Vdc1 is None")

    return 2 * np.sqrt(2) * self.U0 / self.Vdc1
