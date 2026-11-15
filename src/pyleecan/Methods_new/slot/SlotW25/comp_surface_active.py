import numpy as np


def comp_surface_active(self) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW25
        A SlotW25 object

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """

    point_dict = self._comp_point_coordinate()
    Z2 = point_dict["Z2"]
    Z4 = point_dict["Z4"]

    if self.is_outwards():
        Rint = abs(Z2)
        Rext = abs(Z4)
    else:
        Rint = abs(Z4)
        Rext = abs(Z2)

    # Surface of a slot pitch
    Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

    # Tooth surface
    St = self.H2 * self.W3

    alpha_bore = 2 * np.arcsin(self.W3 / (2 * Rint))
    Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

    alpha_yoke = 2 * np.arcsin(self.W3 / (2 * Rext))
    Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

    return Sring - (St + Sarc_yoke - Sarc_bore)
