# -*- coding: utf-8 -*-

import numpy as np


def comp_surface_active(self):
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """

    Rbo = self.get_Rbo()
    point_dict = self._comp_point_coordinate()

    if self.is_outwards():
        Rint = Rbo
        Rext = abs(point_dict["Z2"])
    else:
        Rint = abs(point_dict["Z2"])
        Rext = Rbo

    # Surface of a slot pitch
    Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

    # Tooth surface
    St = self.H2 * self.W3

    alpha_bore = 2 * np.arcsin(self.W3 / (2 * Rint))
    Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

    alpha_yoke = 2 * np.arcsin(self.W3 / (2 * Rext))
    Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

    if self.is_outwards():
        return Sring - (St + Sarc_yoke - Sarc_bore)
    else:
        return Sring - (St + Sarc_yoke - Sarc_bore)
