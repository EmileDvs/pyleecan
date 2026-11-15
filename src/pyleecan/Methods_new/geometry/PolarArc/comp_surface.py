import numpy as np


def comp_surface(self) -> float:
    """Compute the PolarArc surface

    Parameters
    ----------
    self : PolarArc
        A PolarArc object

    Returns
    -------
    surf: float
        The PolarArc surface [m**2]

    """

    Rint = abs(self.point_ref) - self.height / 2
    Rext = Rint + self.height

    return (np.pi * Rext**2 - np.pi * Rint**2) * (self.angle / (2 * np.pi))
