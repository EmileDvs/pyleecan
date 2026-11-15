import numpy as np


def comp_angle_opening(self) -> float:
    """Compute the average opening angle of the Slot

    Parameters
    ----------
    self : SlotM18_2
        A SlotM18_2 object

    Returns
    -------
    alpha: float
        Average opening angle of the slot [rad]

    """

    return 2 * np.pi / self.Zs
