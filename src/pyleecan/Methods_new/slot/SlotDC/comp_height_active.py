import numpy as np


def comp_height_active(self) -> float:
    """Compute the height of the winding area

    Parameters
    ----------
    self : SlotDC
        A SlotDC object

    Returns
    -------
    Hwind: float
        Height of the winding area [m]

    """

    return self.R3 + self.H3 + self.H2 + np.sqrt((self.D1 / 2) ** 2 - (self.W1 / 2) ** 2)
