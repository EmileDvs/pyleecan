import numpy as np


def comp_angle_active_eq(self) -> float:
    """Compute the equivalent angle of the active part of the slot
    (Ideal polar shape with the same surface and height)

    Parameters
    ----------
    self : Slot
        A Slot object

    Returns
    -------
    alpha: float
        Average angle of the slot [rad]

    """

    Swind = self.comp_surface_active()
    Hwind = self.comp_height_active()
    Rmw = self.comp_radius_mid_active()
    Rext = Rmw + Hwind / 2
    Rint = Rmw - Hwind / 2

    return Swind * 2 * np.pi / (np.pi * Rext**2 - np.pi * Rint**2)
