from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotUD2 is correctly defined

    Parameters
    ----------
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)
    """

    if self.line_list is None:
        self.line_list = list()

    if len(self.line_list) == 0:
        raise SlotCheckError("SlotUD2 must have at least one line")

    for ii in range(len(self.line_list) - 1):
        if (
            abs(self.line_list[ii].get_end() - self.line_list[ii + 1].get_begin())
            > 1e-6
        ):
            raise SlotCheckError(
                "SlotUD line " + str(ii) + " and line " + str(ii + 1) + " doesn't match"
            )
