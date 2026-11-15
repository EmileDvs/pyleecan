import numpy as np


def comp_surface_active(self):
    """Compute the active surface of the conductor

    Parameters
    ----------
    self : CondType12
        A CondType12 object

    Returns
    -------
    Sact: float
        Surface without insulation [m**2]

    """

    Sact = ((self.Wwire / 2.0) ** 2) * np.pi * self.Nwppc

    return Sact
