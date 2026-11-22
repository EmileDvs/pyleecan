import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding

    Parameters
    ----------
    self : SlotW63
        A SlotW63 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """
    Rbo = self.get_Rbo()
    surface = self.comp_surface(lam=lam)

    point_dict = self._comp_point_coordinate()
    Zw1 = point_dict["Zw1"]
    Zw2 = point_dict["Zw2"]
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z7 = point_dict["Z7"]
    Z8 = point_dict["Z8"]

    s_bottom = abs(Zw1 - Zw2) * self.W2

    # top cercle
    D81 = abs(Z8 - Z1)
    alpha = 2 * np.arcsin(D81 / (2 * Rbo))
    Sarc_top = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

    D72 = abs(Z7 - Z2)

    Striangle = (Z8.real - Z7.real) * (Z8.imag - Z7.imag)

    Srect = D72 * (Z8.real - Z7.real)

    return surface - s_bottom - Sarc_top - Striangle - Srect
