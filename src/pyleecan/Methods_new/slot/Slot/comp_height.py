import numpy as np


def comp_height(self, Ndisc: int = 200) -> float:
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : Slot
        A Slot object
    Ndisc : int
        Number of point to discretize the lines

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """

    Rbo = self.get_Rbo()

    surf = self.get_surface()

    point_list = surf.discretize(Ndisc)
    point_list = np.array(point_list)
    if self.is_outwards():
        return max(abs(point_list)) - Rbo
    else:
        return Rbo - min(abs(point_list))
