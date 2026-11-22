from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_height(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the height of the Slot.
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW63
        A SlotW63 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Htot: float
        Height of the slot [m]

    """

    Rbo = self.get_Rbo(lam=lam)
    point_dict = self._comp_point_coordinate(lam=lam)
    Z5 = point_dict["Z5"]
    Z4 = point_dict["Z4"]

    return Rbo - abs((Z5 + Z4) / 2)
