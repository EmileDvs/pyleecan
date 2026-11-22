import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_point_coordinate(self, lam: Lamination | Notch | None = None) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : SlotM18_2
        A SlotM18_2 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """

    Rbo = self.get_Rbo(lam=lam)

    sp = 2 * np.pi / self.Zs
    Z1 = Rbo * np.exp(-1j * sp / 2)
    ZM1 = Rbo * np.exp(-1j * sp / 2)

    if self.is_outwards(lam=lam):
        ZM2 = (Rbo - self.H0_bore) * np.exp(-1j * sp / 2)
        ZM3 = (Rbo - self.H0_bore - self.H0_gap) * np.exp(-1j * sp / 2)
    else:  # inward slot
        ZM2 = (Rbo + self.H0_bore) * np.exp(-1j * sp / 2)
        ZM3 = (Rbo + self.H0_bore + self.H0_gap) * np.exp(-1j * sp / 2)

    point_dict = dict()
    point_dict["Z1"] = Z1
    point_dict["ZM1"] = ZM1
    point_dict["ZM2"] = ZM2
    point_dict["ZM3"] = ZM3
    # symetry
    point_dict["Z2"] = Z1.conjugate()
    point_dict["ZM4"] = ZM3.conjugate()
    point_dict["ZM5"] = ZM2.conjugate()
    point_dict["ZM6"] = ZM1.conjugate()

    return point_dict
