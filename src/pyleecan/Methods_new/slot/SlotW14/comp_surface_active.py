from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def comp_surface_active(self, lam: Lamination | Notch | None = None) -> float:
    """Compute the Slot inner surface for winding (by analytical computation)

    Parameters
    ----------
    self : SlotW14
        A SlotW14 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Swind: float
        Slot inner surface for winding [m**2]

    """

    point_dict = self._comp_point_coordinate()
    Z4 = point_dict["Z4"]
    Z5 = point_dict["Z5"]
    Z6 = point_dict["Z6"]
    Z7 = point_dict["Z7"]

    # Compute area of triangle Z5,Z6
    S1 = abs(Z6.imag) * abs(Z5.real - Z4.real) / 2
    S2 = (abs(Z6.imag) + abs(Z7.imag)) * abs(Z7.real - Z6.real) / 2

    if self.is_outwards(lam=lam):
        return (S1 + S2) * 2
    else:
        return (S2 - S1) * 2
