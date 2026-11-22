from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleUD is correctly defined

    Parameters
    ----------
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)
    """
    if self.surf_list is None:
        self.surf_list = list()
    if self.magnet_dict is None:
        self.magnet_dict = dict()
    if len(self.surf_list) == 0:
        raise SlotCheckError("HoleUD must have at least one surface")
    for key in self.magnet_dict:
        if key[:7] != "magnet_":
            raise SlotCheckError(
                "HoleUD magnet_dict must use key like 'magnet_X' with X the index of the magnet. Found: "
                + key
            )
