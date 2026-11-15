import numpy as np


def comp_surface(self) -> float:
    """Compute the complete surface of the Hole

    Parameters
    ----------
    self : HoleM54
        A HoleM54 object

    Returns
    -------
    S: float
        Surface of the Hole [m**2]

    """

    Sint = np.pi * self.R1**2
    Sext = np.pi * (self.R1 + self.H1) ** 2
    Sarc = (Sext - Sint) * (self.W0 / (2 * np.pi))

    return Sarc + np.pi * (self.H1 / 2) ** 2
