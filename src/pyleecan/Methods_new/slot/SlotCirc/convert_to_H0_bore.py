from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def convert_to_H0_bore(self, lam: Lamination | Notch | None = None) -> None:
    """Convert the slot to the other definition of H0

    Parameters
    ----------
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Parameters:
    -----------
    self : SlotCirc
        A SlotCirc objec with is_H0_bore==False
    """

    if self.is_H0_bore:
        raise Exception("Error, slot is already H0 bore type!")

    self.H0 = self.comp_height(lam=lam)
    self.is_H0_bore = True
