from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the winding area

    Parameters
    ----------
    self : SlotW28
        A SlotW28 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Hwind: float
        Height of the winding area [m]

    """

    point_dict = self._comp_point_coordinate()
    Z2 = point_dict["Z2"]
    Z5 = point_dict["Z5"]
    Z7 = point_dict["Z7"]
    if self.is_outwards(lam=lam):
        Ztan2 = Z5 + Z5.imag * (-1 - 1j)
    else:
        Ztan2 = Z5 + Z5.imag * (+1 - 1j)
    Ztan1 = (Z2 + Z7) / 2.0

    return abs(Ztan2 - Ztan1)
